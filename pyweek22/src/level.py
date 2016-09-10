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

learns = {
	1: ["XX"],
	2: ["Y", "XY"],
	3: ["Z", "YY"],
	4: ["XZ", "YZ"],
	5: [],
	6: [],
	7: [],
	8: [],
}

# position of each level on the menu screen
layout = {
	1: [30, 120, 70],
	2: [30, 320, 140],
	3: [45, 600, 200],
	4: [30, 400, 240],
	5: [30, 140, 220],
	6: [45, 200, 360],
	7: [30, 380, 400],
	8: [30, 550, 310],
	9: [50, 730, 380],
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
		"autoatp": [0.2, 0],  # per second
		"wavespecs": [
			(12, 0, "ant", 3),
			(40, 0.15, "ant", 5),
			(60, -0.15, "ant", 10),
			(80, -0.1, "ant", 20),
			(80, 0.1, "ant", 20),
		],
	},
	2: {
		"Rlevel": 180,
		"cellpos": (-100, -100),
		"health": 20,
		"atp": [30, 0],
		"autoatp": [0.2, 0],
		"wavespecs": [
			(12, 0.2, "ant", 5),
			(30, 0.125, "ant", 10),
			(30, 0.125, "Lant", 2),
			(70, 0, "ant", 5),
			(70, 0, "Lant", 4),
			(120, 0.05, "ant", 5),
			(120, 0.05, "Lant", 6),
			(120, 0.2, "ant", 5),
			(120, 0.2, "Lant", 6),
		],
	},
	3: {
		"Rlevel": 250,
		"cellpos": (0, 0),
		"health": 40,
		"atp": [60, 0],
		"wavespecs": [
		],
		"streamspecs": [
			(20, "ant", 20, 0.1),
			(60, "Lant", 5, 0.05),
		],
	},
	4: {
		"Rlevel": 180,
		"cellpos": (150, 0),
		"health": 50,
		"atp": [30, 0],
		"autoatp": [0.2, 0],
		"wavespecs": [
			(15, 0.75, "ant", 15),
			(40, 0.7, "bee", 5),
			(40, 0.8, "bee", 5),
			(120, 0.75, "bee", 20),
			(200, 0.8, "bee", 15),
			(205, 0.75, "bee", 15),
			(205, 0.75, "Lbee", 5),
			(210, 0.7, "bee", 15),
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


