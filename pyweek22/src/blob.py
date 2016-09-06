from __future__ import division
import pygame, math, numpy
from . import settings

hillcache = {}
def hill(R, h):
	key = R, h
	if key in hillcache:
		return hillcache[key]
	N = 2 * R
	img = pygame.Surface((N, N)).convert_alpha()
	x2s = ((numpy.arange(N) + 0.5) * 2.0 / N - 1) ** 2
	m = numpy.sqrt(x2s.reshape((1, N)) + x2s.reshape((N, 1)))
	m = numpy.minimum(m, 1)
	m = numpy.minimum(255 * h * (1 - m * m * (3 - 2 * m)), 255)
	img.fill((255, 255, 255, 255))
	pygame.surfarray.pixels_alpha(img)[:,:] = m
	hillcache[key] = img
	return img

def mote(R, h):
	key = R, h, "mote"
	if key in hillcache:
		return hillcache[key]
	N = 2 * R
	img = pygame.Surface((N, N)).convert()
	x2s = ((numpy.arange(N) + 0.5) * 2.0 / N - 1) ** 2
	m = numpy.sqrt(x2s.reshape((1, N)) + x2s.reshape((N, 1)))
	m = numpy.minimum(m, 1)
	m = numpy.minimum(255 * h * (1 - m * m * (3 - 2 * m)), 255)
	pygame.surfarray.pixels3d(img)[:,:,:] = m.reshape((N, N, 1)) + numpy.random.rand(N, N, 1)
	hillcache[key] = img
	return img

def tocell(surf):
	osurf = surf.copy()
	osurf.fill((0, 0, 0, 0))
	a = pygame.surfarray.pixels_alpha(surf)
	pygame.surfarray.pixels_alpha(osurf)[a > 100] = 255
	arr = pygame.surfarray.pixels3d(osurf)
	arr[a > 150] = 0, 120, 120
	if settings.cellshading:
		aoff = 1 - settings.cellshading * (a[:-1,:-1] - (a[1:,1:].astype(numpy.int16)))
		ax, ay = aoff.shape
		arr[1:,1:] = (arr[1:,1:] * aoff.reshape((ax, ay, 1))).astype(numpy.uint8)
	return osurf

def drawcell(surf, hillspecs):
	if not hillspecs:
		return
	x0 = max(int(min(x - r for x, y, r, h in hillspecs)), 0)
	x1 = min(int(max(x + r for x, y, r, h in hillspecs)), surf.get_width())
	y0 = max(int(min(y - r for x, y, r, h in hillspecs)), 0)
	y1 = min(int(max(y + r for x, y, r, h in hillspecs)), surf.get_height())
	w, h = x1 - x0, y1 - y0
	if w <= 0 or h <= 0:
		return
	osurf = pygame.Surface((w, h)).convert_alpha()
	osurf.fill((0, 0, 0, 0))
	# TODO: treat as numpy arrays for faster summation
	for x, y, r, h in hillspecs:
		r = int(r)
		x = int(x - x0 - r)
		y = int(y - y0 - r)
		hill(r, h)
		osurf.blit(hill(r, h), (x, y), None, pygame.BLEND_RGBA_ADD)
	surf.blit(tocell(osurf), (x0, y0))

if __name__ == "__main__":
	import random
	from . import mhack, ptext
	pygame.init()
	screen = pygame.display.set_mode((1280, 960))
	blobs = [(
		random.uniform(0, math.tau),  # theta0
		random.uniform(0.3, 0.5) * random.choice([-1, 1]),  # dtheta
		random.uniform(0, math.tau),  # phi0
		random.uniform(0.1, 0.2) * random.choice([-1, 1]),  # dphi
		random.randrange(100, 101), # r
		random.uniform(0.2, 0.4), # h
	) for _ in range(30)]
	surf = pygame.Surface((1280, 960)).convert_alpha()
	clock = pygame.time.Clock()
	while not any(event.type == pygame.KEYDOWN for event in pygame.event.get()):
		clock.tick()
		if False:
			surf.fill((0, 0, 0, 0))
			img = hill(200, 2)
			surf.blit(img, img.get_rect(center = (640, 480)))
			for theta0, dtheta, phi0, dphi, r, h in blobs:
				theta = theta0 + dtheta * pygame.time.get_ticks() * 0.001
				phi = phi0 + dphi * pygame.time.get_ticks() * 0.001
				R = 140 + 20 * math.sin(phi)
				x, y = 640 + R * math.cos(theta), 480 + R * math.sin(theta)
				img = hill(r, h)
				surf.blit(img, img.get_rect(centerx = int(x), centery = int(y)))
			screen.blit(tocell(surf), (0, 0))
		elif True:
			screen.fill((0, 40, 40))
			hillspecs = [(640, 480, 200, 2)]
			for theta0, dtheta, phi0, dphi, r, h in blobs:
				theta = theta0 + dtheta * pygame.time.get_ticks() * 0.001
				phi = phi0 + dphi * pygame.time.get_ticks() * 0.001
				R = 140 + 20 * math.sin(phi)
				x, y = 640 + R * math.cos(theta), 480 + R * math.sin(theta)
				hillspecs.append((x, y, r, h))
			drawcell(screen, hillspecs)
		ptext.draw("%.1ffps" % clock.get_fps(), (10, 10), fontsize = 32)
		pygame.display.flip()
	
