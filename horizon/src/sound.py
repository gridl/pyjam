# Intro music plays on channel 0
# Title music plays on channel 1

# Gameplay music plays on channels 0/1/2

# Dialog on line 4
# Channels 5/6/7 for sound effects

from __future__ import division
import pygame, random, sys, math, os
from src import settings

freq = 22050

pygame.mixer.pre_init(freq, -16, 1, 1)


data = [random.randint(1, 255) for _ in range(freq)]
if sys.version_info >= (3,):
	static = bytes(data)
else:
	static = "".join(map(chr, data))
static *= 60
def playstatic(t):
	nsamp = int(freq * 2 * t)
	sound = pygame.mixer.Sound(static[:nsamp])
	sound.set_volume(0.01)
	sound.play()
	return sound

def loadsound(*args):
	path = os.path.join(*args) + "." + settings.soundext
	if not os.path.exists(path):
		print("Missing sound: " + name)
		return None
	return pygame.mixer.Sound(path)

sounds = {}
channels = {}
channel_volumes = {}
def init():
	for n in range(8):
		channels[n] = pygame.mixer.Channel(n)
	sounds["intro"] = loadsound("data", "music", "intro")
	sounds["title"] = loadsound("data", "music", "title")
	sounds["epic0"] = loadsound("data", "music", "epic")
	sounds["epic1"] = loadsound("data", "music", "epicer")
	sounds["epic2"] = loadsound("data", "music", "epicest")

def play(name):
	if name not in sounds:
		sounds[name] = loadsound("data", "sound", name)
		if sounds[name] is not None:
			sounds[name].set_volume({
				"teleport": 0.5,
			}.get(name, 1))
	if sounds[name] is None:
		return
	if not channels[5].get_busy():
		channels[5].play(sounds[name])
	elif not channels[6].get_busy():
		channels[6].play(sounds[name])
	else:
		channels[7].play(sounds[name])


tlineend = -100
def playline(name, volume = 1):
	global tlineend
	channels[4].set_volume(volume)
	line = loadsound("data", "dialog", name)
	tlineend = pygame.time.get_ticks() * 0.001 + line.get_length()
	channels[4].play(line)
def lineplaying():
	return pygame.time.get_ticks() * 0.001 <= tlineend

currentmusic = None
def playmusic(name):
	if name not in sounds:
		sounds[name] = loadsound("data", "music", name)
	sounds[name].play(-1)

musicmode = None
epicness = 0
epictarget = 0
def playintromusic():
	global musicmode
	musicmode = "intro"
	channels[0].set_volume(1)
	channels[0].play(sounds["intro"], -1)
def playtitlemusic():
	channels[1].set_volume(1)
	channels[1].play(sounds["title"], -1)
	channels[0].stop()
	channels[2].fadeout(1000)
def playgamemusic():
	global musicmode, epicness, epictarget
	musicmode = "game"
	epicness = 0
	epictarget = 0
	channels[0].set_volume(1)
	channels[1].set_volume(0)
	channels[2].set_volume(0)
	channel_volumes[0] = 1
	channel_volumes[1] = 0
	channel_volumes[2] = 0
	channels[0].play(sounds["epic0"], -1)
	channels[1].play(sounds["epic1"], -1)
	channels[2].play(sounds["epic2"], -1)
	
def think(dt):
	global epictarget
	if musicmode == "game":
		if epictarget == 0 and epicness > 0.75:
			epictarget = 1
		elif epictarget == 1 and epicness < 0.25:
			epictarget = 0
		elif epictarget == 1 and epicness > 1.75:
			epictarget = 2
		elif epictarget == 2 and epicness < 1.25:
			epictarget = 1
	musicvolume = settings.musicvolume[0] if lineplaying() else settings.musicvolume[1]

	dvmax = dt / settings.musiccrossfadetime
	for j in (0, 1, 2):
		goalvolume = musicvolume if j == epictarget else 0
		if channel_volumes[j] != goalvolume:
			dv = math.clamp(goalvolume - channel_volumes[j], -dvmax, dvmax)
			channel_volumes[j] += dv
			channels[j].set_volume(channel_volumes[j])
#	print [channels[j].get_volume() for j in (0, 1, 2)]


