from __future__ import division
import math, pygame
from . import ptext, view, scene, state, progress, img, mechanics
from .util import F

class Cutscene(object):
	lifetime = 1
	message = "cutscene"
	color = "yellow"
	gcolor = "orange"
	fadestart = 0
	fadeend = 0
	tfade = 0.5
	darkin = False
	darkout = False
	darkcolor = 0, 0, 0
	tomenu = False
	
	def init(self):
		self.t = 0
		self.tview = 0
		self.fade = self.fadestart
		self.fading = True

	def think(self, dt, *args):
		self.t += dt
		if self.fading:
			self.fade = math.clamp(self.fade + dt / self.tfade, 0, 1)
			self.tview += dt
			if self.tview >= self.lifetime:
				self.fading = False
		else:
			self.fade = math.clamp(self.fade - dt / self.tfade, 0, 1)
		if self.fade <= self.fadeend and not self.fading:
			if self.tomenu:
				from . import menuscene
				scene.pop()
				scene.pop()
				scene.push(menuscene)
			else:
				scene.pop()

	def draw(self):
		from . import playscene
		playscene.draw()

		if self.fade < 1:
			dark = self.darkin if self.fading else self.darkout
			text = self.message if dark else None
			overlay = 1 if dark else self.fade
		else:
			dark = False
			text = self.message
			overlay = 1

		if overlay is not None:
			view.drawoverlay(0.6 * overlay)
		if text:
			ptext.draw(text, fontsize = F(150), center = F(854/2, 480/2),
				color = self.color, gcolor = self.gcolor, shadow = (1, 1))
		if dark:
			view.drawoverlay(1 - self.fade, self.darkcolor)

	def abort(self):
		state.save()

class Start(Cutscene):
	message = "Level start"
	darkin = True
	fadestart = 1

class Win(Cutscene):
	message = "Level complete"
	darkout = True
	tomenu = True

class Lose(Cutscene):
	message = "Level failed"
	darkout = True
	tomenu = True

class Combos(object):
	color = "yellow"
	gcolor = "orange"
	fadestart = 0
	fadeend = 0
	tfade = 0.3
	darkin = False
	darkout = False
	darkcolor = 0, 0, 0
	tomenu = False
	
	def init(self):
		self.t = 0
		self.tview = 0
		self.fade = self.fadestart
		self.fading = True

	def think(self, dt, mpos, mdown, *args):
		self.t += dt
		if self.fading:
			self.fade = math.clamp(self.fade + dt / self.tfade, 0, 1)
		else:
			self.fade = math.clamp(self.fade - dt / self.tfade, 0, 1)
		if self.fade <= self.fadeend and not self.fading:
			scene.pop()
		if mdown:
			self.fading = False

	def draw(self):
		from . import playscene
		playscene.draw()

		view.drawoverlay(0.96 * self.fade)

		if self.fade < 1:
			return		
		for jflavor, flavor in enumerate(sorted(progress.learned)):
			y, x = divmod(jflavor, 3)
			x0 = 80 + x * 260
			y0 = 50 + y * 65
			for j, f in enumerate(reversed(flavor)):
				p = F(x0 - 20 * j, y0)
				pygame.draw.circle(view.screen, (0, 0, 0), p, F(12))
				img.draw("organelle-" + f, p, radius = F(10))
			text = mechanics.towerinfo.get(flavor, flavor)
			ptext.draw(text, midleft = F(x0 + 20, y0), fontsize = F(17),
				color = "yellow", shadow = (1, 1), width = F(180))
		ptext.draw("Organelle slots unlocked: %d" % progress.nslots,
			bottomright = F(840, 465), fontsize = F(22),
			color = "yellow", shadow = (1, 1))

	def abort(self):
		state.save()



