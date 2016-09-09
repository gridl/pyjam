import random, math
from . import ptext, state, thing, view, control, bounce, quest, dialog, background, progress
from . import scene, cutscene
from .util import F

def init():
	state.reset(progress.chosen)
	control.cursor = None
	control.dragpos = None
	control.buttons = [
		control.Button((10, 10, 100, 40), "build 1"),
		control.Button((10, 60, 100, 40), "build 2"),
		control.Button((10, 110, 100, 40), "build 3"),
	]
	background.init()

def think(dt, mpos, mdown, mup, mwheel, rdown, mclick):
	control.towerinfo.target = None
	if control.cursor:
		dragthink(dt, mpos, mdown, mup, mwheel, rdown, mclick)
	elif control.dragpos:
		pdragthink(dt, mpos, mdown, mup, mwheel, rdown, mclick)
	else:
		nodragthink(dt, mpos, mdown, mup, mwheel, rdown, mclick)

	if mwheel:
		view.zoom(mwheel)

	for obj in state.thinkers:
		obj.think(dt)

	bounce.adjust(state.colliders, dt)
	state.think(dt)
	quest.think(dt)
	dialog.think(dt)
	control.towerinfo.think(dt)
	if state.twin > 2 and not state.tlose:
		progress.complete(progress.chosen)
		scene.push(cutscene.Win())
	if state.tlose > 2:
		scene.push(cutscene.Lose())


def dragthink(dt, mpos, mdown, mup, mwheel, rdown, mclick):
	gpos = view.gamepos(mpos)
	if not control.cursor.alive:
		control.cursor = None
		return
	if mclick:
		toclick = control.cursor
		drop()
		if toclick.alive:
			toclick.onclick()
		return
	elif mup:
		drop()
		return
	control.cursor.scootch(gpos[0] - control.cursor.x, gpos[1] - control.cursor.y)
	control.cursor.think(dt)
	control.cursor.reset()
	control.cursor.constraintoworld()

def pdragthink(dt, mpos, mdown, mup, mwheel, rdown, mclick):
	view.drag(control.dragpos, mpos)
	if mwheel or mup or rdown:
		control.dragpos = None

def nodragthink(dt, mpos, mdown, mup, mwheel, rdown, mclick):
	for button in control.buttons:
		if button.within(mpos):
			if mdown:
				click(button.name)
				return
	gpos = view.gamepos(mpos)
	toclick = None
	for obj in state.mouseables:
		if obj.within(gpos):
			obj.onhover()
			if toclick is None or obj.distanceto(gpos) < toclick.distanceto(gpos):
				toclick = obj
	downed = None
	if toclick:
		control.towerinfo.target = toclick.flavors()
		if mdown:
			toclick.onmousedown()
			downed = toclick
			control.dragpos = None
		if rdown:
			toclick.onrdown()
	if mdown and not downed:
		control.dragpos = gpos


def click(bname):
	if state.cell.isfull():
		return
	flavor = {
		"build 1": 0,
		"build 2": 1,
		"build 3": 2,
	}[bname]
	egg = thing.Egg(container = state.cell, flavor = flavor)
	state.cell.add(egg)
	egg.addtostate()

def drop():
	for obj in state.buildables:
		if obj.cantake(control.cursor):
			for x in control.cursor.slots:
				obj.add(x)
				x.container = obj
				control.cursor.die()
			break
	else:
		control.cursor.addtostate()
	control.cursor = None

def draw():
	view.clear(color = (0, 50, 50))
	state.drawwaves()
	for obj in state.drawables:
		obj.draw()
	if control.cursor:
		control.cursor.draw()
	background.draw()
	view.drawiris(state.Rlevel)
	for button in control.buttons:
		button.draw()
	dialog.draw()

	ptext.draw("ATP1: %d\nATP2: %d\nhealth: %d" % (state.atp[0], state.atp[1], state.health),
		bottom = F(470), left = F(10), fontsize = F(26), color = "yellow")
	control.towerinfo.draw()

def abort():
	state.save()

