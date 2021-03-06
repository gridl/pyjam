from __future__ import division
import pygame, math, random, time
from pygame.locals import *
from src import window, thing, settings, state, hud, quest, background, dialog, ptext, scene, sound
from src.scenes import play
from src.window import F

def init():
	global t
	t = 0
	window.camera.X0 = 0
	window.camera.R = window.sy / 200
	window.camera.y0 = state.R - 300 / 16
	sound.playtitlemusic()
	background.wash()

def think(dt, events, kpressed):
	global t
	t += dt

	background.think(dt, 4)

	for event in (events or []):
		if event.type == KEYUP and event.key == "go":
			scene.current = None

def draw():
	window.screen.fill((0, 0, 0))
	background.draw(hradius = 6)

	a1 = math.clamp((t - 3.5) / 2, 0, 1)
	a2 = math.clamp((t - 10) / 2, 0, 1)
	ptext.draw(settings.gamename, fontsize = F(70), center = F(427, 140),
		owidth = 2, color = "#44FF77", gcolor = "#AAFFCC", alpha = a1, fontname = "Audiowide")
	ptext.draw("Thank you for playing", fontsize = F(26), midtop = F(427, 180),
		owidth = 2, color = "#7777FF", gcolor = "#AAAAFF", alpha = a2, fontname = "Audiowide")

	background.drawwash()

