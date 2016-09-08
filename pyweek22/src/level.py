# The levels that are unlocked when you beat a given level.

unlocks = {
	1: [2],
	2: [3],
	3: [4],
	4: [5],
	5: [6],
	6: [7, "endless"],
	7: [8],
	8: [9],
}

# position of each level on the menu screen
layout = {
	1: [30, 120, 70],
	2: [30, 320, 140],
	3: [45, 500, 160],
	4: [30, 400, 240],
	5: [30, 140, 220],
	6: [45, 200, 360],
	7: [30, 380, 400],
	8: [30, 550, 310],
	9: [50, 750, 400],
	"endless": [30, 50, 400],
	"qwin": [30, 800, 200],
}

# Level data

data = {
	1: {
		"Rlevel": 150,
		"cellpos": (0, -100),
		"health": 10,
		"atp": [20, 0],
		"wavespecs": [
			(0, 0, 5),
			(20, 0.15, 10),
			(40, -0.15, 15),
			(60, -0.1, 20),
			(60, 0.1, 20),
		],
	},
	2: {
		"Rlevel": 150,
		"cellpos": (0, -100),
		"health": 10,
		"atp": [20, 0],
		"wavespecs": [
			(0, 0, 5),
			(20, 0.15, 10),
			(40, -0.15, 15),
			(60, -0.1, 20),
			(60, 0.1, 20),
		],
	},



	# Endless mode
	"endless": {
		"Rlevel": 400,
		"cellpos": (0, 0),
		"health": 100,
		"atp": 100,
		# Endless mode waves are procedurally generated after the first one.
		"wavespecs": [
			(0, 0, 5),
		],
	},

	# Quick-win level (just a single enemy)
	"qwin": {
		"Rlevel": 100,
		"cellpos": (0, -50),
		"health": 99999,
		"atp": 99999,
		"wavespecs": [
			(0, 0, 1),
		],
	},
}


