from __future__ import division
# import vidcap
import pygame, datetime, os.path
from pygame.locals import *
from src import settings, thing, window, ptext, state, background, scene
from src.window import F
from src.scenes import play, intro, title

window.init()
pygame.display.set_caption(settings.gamename)
pygame.mixer.init()
background.init()

if os.path.exists(settings.savename):
	scene.current = play
	lastscene = play
	state.load()
else:
	scene.current = intro
	lastscene = None

clock = pygame.time.Clock()
playing = True
tconfirmfull = 0
while playing:
	dt = clock.tick(settings.maxfps) * 0.001
	events = list(pygame.event.get())
	for event in events:
		if event.type == QUIT:
			playing = False
		if event.type == KEYDOWN and event.key == K_ESCAPE:
			playing = False
		if event.type == KEYDOWN and event.key == K_F11:
			settings.fullscreen = not settings.fullscreen
			if settings.fullscreen:
				tconfirmfull = 10
			window.init()
		if event.type == KEYUP and event.key == K_SPACE:
			tconfirmfull = 0
		if event.type == KEYDOWN and event.key == K_F12:
			fname = datetime.datetime.now().strftime("screenshot-%Y%m%d%H%M%S.png")
			pygame.image.save(window.screen, os.path.join("screenshots", fname))
		if settings.DEBUG and event.type == KEYDOWN and event.key == K_F2:
			print("ships %d" % len(state.ships))
			print("objs %d" % len(state.objs))
			print("hazards %d" % len(state.hazards))
			print("effects %d" % len(state.effects))
		if settings.DEBUG and event.type == KEYDOWN and event.key == K_F3:
			settings.drawbackground = not settings.drawbackground
		if settings.DEBUG and event.type == KEYDOWN and event.key == K_F4:
			state.you.y = 100
			state.you.hp += 100
		if event.type == KEYDOWN and event.key == K_F5 and scene.current is play:
			state.save()
		if settings.DEBUG and event.type == KEYDOWN and event.key == K_F6:
			scene.current = play
	kpressed = pygame.key.get_pressed()
	if scene.current is not lastscene:
		scene.current.init()
		lastscene = scene.current
	s = scene.current
	if tconfirmfull:
		if tconfirmfull == 10:
			s.think(0, events, kpressed)
		s.draw()
		ptext.draw("Press space to\nconfirm fullscreen", fontsize = 100, owidth = 1,
			center = window.screen.get_rect().center)
		tconfirmfull -= dt
		if tconfirmfull <= 0:
			settings.fullscreen = False
			window.init()
			tconfirmfull = 0
	else:
		s.think(dt, events, kpressed)
		s.draw()
	if settings.DEBUG:
		ptext.draw("%.4f, %.1f" % (state.you.X, state.you.y), fontsize = F(36),
			bottomright = (window.sx - F(10), window.sy - F(50)), cache = False)
		ptext.draw("%.1ffps" % clock.get_fps(), fontsize = F(36),
			bottomright = (window.sx - F(10), window.sy - F(10)), cache = False)
	pygame.display.flip()

if scene.current is play and settings.autosave:
	state.save()
pygame.quit()

