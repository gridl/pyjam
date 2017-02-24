from __future__ import division
import pygame, os, datetime
from pygame.locals import *
from . import settings, view, ptext, background, state
from . import scene, playscene, losescene, climaxscene
from .util import F

pygame.init()
view.init()
background.init()

scene.push(playscene, 1)
#scene.push(climaxscene)

clock = pygame.time.Clock()
dtexcess = 0
while scene.stack:
	dt = min(clock.tick(settings.maxfps) * 0.001, 1 / settings.minfps)
	top = scene.stack[-1]
	kdowns = set()
	for event in pygame.event.get():
		if event.type == QUIT:
			scene.quit()
		if event.type == KEYDOWN:
			kdowns.add(event.key)
	kpressed = pygame.key.get_pressed()
	if settings.DEBUG and kpressed[K_F7]:
		dt *= 20

	dtexcess += dt
	kd = kdowns
	while dtexcess >= 1 / settings.maxfps:
		top.think(1 / settings.maxfps, kd, kpressed)
		dtexcess -= 1 / settings.maxfps
		kd = set()
	top.draw()
	if settings.DEBUG:
		text = "\n".join([
			"F2: toggle DEBUG mode",
			"F10: toggle portrait mode",
			"F11: toggle fullscreen",
			"F12: screenshot",
			"%.1ffps" % clock.get_fps(),
		])
		h = 849 if settings.portrait else 475
		ptext.draw(text, bottomleft = F(5, h), fontsize = F(18), color = "white", owidth = 1)
	pygame.display.flip()

	if settings.isdown("quit", kdowns):
		scene.quit()
	if settings.isdown("fullscreen", kdowns):
		settings.fullscreen = not settings.fullscreen
		view.init()
	if settings.isdown("portrait", kdowns):
		settings.portrait = not settings.portrait
		view.init()
	if settings.isdown("screenshot", kdowns):
		if not os.path.exists(settings.screenshotdir):
			os.makedirs(settings.screenshotdir)
		t = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
		path = os.path.join(settings.screenshotdir, "screenshot-%s.png" % t)
		pygame.image.save(view.screen, path)
	if settings.DEBUG and settings.isdown("quicksave", kdowns):
		state.save(settings.quicksavefile)
	if settings.DEBUG and settings.isdown("quickload", kdowns):
		state.load(settings.quicksavefile)
	if settings.isdown("toggledebug", kdowns):
		settings.DEBUG = not settings.DEBUG

pygame.quit()



