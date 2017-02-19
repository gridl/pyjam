import random
from . import view, settings, ptext, state
from .util import F

stars = []
def init():
	stars.extend([
		(random.uniform(0, 1000000), random.uniform(0, 1000000), random.uniform(0.4, 0.8))
		for _ in range(10000)
	])

def draw():
	x0, y0 = view.x0 + state.xoffset, view.y0
	view.screen.fill((0, 0, 0))
	pos = F(427 - 0.3 * x0, 240 - 0.3 * y0)
	ptext.draw(settings.gamename, center = pos, color = "#220000", fontsize = F(60), angle = 10)
	pos = F(600 - 0.3 * x0, 400 - 0.3 * y0)
	ptext.draw("by team Universe Factory", center = pos, color = "#222222", fontsize = F(40), angle = 10)
	N = min(len(stars), int(view.sx * view.sy * 0.001))
	for x, y, z in stars[:N]:
		px = int((x - x0) * z % view.sx)
		py = int((y - y0) * z % view.sy)
		color = (int(255 * z),) * 3
		view.screen.set_at((px, py), color)

