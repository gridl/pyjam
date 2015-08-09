import pygame, datetime
from pygame.locals import *
from src import settings, thing, window, ptext
from window import F
from src.scenes import play

window.init()
pygame.display.set_caption(settings.gamename)

clock = pygame.time.Clock()
playing = True
while playing:
	dt = clock.tick(settings.maxfps)
	events = list(pygame.event.get())
	for event in events:
		if event.type == QUIT:
			playing = False
		if event.type == KEYDOWN and event.key == K_ESCAPE:
			playing = False
		if event.type == KEYDOWN and event.key == K_F11:
			settings.fullscreen = not settings.fullscreen
			window.init()
		if event.type == KEYDOWN and event.key == K_F12:
			fname = datetime.datetime.now().strftime("screenshot-%Y%m%d%H%M%S.png")
			pygame.image.save(window.screen, fname)
	play.think(dt, events)
	window.screen.fill((0, 40, 0))
	play.draw()
	if settings.DEBUG:
		ptext.draw("%.1ffps" % clock.get_fps(), fontsize = F(36), owidth = 2,
			bottomright = (window.sx - 10, window.sy - 10))
	pygame.display.flip()

pygame.quit()

