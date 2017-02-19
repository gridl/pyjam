from __future__ import division
import pygame
from pygame.locals import *
from . import util, settings, state
from .util import F

screen = None
sx, sy = None, None
x0, y0, Z = None, None, None

def init():
	global screen, sx, sy, x0, y0, Z
	sy = settings.windowsize
	sx = int(round(sy * 16 / 9))
	if sy == 480: sx = 854  # special case to match YouTube video size
	if settings.fullscreen:
		sx0, sy0 = max(pygame.display.list_modes())
		sx, sy = min((sx0, int(round(sx0 * 9 / 16))), (int(round(sy0 * 16 / 9)), sy0))
	flags = 0
	if settings.fullscreen: flags |= FULLSCREEN
	screen = pygame.display.set_mode((sx, sy), flags)
	util.seth(sy)
	pygame.display.set_caption(settings.gamename)
	
	x0 = 0
	y0 = 0
	Z = 1

def screenpos(pos):
	x, y = pos
	return F([(x - x0) * Z + 427, (y - y0) * Z + 240])

def think(dt):
	global x0, y0
	x0 += state.scrollspeed * dt
	y0 = state.you.y / 2

