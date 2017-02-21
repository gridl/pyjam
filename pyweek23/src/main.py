from __future__ import division
import pygame, os, datetime
from pygame.locals import *
from . import settings, view, ptext, background, state
from . import scene, playscene, losescene
from .util import F

pygame.init()
view.init()
background.init()

scene.push(playscene)

clock = pygame.time.Clock()
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

	top.think(dt, kdowns, kpressed)
	top.draw()
	if settings.DEBUG:
		text = "\n".join([
			"F2: toggle DEBUG mode",
			"%.1ffps" % clock.get_fps(),
		])
		ptext.draw(text, bottomleft = F(5, 475), fontsize = F(18), color = "white", owidth = 1)
	pygame.display.flip()

	if settings.isdown("quit", kdowns):
		scene.quit()
	if settings.isdown("fullscreen", kdowns):
		settings.fullscreen = not settings.fullscreen
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



