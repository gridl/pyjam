import json, os.path
from src import settings

worlddata = json.load(open(os.path.join("data", "worlddata.json")))
R = worlddata["R"]
Rcore = worlddata["Rcore"]

you = None
mother = None
target = None
ships = []
objs = []
hazards = []
effects = []
beacons = []
convergences = []

goals = []

quickteleport = True

def buildnetwork():
	from src import thing, window
	del network[:]
	nobjs = [mother.thingid] + [ship.thingid for ship in ships if ship.rnetwork()]
	if len(nobjs) < 2:
		return
	ds = {}
	for id0 in nobjs:
		for id1 in nobjs:
			if id0 >= id1:
				continue
			thing0, thing1 = thing.get(id0), thing.get(id1)
			rmax = max(thing0.rnetwork(), thing1.rnetwork())
			d = window.distance(thing0, thing1)
			if d <= rmax:
				ds[(id0, id1)] = d
	# TODO: remove triangles
	for id0, id1 in ds:
		network.append((thing.get(id0), thing.get(id1)))

def save():
	import window, thing, quest, dialog
	def getids(x):
		if x is None:
			return None
		if isinstance(x, list):
			return [a.thingid for a in x]
		return x.thingid
	savestate = {
		"you": getids(you),
		"mother": getids(mother),
		"target": getids(target),
		"ships": getids(ships),
		"objs": getids(objs),
		"hazards": getids(hazards),
		"beacons": getids(beacons),
		"effects": getids(effects),
		"convergences": getids(convergences),
		"goals": getids(goals),
		"quickteleport": quickteleport,
		"camera": window.camera.dump(),
		"thing": thing.dump(),
		"quest": quest.dump(),
		"dialog": dialog.dump(),
	}
	json.dump(savestate, open(settings.savename, "w"))

def load():
	import window, thing, quest, dialog
	savestate = json.load(open(settings.savename))
	thing.load(savestate["thing"])
	window.camera.load(savestate["camera"])
	quest.load(savestate["quest"])
	dialog.load(savestate["dialog"])
	def getthings(x):
		if x is None:
			return None
		if isinstance(x, list):
			return [thing.get(a) for a in x]
		return thing.get(x)
	global you, mother, target, ships, objs, hazards, beacons, effects, convergences, goals, quickteleport
	you = getthings(savestate["you"])
	mother = getthings(savestate["mother"])
	target = getthings(savestate["target"])
	ships = getthings(savestate["ships"])
	objs = getthings(savestate["objs"])
	hazards = getthings(savestate["hazards"])
	beacons = getthings(savestate["beacons"])
	effects = getthings(savestate["effects"])
	convergences = getthings(savestate["convergences"])
	goals = getthings(savestate["goals"])
	quickteleport = savestate["quickteleport"]


