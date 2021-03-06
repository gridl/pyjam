from __future__ import division
import pygame, math, random, os.path
from . import view, ptext, state, util, image, settings, sound, pview
from . import scene, visitscene
from .enco import Component
from .pview import T

# Positive x is right
# Positive y is down

# positive rotational motion is clockwise
# angle of 0 is right
# angle of tau/4 is down

def getattribs(obj, kw, *anames):
	for aname in anames:
		if aname in kw:
			setattr(obj, aname, kw[aname])

class WorldBound(Component):
	def setstate(self, **kw):
		getattribs(self, kw, "x", "y")

class Lives(Component):
	def __init__(self):
		self.alive = True
		self.t = 0
	def setstate(self, **kw):
		getattribs(self, kw, "t", "alive")
	def think(self, dt):
		self.t += dt
	def die(self):
		self.alive = False

class Lifetime(Component):
	def __init__(self, lifetime = 1):
		self.lifetime = lifetime
		self.f = 0
	def setstate(self, **kw):
		getattribs(self, kw, "lifetime", "f")
	def think(self, dt):
		self.f = 1 if self.lifetime <= 0 else util.clamp(self.t / self.lifetime, 0, 1)
		if self.f >= 1:
			self.die()

class LinearMotion(Component):
	def __init__(self):
		self.vx = 0
		self.vy = 0
	def setstate(self, **kw):
		getattribs(self, kw, "vx", "vy")
	def think(self, dt):
		self.x += dt * self.vx
		self.y += dt * self.vy

class Accelerates(Component):
	def __init__(self):
		self.ax = 0
		self.ay = 0
	def setstate(self, **kw):
		getattribs(self, kw, "ax", "ay")
	def think(self, dt):
		self.vx += dt * self.ax
		self.vy += dt * self.ay

class CirclesRift(Component):
	def __init__(self):
		self.rrift = 300
		self.thetarift = 0
	def setstate(self, **kw):
		getattribs(self, kw, "rrift", "thetarift")
		self.think(0)
	def think(self, dt):
		self.rrift = 1 + 300 * math.exp(-0.07 * self.t)
		self.x = self.rrift * math.cos(self.thetarift) + 300
		self.y = self.rrift * math.sin(self.thetarift) + 0
		self.thetarift += 100 / self.rrift * dt

class Knockable(Component):
	def __init__(self):
		self.kx = 0
		self.ky = 0
	def setstate(self, **kw):
		getattribs(self, kw, "kx", "ky")
	def knock(self, dkx, dky):
		self.kx = dkx
		self.ky = dky
	def think(self, dt):
		if not self.kx and not self.ky: return
		k = math.sqrt(self.kx ** 2 + self.ky ** 2)
		d = 300 * dt
		if k < d:
			dx, dy = self.kx, self.ky
			self.kx, self.ky = 0, 0
		else:
			dx, dy = util.norm(self.kx, self.ky, d)
			self.kx -= dx
			self.ky -= dy
		self.x += dx
		self.y += dy

class MovesWithArrows(Component):
	def __init__(self, **kw):
		self.vx = 0
		self.vy = 0
	def move(self, dt, dx, dy):
		if dx: self.vx = state.speed * dx
		if dy: self.vy = state.speed * dy
		self.x += state.speed * dx * dt
		self.y += state.speed * dy * dt
	def think(self, dt):
		f = math.exp(-10 * dt)
		self.vx *= f
		self.vy *= f

class SeeksEnemies(Component):
	def __init__(self, v0):
		self.v0 = v0
	def setstate(self, **kw):
		getattribs(self, kw, "v0")
	def think(self, dt):
		target, r = None, 200
		for e in state.enemies + state.bosses:
			if e.hp <= 0:
				continue
			d = math.sqrt((self.x - e.x) ** 2 + (self.y - e.y) ** 2)
			if d < r:
				target, r = e, d
		if target:
			ax, ay = util.norm(target.x - self.x, target.y - self.y, 2000)
		else:
			ax, ay = 2000, 0
		self.vx, self.vy = util.norm(self.vx + dt * ax, self.vy + dt * ay, self.v0)

class SeeksYou(Component):
	def __init__(self, v0 = 200):
		self.v0 = v0
	def setstate(self, **kw):
		getattribs(self, kw, "v0")
	def think(self, dt):
		target = state.you
		ax, ay = util.norm(target.x - self.x, target.y - self.y, 2000)
		self.vx, self.vy = util.norm(self.vx + dt * ax, self.vy + dt * ay, self.v0)

class SeeksFormation(Component):
	def __init__(self, vmax, accel):
		self.vmax = vmax
		self.v = 0
		self.vx = 0
		self.vy = 0
		self.accel = accel
		self.target = None
	def setstate(self, **kw):
		getattribs(self, kw, "vmax", "v", "vx", "vy", "accel", "steps", "target")
		self.steps = list(self.steps)
	def think(self, dt):
		while self.steps and self.steps[0][0] < self.t:
			self.target = self.steps[0][1:3]
			self.steps = self.steps[1:]
		if not self.target:
			return
		self.v = min(self.v + dt * self.accel, self.vmax)
		tx, ty = self.target
		dx, dy = tx - self.x, ty - self.y
		d = math.sqrt(dx * dx + dy * dy)
		if d < 0.01:
			v = 100
		else:
			v = min(self.v, math.sqrt(2 * 2 * self.accel * d) + 1)
		if v * dt >= d:
			self.x, self.y = self.target
			self.target = None
			self.v = 0
			self.vx = 0
			self.vy = 0
		else:
			self.vx = v * dx / d
			self.vy = v * dy / d
			self.x += self.vx * dt
			self.y += self.vy * dt

class Cycloid(Component):
	def setstate(self, **kw):
		getattribs(self, kw, "x0", "y0", "dy0", "vy0", "cr", "dydtheta")
		self.think(0)
	def think(self, dt):
		dy = self.dy0 + self.vy0 * self.t
		yc = self.y0 + dy
		dycdt = self.vy0
		xc = self.x0
		theta = math.tau / 2 + dy / self.dydtheta
		dthetadt = self.vy0 / self.dydtheta
		S, C = math.sin(theta), math.cos(theta)
		self.x = xc + C * self.cr
		self.y = yc + S * self.cr
		self.vx = -S * dthetadt * self.cr
		self.vy = dycdt + C * dthetadt * self.cr


class SeeksHorizontalPosition(Component):
	def __init__(self, vxmax, accel):
		self.vxmax = vxmax
		self.vx = 0
		self.xaccel = accel
		self.xtarget = None
	def setstate(self, **kw):
		getattribs(self, kw, "vxmax", "vx", "xaccel", "xtarget")
	def think(self, dt):
		if self.xtarget is None: return
		self.vx = abs(self.vx)
		self.vx = min(self.vx + dt * self.xaccel, self.vxmax)
		dx = abs(self.xtarget - self.x)
		if dx < 0.01:
			v = 100
		else:
			v = min(self.vx, math.sqrt(2 * 2 * self.xaccel * dx) + 1)
		if v * dt >= dx:
			self.x = self.xtarget
			self.xtarget = None
			self.vx = 0
		else:
			self.vx = v if self.xtarget > self.x else -v
			self.x += self.vx * dt

class SeeksHorizontalSinusoid(Component):
	def __init__(self, vxmax0, xaccel0, xomega, xr):
		self.vxmax0 = vxmax0
		self.vx0 = 0
		self.x0 = None
		self.xaccel0 = xaccel0
		self.xomega = xomega
		self.xr = xr
		self.xtarget0 = None
		self.xtheta = 0
	def setstate(self, **kw):
		getattribs(self, kw, "vxmax0", "vx0", "x0", "xaccel0", "xomega", "xtheta" "xr", "xtarget0", "x", "vx")
	def think(self, dt):
		if self.x0 is None:
			self.x0 = self.x
		if self.xtarget0 is not None:
			self.vx0 = abs(self.vx0)
			self.vx0 = min(self.vx0 + dt * self.xaccel0, self.vxmax0)
			dx = abs(self.xtarget0 - self.x0)
			if dx < 0.01:
				v = 100
			else:
				v = min(self.vx0, math.sqrt(2 * 2 * self.xaccel0 * dx) + 1)
			if v * dt >= dx:
				self.x0 = self.xtarget0
				self.xtarget0 = None
				self.vx0 = 0
			else:
				self.vx0 = v if self.xtarget0 > self.x0 else -v
				self.x0 += self.vx0 * dt
		self.xtheta += self.xomega * dt
		self.x = self.x0 + self.xr * math.sin(self.xtheta)
		self.vx = self.vx0 + self.xr * self.xomega * math.cos(self.xtheta)

class VerticalSinusoid(Component):
	def __init__(self, yomega, yrange, y0 = 0):
		self.yomega = yomega
		self.yrange = yrange
		self.y0 = y0
		self.ytheta = 0
	def setstate(self, **kw):
		getattribs(self, kw, "yomega", "yrange", "y0", "ytheta")
	def think(self, dt):
		self.ytheta += dt * self.yomega
		self.y = self.y0 + self.yrange * math.sin(self.ytheta)
		self.vy = self.yrange * self.ytheta * math.cos(self.ytheta)


class FiresWithSpace(Component):
	def __init__(self):
		self.tshot = 0  # time since last shot
	def setstate(self, **kw):
		getattribs(self, kw, "tshot")
	def think(self, dt):
		self.tshot += dt
	def act(self):
		if self.tshot > state.reloadtime:
			self.shoot()
	def getcharge(self):
		t = self.tshot - state.reloadtime
		if t <= 0 or state.chargetime > 100000: return 0
		if t >= state.chargetime: return state.maxcharge
		return t / state.chargetime * state.maxcharge
	def getdamage(self):
		return state.basedamage + int(self.getcharge())
	def getbulletsize(self):
		return 3 * (state.basedamage + self.getcharge()) ** 0.3
	def shoot(self):
		r = self.r + 15
		x0, y0 = self.x + r, self.y
		bullet = GoodBullet(
			x = self.x + r, y = self.y,
			vx = 500, vy = 0,
			r = self.getbulletsize(),
			damage = self.getdamage()
		)
		state.goodbullets.append(bullet)
		for jvshot in range(state.vshots):
			dx, dy = -6 * (jvshot + 1), 8 * (jvshot + 1)
			state.goodbullets.append(RangeGoodBullet(
				x = x0 + dx, y = y0 + dy, vx = 500, vy = 0, r = 3, damage = 1, lifetime = 0.2))
			state.goodbullets.append(RangeGoodBullet(
				x = x0 + dx, y = y0 - dy, vx = 500, vy = 0, r = 3, damage = 1, lifetime = 0.2))
		sound.playsfx("shot")
		self.tshot = 0
	def draw(self):
		charge = self.getcharge()
		if charge <= 0: return
		pos = view.screenpos((self.x + self.r * 7, self.y))
		r = T(view.Z * self.getbulletsize())
		color = (255, 255, 255) if self.t * 4 % 1 > 0.5 else (200, 200, 255)
		pygame.draw.circle(pview.screen, color, pos, r)

class MissilesWithSpace(Component):
	def __init__(self):
		self.tmissile = 0  # time since last shot
		self.jmissile = 0
	def setstate(self, **kw):
		getattribs(self, kw, "tmissile", "jmissile")
	def think(self, dt):
		self.tmissile += dt
	def act(self):
		if self.tmissile > state.missiletime:
			self.shootmissile()
	def shootmissile(self):
		dx, dy = util.norm(*[[0, -3], [0, 3]][self.jmissile])
		r = self.r + 5
		missile = GoodMissile(
			x = self.x + r * dx, y = self.y + r * dy,
			vx = 1000 * dx, vy = 1000 * dy
		)
		state.goodbullets.append(missile)
		self.jmissile += 1
		self.jmissile %= 2
		self.tmissile = 0

class CShotsWithSpace(Component):
	def __init__(self):
		self.tcshot = 0  # time since last shot
	def setstate(self, **kw):
		getattribs(self, kw, "tcshot")
	def think(self, dt):
		self.tcshot += dt
	def act(self):
		if self.tcshot > state.cshottime:
			self.cshot()
	def cshot(self):
		r = self.r + 5
		for jshot in range(2, 11):
			theta = jshot / 12 * math.tau
			dx, dy = math.cos(theta), math.sin(theta)
			bullet = GoodBullet(
				x = self.x + r * dx, y = self.y + r * dy,
				vx = 500 * dx, vy = 500 * dy,
				r = 5,
				damage = 5
			)
			state.goodbullets.append(bullet)
			self.tcshot = 0

class YouBound(Component):
	def __init__(self, omega, R):
		self.omega = omega
		self.R = R
	def think(self, dt):
		theta = self.omega * self.t
		self.x = state.you.x + self.R * math.cos(theta)
		self.y = state.you.y + self.R * math.sin(theta)

class BossBound(Component):
	def __init__(self, diedelay = 0):
		self.diedelay = diedelay
		self.target = None
	def setstate(self, **kw):
		getattribs(self, kw, "target", "diedelay")
	def think(self, dt):
		if not self.alive:
			return
		if self.target and not self.target.alive:
			self.diedelay -= dt
			if self.diedelay <= 0:
				self.die()

class Tumbles(Component):
	def __init__(self, omega):
		self.omega = omega
		self.theta = 0
	def setstate(self, **kw):
		getattribs(self, kw, "theta", "omega")
	def think(self, dt):
		self.theta += self.omega * dt

class EncirclesBoss(Component):
	def __init__(self):
		self.vx = 0
		self.vy = 0
	def setstate(self, **kw):
		getattribs(self, kw, "omega", "R", "theta")
	def think(self, dt):
		if not self.alive or not self.target.alive:
			return
		self.theta += self.omega * dt
		S, C = math.sin(self.theta), math.cos(self.theta)
		self.x = self.target.x + self.R * C
		self.y = self.target.y + self.R * S
		self.vx = -S * self.R * self.omega
		self.vy = C * self.R * self.omega

class SinusoidsAcross(Component):
	def __init__(self, varc = 50, harc = 50, p0arc = 0):
		self.vx = 0
		self.vy = 0
		self.varc = varc
		self.harc = harc
		self.p0arc = p0arc
	def setstate(self, **kw):
		getattribs(self, kw, "x0arc", "y0arc", "dxarc", "dyarc", "varc", "harc", "p0arc")
	def think(self, dt):
		if not self.alive or (self.target and not self.target.alive):
			return
		p = self.p0arc + self.varc * self.t
		dpdt = self.varc
		darc = math.sqrt(self.dxarc ** 2 + self.dyarc ** 2)
		beta = math.tau * p / darc
		dbetadt = math.tau * dpdt / darc
		h = self.harc * math.sin(beta)
		dhdt = self.harc * dbetadt * math.cos(beta)
		C, S = util.norm(self.dxarc, self.dyarc)
		self.x = self.x0arc + p * C - h * S
		self.y = self.y0arc + p * S + h * C
		self.vx = dpdt * C - dhdt * S
		self.vy = dpdt * S + dhdt * C

class SpawnsCompanion(Component):
	def __init__(self):
		self.companion = None
	def think(self, dt):
		if self.companion is None and state.companion:
			self.companion = Companion(x = self.x, y = self.y)
			self.companion.think(dt)
			state.yous.append(self.companion)
		if self.companion and not self.companion.alive:
			self.companion = None
		if self.companion and not state.companion:
			self.companion.alive = False

class SpawnsCapsule(Component):
	def die(self):
		capsule = Capsule(x = self.x, y = self.y, vx = self.vx, vy = self.vy, name = "X")
		state.planets.append(capsule)

class SpawnsCobras(Component):
	def __init__(self, dtcobra = 6):
		self.tcobra = 0
		self.dtcobra = dtcobra
		self.jcobra = 0
	def setstate(self, **kw):
		getattribs(self, kw, "tcobra", "dtcobra", "jcobra")
	def think(self, dt):
		self.tcobra += dt
		while self.tcobra > self.dtcobra:
			self.spawncobra()
			self.tcobra -= self.dtcobra
	def spawncobra(self):
		x0 = 500 + (self.jcobra * math.phi % 1) * 200
		y0 = (self.jcobra * math.phi % 1 * 2 - 1) * state.yrange
		dx = -600
		dy = (self.jcobra * math.phi ** 2 % 1 * 2 - 1) * 100
		h = 80
		p0 = 0
		r = 40
		for jseg in range(12):
			state.enemies.append(Cobra(
				x0arc = x0, y0arc = y0, dxarc = dx, dyarc = dy,
				p0arc = p0, harc = h, r = r, target = self, diedelay = 0.5 + 0.2 * jseg))
			p0 -= r * 0.8
			r *= 0.95
		self.jcobra += 1
	
class SpawnsSwallows(Component):
	def __init__(self, nswallow):
		self.nswallow = nswallow
		self.tfreak = 0
	def setstate(self, **kw):
		getattribs(self, kw, "nswallow")
		self.swallows = []
		for jswallow in range(self.nswallow):
			theta = jswallow * math.tau / self.nswallow
			swallow = Swallow(target = self, omega = 1, R = self.r, theta = theta)
			self.swallows.append(swallow)
			state.enemies.append(swallow)
	def think(self, dt):
		if self.tfreak:
			self.tfreak = max(self.tfreak - dt, 0)
			if self.tfreak == 0:
				self.xomega /= 3
				self.yomega /= 3
				if not self.swallows:
					self.die()
		elif any(not s.alive for s in self.swallows):
			self.tfreak = 1.5
			self.xomega *= 5
			self.yomega *= 5
			self.swallows = [s for s in self.swallows if s.alive]
			for s in self.swallows:
				s.omega *= 1.4

class SpawnsCanaries(Component):
	def __init__(self, ncanary = 6):
		self.ncanary = 6
	def setstate(self, **kw):
		getattribs(self, kw, "ncanary")
		self.canaries = []
		dt0 = 0
		for jcanary in range(self.ncanary):
			theta = jcanary * math.tau / self.ncanary
			omega = 1.5
			for r in (2, 3, 4):
				canary = Canary(target = self, omega = omega, R = r * self.r, theta = theta, tbullet = dt0 * 4)
				self.canaries.append(canary)
				state.enemies.append(canary)
				theta += math.phi * math.tau
				omega /= -1.5
			dt0 = (dt0 + math.phi) % 1
	def think(self, dt):
		if any(not s.alive for s in self.canaries):
			self.yomega *= 1.2
			self.canaries = [s for s in self.canaries if s.alive]
			for s in self.canaries:
				s.omega *= 1.1


	
class SpawnsHerons(Component):
	def __init__(self, dtheron):
		self.dtheron = dtheron
		self.theron = 0
		self.jheron = 0
	def setstate(self, **kw):
		getattribs(self, kw, "theron", "dtheron", "jheron")
	def think(self, dt):
		self.theron += dt
		while self.theron >= self.dtheron:
			heron = Heron(x = 600, y = self.y, vx = -60, vy = 0, target = self)
			state.enemies.append(heron)
			self.jheron += 1
			self.theron -= self.dtheron

class SpawnsClusterBullets(Component):
	def __init__(self, dtcb):
		self.dtcb = dtcb
		self.tcb = 0
		self.jcb = 0
	def setstate(self, **kw):
		getattribs(self, kw, "dtcb", "tcb", "jcb")
	def think(self, dt):
		self.tcb += dt
		while self.tcb >= self.dtcb:
			y = (self.jcb * math.phi % 1 * 2 - 1) * state.yrange
			state.badbullets.append(BadClusterBullet(x = 500, y = y, vx = -100, vy = 0))
			self.tcb -= self.dtcb
			self.jcb += 1

class Collides(Component):
	def __init__(self, r):
		self.r = r
	def setstate(self, **kw):
		getattribs(self, kw, "r")

class ConstrainToScreen(Component):
	def __init__(self, xmargin = 0, ymargin = 0):
		self.xmargin = xmargin
		self.ymargin = ymargin
	def think(self, dt):
		if state.twin:
			return
		dxmax = 427 / view.Z - self.r - self.xmargin
		self.x = util.clamp(self.x, view.x0 - dxmax, view.x0 + dxmax)
		dymax = state.yrange - self.r - self.ymargin
		self.y = util.clamp(self.y, -dymax, dymax)

class DisappearsOffscreen(Component):
	def __init__(self, offscreenmargin = 20):
		self.offscreenmargin = offscreenmargin
	def setstate(self, **kw):
		getattribs(self, kw, "offscreenmargin")
	def think(self, dt):
		x = self.x - view.x0
		xmax = 427 / view.Z + self.r + self.offscreenmargin
		ymax = state.yrange + self.r + self.offscreenmargin
		if x * self.vx > 0 and abs(x) > xmax:
			self.alive = False
		if self.y * self.vy > 0 and abs(self.y) > ymax:
			self.alive = False

class RoundhouseBullets(Component):
	def __init__(self, dtbullet = 0.3):
		self.tbullet = 0
		self.dtbullet = dtbullet
		self.nbullet = 20
		self.vbullet = 50
		self.jbullet = 0
	def think(self, dt):
		self.tbullet += dt
		while self.tbullet >= self.dtbullet:
			for jtheta in range(3):
				theta = (self.jbullet / self.nbullet + jtheta / 3) * math.tau
				dx, dy = math.cos(theta), math.sin(theta)
				r = self.r + 2
				bullet = BadBullet(
					x = self.x + r * dx,
					y = self.y + r * dy,
					vx = self.vbullet * dx,
					vy = self.vbullet * dy
				)
				state.badbullets.append(bullet)
			self.tbullet -= self.dtbullet
			self.jbullet += 1

class ShootsAtYou(Component):
	def __init__(self, dtbullet = 4):
		self.tbullet = 0
		self.dtbullet = dtbullet
		self.nbullet = 20
		self.vbullet = 150
		self.jbullet = 0
	def setstate(self, **kw):
		getattribs(self, kw, "tbullet")
	def think(self, dt):
		self.tbullet += dt
		while self.tbullet >= self.dtbullet:
			dx, dy = util.norm(state.you.x - self.x, state.you.y - self.y)
			r = self.r + 2
			bullet = BadBullet(
				x = self.x + r * dx,
				y = self.y + r * dy,
				vx = self.vbullet * dx,
				vy = self.vbullet * dy
			)
			state.badbullets.append(bullet)
			self.tbullet -= self.dtbullet
			self.jbullet += 1


class ABBullets(Component):
	def __init__(self, nbullet, dtbullet):
		self.tbullet = 0
		self.nbullet = nbullet
		self.dtbullet = dtbullet
		self.vbullet = 50
		self.jbullet = 0
	def think(self, dt):
		self.tbullet += dt
		while self.tbullet >= self.dtbullet:
			for jtheta in range(self.nbullet):
				theta = (jtheta + self.jbullet * 0.5) / self.nbullet * math.tau
				dx, dy = math.cos(theta), math.sin(theta)
				r = self.r + 2
				bullet = BadBullet(
					x = self.x + r * dx,
					y = self.y + r * dy,
					vx = self.vbullet * dx,
					vy = self.vbullet * dy
				)
				state.badbullets.append(bullet)
			self.tbullet -= self.dtbullet
			self.jbullet += 1
			self.jbullet %= 2

class Visitable(Component):
	def __init__(self, help = True):
		self.help = help
	def setstate(self, **kw):
		getattribs(self, kw, "name", "help")
		self.name = str(self.name)
	def visit(self):
		if not self.alive:
			return
		state.met.add(self.name)
		scene.push(visitscene, self.name)
		self.alive = False
	def draw(self):
		if not self.help:
			return
		if self.name in state.met:
			return
		alpha = util.clamp(abs(self.t % 2 - 1) * 7, 0, 1)
		pos = view.screenpos((self.x + self.r, self.y - 2 * self.r))
		ptext.draw("HELP!", center = pos, fontsize = T(20), fontname = "Bungee", alpha = alpha)

class DiesOnCollision(Component):
	def hit(self, target = None):
		self.die()

class HurtsOnCollision(Component):
	def __init__(self, damage = 1):
		self.damage = damage
	def setstate(self, **kw):
		getattribs(self, kw, "damage")
	def hit(self, target = None):
		if target is not None:
			target.hurt(self.damage)

class KnocksOnCollision(Component):
	def __init__(self, dknock = 10):
		self.dknock = dknock
	def setstate(self, **kw):
		getattribs(self, kw, "dknock")
	def hit(self, target = None):
		if target is not None:
			target.knock(*util.norm(target.x - self.x, target.y - self.y, self.dknock))

class ClustersNearYou(Component):
	def __init__(self, nbullet, dyou, vbullet = 50):
		self.nbullet = nbullet
		self.dyou = dyou
		self.vbullet = vbullet
	def setstate(self, **kw):
		getattribs(self, kw, "nbullet", "dyou", "vbullet")
	def think(self, dt):
		if not state.you.alive: return
		if (self.x - state.you.x) ** 2 + (self.y - state.you.y) ** 2 < self.dyou ** 2:
			r = self.r
			for jtheta in range(self.nbullet):
				theta = jtheta / self.nbullet * math.tau
				dx, dy = math.cos(theta), math.sin(theta)
				bullet = BadBullet(
					x = self.x + r * dx,
					y = self.y + r * dy,
					vx = self.vbullet * dx,
					vy = self.vbullet * dy
				)
				state.badbullets.append(bullet)
			self.alive = False
			sound.play("boom")

class HasHealth(Component):
	def __init__(self, hp0, iflashmax = 1):
		self.hp0 = self.hp = hp0
		self.iflashmax = iflashmax
	def setstate(self, **kw):
		getattribs(self, kw, "hp", "hp0", "iflashmax")
	def hurt(self, damage):
		if self.hp <= 0: return
		self.hp -= damage
		self.iflash = self.iflashmax
		if self.hp <= 0:
			sound.playsfx("boss-die" if self in state.bosses else "enemy-die")
			self.die()
		else:
			sound.playsfx("enemy-hurt")

class LeavesCorpse(Component):
	def die(self):
		state.corpses.append(Corpse(x = self.x, y = self.y, r = self.r))

class LetPickup(Component):
	def __init__(self, apickup):
		self.apickup = apickup
	def setstate(self, **kw):
		getattribs(self, kw, "apickup")
	def die(self):
		if self.hp <= 0:
			state.addapickup(self.apickup, self)

class InfiniteHealth(Component):
	def __init__(self):
		self.hp = 0
	def hurt(self, damage):
		pass

class Collectable(Component):
	def think(self, dt):
		dx, dy = state.you.x - self.x, state.you.y - self.y
		d = math.sqrt(dx * dx + dy * dy)
		if d < state.rmagnet:
			dx, dy = util.norm(dx, dy, 300 * dt)
			self.x += dx
			self.y += dy
	def collect(self):
		sound.playsfx("get")
		self.die()

class HealsOnCollect(Component):
	def __init__(self, heal = 1):
		self.heal = heal
	def setstate(self, **kw):
		getattribs(self, kw, "heal")
	def collect(self):
		state.heal(self.heal)

class MissilesOnCollect(Component):
	def __init__(self, nmissile = 40):
		self.nmissile = nmissile
	def setstate(self, **kw):
		getattribs(self, kw, "nmissile")
	def collect(self):
		r = self.r + 5
		for jmissile in range(self.nmissile):
			theta = math.tau * (jmissile + 0.5) * math.phi
			dx, dy = math.cos(theta), math.sin(theta)
			missile = GoodMissile(
				x = self.x + r * dx, y = self.y + r * dy,
				vx = 1000 * dx, vy = 1000 * dy
			)
			t = jmissile / self.nmissile * 0.2
			state.spawners.append(Spawner(egg = missile, collection = state.goodbullets, lifetime = t))

class SlowsOnCollect(Component):
	def __init__(self, tslow = 5):
		self.tslow = tslow
	def setstate(self, **kw):
		getattribs(self, kw, "tslow")
	def collect(self):
		state.tslow = max(state.tslow, self.tslow)

class Spawns(Component):
	def setstate(self, **kw):
		getattribs(self, kw, "egg", "collection")
	def die(self):
		self.collection.append(self.egg)

def getcfilter(iflash):
	if iflash <= 0: return None
	a = iflash ** 0.5 * 12
	return [None, (1, 0.2, 0.2), None, (1, 0.7, 0.2)][int(a) % 4]

class DrawImage(Component):
	def __init__(self, imgname, imgscale = 1, cfilter0 = None):
		self.imgname = imgname
		self.imgscale = imgscale
		self.cfilter0 = cfilter0
		self.iflash = 0
	def setstate(self, **kw):
		getattribs(self, kw, "imgname", "imgscale", "cfilter0", "iflash")
	def think(self, dt):
		self.iflash = max(self.iflash - dt, 0)
	def draw(self):
		scale = 0.01 * self.r * self.imgscale
		cfilter = getcfilter(self.iflash) or self.cfilter0
		image.Gdraw(self.imgname, pos = (self.x, self.y), scale = scale, cfilter = cfilter)
		if settings.DEBUG:
			pos = view.screenpos((self.x, self.y))
			r = T(view.Z * self.r)
			pygame.draw.circle(pview.screen, (255, 0, 0), pos, r, T(1))

class DrawTumblingRock(Component):
	def __init__(self, cfilter0 = None):
		self.cfilter0 = cfilter0
		self.iflash = 0
	def setstate(self, **kw):
		getattribs(self, kw, "cfilter0", "iflash")
		self.rtheta = random.random()
		self.romega = random.choice([-1, 1]) * random.uniform(0.08, 0.25)
	def think(self, dt):
		self.iflash = max(self.iflash - dt, 0)
		self.rtheta += self.romega * dt
	def draw(self):
		scale = 0.01 * self.r * 0.39 * 4
		jframe = int(self.rtheta * 60) % 60 * 1
		if settings.lowres:
			jframe = 0
		cfilter = getcfilter(self.iflash) or self.cfilter0
		imgname = os.path.join("data", "rock", "main-%d.png" % jframe)
		image.Gdraw(imgname, pos = (self.x, self.y), scale = scale, cfilter = cfilter, angle = 50)
		if settings.DEBUG:
			pos = view.screenpos((self.x, self.y))
			r = T(view.Z * self.r)
			pygame.draw.circle(pview.screen, (255, 0, 0), pos, r, T(1))

class DrawFacingImage(Component):
	def __init__(self, imgname, imgscale = 1, ispeed = 0):
		self.imgname = imgname
		self.imgscale = imgscale
		self.ispeed = ispeed
		self.iflash = 0
	def setstate(self, **kw):
		getattribs(self, kw, "imgname", "imgscale", "ispeed", "iflash")
	def think(self, dt):
		self.iflash = max(self.iflash - dt, 0)
	def draw(self):
		scale = 0.01 * self.r * self.imgscale
		y = -self.vy
		x = self.vx + self.ispeed
		angle = 0 if x == 0 and y == 0 else math.degrees(math.atan2(y, x))
		if settings.portrait:
			angle += 90
		image.Gdraw(self.imgname, pos = (self.x, self.y), scale = scale, angle = angle, cfilter = getcfilter(self.iflash))
		if settings.DEBUG:
			pos = view.screenpos((self.x, self.y))
			r = T(view.Z * self.r)
			pygame.draw.circle(pview.screen, (255, 0, 0), pos, r, T(1))

class DrawAngleImage(Component):
	def __init__(self, imgname, imgscale = 1):
		self.imgname = imgname
		self.imgscale = imgscale
		self.iflash = 0
	def setstate(self, **kw):
		getattribs(self, kw, "imgname", "imgscale", "iflash")
	def think(self, dt):
		self.iflash = max(self.iflash - dt, 0)
	def draw(self):
		scale = 0.01 * self.r * self.imgscale
		angle = math.degrees(-self.theta)
		if settings.portrait:
			angle += 90
		image.Gdraw(self.imgname, pos = (self.x, self.y), scale = scale, angle = angle, cfilter = getcfilter(self.iflash))
		if settings.DEBUG:
			pos = view.screenpos((self.x, self.y))
			r = T(view.Z * self.r)
			pygame.draw.circle(pview.screen, (255, 0, 0), pos, r, T(1))

class DrawBox(Component):
	def __init__(self, boxname, boxcolor = (120, 120, 120)):
		self.boxname = boxname
		self.boxcolor = boxcolor
		self.iflash = 0
	def think(self, dt):
		self.iflash = max(self.iflash - dt, 0)
	def draw(self):
		pos = view.screenpos((self.x, self.y))
		r = T(view.Z * self.r)
		color = self.boxcolor
		if hasattr(self, "iflash") and self.iflash >= 0:
			color = [self.boxcolor, (255, 0, 0)][int(self.iflash * 10 % 2)]
		pygame.draw.circle(pview.screen, color, pos, r)
		ptext.draw(self.boxname, center = pos, color = "white", fontsize = T(14))

class DrawCorpse(Component):
	def draw(self):
		color = [(255, 255, 0), (255, 128, 0)][int(self.t * 20 % 2)]
		r = T(self.r * (1 + self.f))
		pos = view.screenpos((self.x, self.y))
		pygame.draw.circle(pview.screen, color, pos, r, T(3))

class FlashesOnInvulnerable(Component):
	def draw(self):
		self.boxcolor = (100, 0, 0) if state.tinvulnerable * 6 % 1 > 0.5 else (100, 100, 100)


class DrawFlash(Component):
	def __init__(self):
		self.dtflash = random.random()
	def draw(self):
		pos = view.screenpos((self.x, self.y))
		r = T(view.Z * self.r)
		color = (255, 120, 120) if (self.t + self.dtflash) * 5 % 1 > 0.5 else (255, 255, 0)
		if settings.lowres:
			rec = pygame.Rect((0, 0, 2*r, 2*r))
			rec.center = pos
			pview.fill(color, rec)
		else:
			pygame.draw.circle(pview.screen, color, pos, r)

class DrawGlow(Component):
	def __init__(self):
		self.dtflash = random.random()
	def draw(self):
		pos = view.screenpos((self.x, self.y))
#		pygame.draw.circle(view.screen, (200, 200, 255), pos, T(view.Z * self.r * 2))
		pygame.draw.circle(pview.screen, (200, 200, 255), pos, T(view.Z * self.r * 1))

@WorldBound()
@Lives()
@MovesWithArrows()
@Knockable()
@FiresWithSpace()
@MissilesWithSpace()
@CShotsWithSpace()
@Collides(5)
@SpawnsCompanion()
@ConstrainToScreen(5, 5)
@FlashesOnInvulnerable()
@DrawFacingImage("you", 5, 1000)
@LeavesCorpse()
class You(object):
	def __init__(self, **kw):
		self.setstate(**kw)
	def hurt(self, damage):
		state.takedamage(damage)

@WorldBound()
@Lives()
@Collides(5)
@CirclesRift()
@Tumbles(1)
@DrawAngleImage("cutter", 5)
class Him(object):
	def __init__(self, **kw):
		self.setstate(**kw)


@WorldBound()
@YouBound(5, 25)
@Lives()
@Collides(4)
@InfiniteHealth()
@Tumbles(4)
@DrawAngleImage("zap", 4)
class Companion(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@Collides(60)
@LinearMotion()
@InfiniteHealth()
@DrawBox("planet")
@Visitable()
class Planet(object):
	def __init__(self, vx = None, vy = None, **kw):
		self.setstate(
			vx = -state.scrollspeed if vx is None else vx,
			vy = 0 if vy is None else vy,
			**kw)

@WorldBound()
@Lives()
@Collides(16)
@LinearMotion()
@InfiniteHealth()
@Tumbles(1)
@DrawAngleImage("capsule", 1.7)
@Visitable()
class Capsule(object):
	def __init__(self, vx = None, vy = None, **kw):
		self.setstate(
			vx = -state.scrollspeed if vx is None else vx,
			vy = 0 if vy is None else vy,
			**kw)

@WorldBound()
@Lives()
@Collides(50)
@LinearMotion()
@SeeksYou(220)
@InfiniteHealth()
@DrawFacingImage("gabriel", 0.6)
@Visitable(False)
class Gabriel(object):
	def __init__(self, vx = None, vy = None, **kw):
		self.setstate(
			vx = -state.scrollspeed if vx is None else vx,
			vy = 0 if vy is None else vy,
			name = 7,
			**kw)

@WorldBound()
@Lives()
@Collides(3)
@LinearMotion()
@DiesOnCollision()
@HurtsOnCollision()
@DisappearsOffscreen()
@DrawFlash()
class BadBullet(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@Collides(6)
@LinearMotion()
@DiesOnCollision()
@HurtsOnCollision(2)
@ClustersNearYou(20, 80)
@DisappearsOffscreen()
@DrawFlash()
class BadClusterBullet(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@Collides(3)
@LinearMotion()
@DiesOnCollision()
@HurtsOnCollision()
@DisappearsOffscreen()
@DrawGlow()
class GoodBullet(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@Lifetime(0.5)
@Collides(3)
@LinearMotion()
@DiesOnCollision()
@HurtsOnCollision()
@DisappearsOffscreen()
@DrawGlow()
class RangeGoodBullet(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@Collides(5)
@SeeksEnemies(300)
@LinearMotion()
@DiesOnCollision()
@HurtsOnCollision()
@DisappearsOffscreen()
@DrawFacingImage("missile", 5)
class GoodMissile(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@HasHealth(40)
@Collides(60)
@RoundhouseBullets(0.5)
@SeeksHorizontalPosition(30, 30)
@VerticalSinusoid(0.4, 100)
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@SpawnsCobras(15)
@SpawnsCanaries()
@SpawnsHerons(8)
@SpawnsClusterBullets(4)
@Tumbles(-0.5)
@DrawAngleImage("hawk", 1.1)
@LeavesCorpse()
class Hawk(object):
	def __init__(self, **kw):
		self.setstate(**kw)


@WorldBound()
@Lives()
@HasHealth(16)
@Collides(60)
@RoundhouseBullets(0.1)
@SeeksHorizontalPosition(30, 30)
@VerticalSinusoid(0.4, 120)
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@SpawnsCobras()
@Tumbles(1)
@DrawAngleImage("medusa", 1.5)
@LeavesCorpse()
class Medusa(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@HasHealth(200)
@Collides(100)
@RoundhouseBullets(1)
@SeeksHorizontalPosition(30, 30)
@VerticalSinusoid(0.4, 120)
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@SpawnsClusterBullets(2)
@Tumbles(0.4)
@DrawAngleImage("heron", 1.5)
@LeavesCorpse()
class Emu(object):
	def __init__(self, **kw):
		self.setstate(**kw)


@WorldBound()
@Lives()
@InfiniteHealth()
@Collides(80)
#@RoundhouseBullets()
@SeeksHorizontalSinusoid(30, 30, 0.8, 100)
@VerticalSinusoid(0.6, 120)
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@SpawnsSwallows(6)
@SpawnsHerons(3)
@SpawnsClusterBullets(2)
@DrawImage("egret", 1.4)
@LeavesCorpse()
class Egret(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@BossBound()
@EncirclesBoss()
@Lives()
@HasHealth(20)
@Collides(30)
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@DrawAngleImage("swallow", 1.3)
@LeavesCorpse()
class Swallow(object):
	def __init__(self, **kw):
		self.setstate(**kw)
		self.think(0)

@WorldBound()
@BossBound()
@EncirclesBoss()
@Lives()
@HasHealth(20)
@Collides(30)
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@DrawFacingImage("canary", 1.7)
@ShootsAtYou()
@LeavesCorpse()
class Canary(object):
	def __init__(self, **kw):
		self.setstate(**kw)
		self.think(0)

@WorldBound()
@BossBound()
@EncirclesBoss()
@Lives()
@HasHealth(20)
@Collides(4)
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@DrawFacingImage("snake", 1.2, 0)
@LeavesCorpse()
class Asp(object):
	def __init__(self, **kw):
		self.setstate(**kw)
		self.think(0)

@WorldBound()
@BossBound()
@SinusoidsAcross()
@Lives()
@DisappearsOffscreen(800)
@InfiniteHealth()
@Collides(4)
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@DrawFacingImage("snake", 1.2, 0)
@LeavesCorpse()
class Cobra(object):
	def __init__(self, **kw):
		self.setstate(**kw)
		self.think(0)

@WorldBound()
@Lives()
@HasHealth(3)
@LetPickup(1)
@Collides(20)
@SeeksFormation(400, 400)
@DisappearsOffscreen()
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@LeavesCorpse()
@DrawFacingImage("duck", 1.8, -100)
class Duck(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@HasHealth(20)
@LetPickup(3)
@Collides(40)
@SeeksFormation(400, 400)
@DisappearsOffscreen()
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@DrawFacingImage("duck", 1.8, -100)
@LeavesCorpse()
class Turkey(object):
	def __init__(self, **kw):
		self.setstate(**kw)


@WorldBound()
@Lives()
@HasHealth(4)
@LetPickup(2)
@Collides(20)
@Cycloid()
@DisappearsOffscreen(1000)
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@DrawFacingImage("canary", 1.7)
@LeavesCorpse()
class Lark(object):
	def __init__(self, **kw):
		self.setstate(**kw)


@WorldBound()
@Lives()
@BossBound()
@HasHealth(10)
@LetPickup(1)
@Collides(20)
@LinearMotion()
@DisappearsOffscreen()
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@ABBullets(12, 3)
@Tumbles(2)
@DrawAngleImage("heron", 1.5)
@LeavesCorpse()
class Heron(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@LinearMotion()
@HasHealth(3, iflashmax = 0.3)
@LetPickup(2)
@Collides(20)
@DisappearsOffscreen()
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@DrawTumblingRock()
@LeavesCorpse()
class Rock(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@LinearMotion()
@HasHealth(40, iflashmax = 0.3)
@Collides(20)
@DisappearsOffscreen()
@HurtsOnCollision(2)
@KnocksOnCollision(40)
@SpawnsCapsule()
@DrawTumblingRock((0.7, 0.7, 1.0))
@LeavesCorpse()
class BlueRock(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@WorldBound()
@Lives()
@Collides(5)
@LinearMotion()
@Accelerates()
@Tumbles(5)
@DrawAngleImage("health", 5)
@Collectable()
@HealsOnCollect()
class HealthPickup(object):
	def __init__(self, vx = None, vy = None, **kw):
		self.setstate(
			vx = -state.scrollspeed if vx is None else vx,
			vy = 0 if vy is None else vy,
			**kw)

@WorldBound()
@Lives()
@Collides(5)
@LinearMotion()
@Accelerates()
@Tumbles(5)
@DrawAngleImage("mpickup", 5)
@Collectable()
@MissilesOnCollect()
class MissilesPickup(object):
	def __init__(self, vx = None, vy = None, **kw):
		self.setstate(
			vx = -state.scrollspeed if vx is None else vx,
			vy = 0 if vy is None else vy,
			**kw)

@WorldBound()
@Lives()
@Collides(5)
@LinearMotion()
@DrawBox("slow")
@Collectable()
@SlowsOnCollect()
class SlowPickup(object):
	def __init__(self, vx = None, vy = None, **kw):
		self.setstate(
			vx = -state.scrollspeed if vx is None else vx,
			vy = 0 if vy is None else vy,
			**kw)

@WorldBound()
@Lives()
@Lifetime(0.2)
@Collides(0)
@DrawCorpse()
class Corpse(object):
	def __init__(self, **kw):
		self.setstate(**kw)

@Lives()
@Lifetime()
@Spawns()
class Spawner(object):
	def __init__(self, **kw):
		self.setstate(**kw)
	def draw(self):
		pass


