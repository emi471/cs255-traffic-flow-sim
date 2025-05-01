#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 13:33:46 2025

@author: mmascavage
"""

import numpy as np
from trafficSim import *
import csv

sim = Simulation()

# Play with these
n = 20      # Iterations for road turns
a = -2      # Indicates point a 
b = 12      # Indicates point b
l = 200     # Length of road

NUM_OF_ROADS = 12 # Number of roads
VEHICLE_RATE = 60 # Vehicle spawn rate per minute
STEPS_PER_UPDATE = 1   # Number of steps per update

# Nodes
WEST_RIGHT_START = (-b-l, a)
WEST_LEFT_START =	(-b-l, -a)

SOUTH_RIGHT_START = (a, b+l)
SOUTH_LEFT_START = (-a, b+l)

EAST_RIGHT_START = (b+l, -a)
EAST_LEFT_START = (b+l, a)

NORTH_RIGHT_START = (-a, -b-l)
NORTH_LEFT_START = (a, -b-l)

WEST_RIGHT = (-b, a)
WEST_LEFT =	(-b, -a)

SOUTH_RIGHT = (a, b)
SOUTH_LEFT = (-a, b)

EAST_RIGHT = (b, -a)
EAST_LEFT = (b, a)

NORTH_RIGHT = (-a, -b)
NORTH_LEFT = (a, -b)

# Roads
WEST_INBOUND = (WEST_LEFT_START, WEST_LEFT)      # Inbound now uses LEFT
SOUTH_INBOUND = (SOUTH_LEFT_START, SOUTH_LEFT)
EAST_INBOUND = (EAST_LEFT_START, EAST_LEFT)
NORTH_INBOUND = (NORTH_LEFT_START, NORTH_LEFT)

WEST_OUTBOUND = (WEST_RIGHT, WEST_RIGHT_START)   # Outbound now uses RIGHT
SOUTH_OUTBOUND = (SOUTH_RIGHT, SOUTH_RIGHT_START)
EAST_OUTBOUND = (EAST_RIGHT, EAST_RIGHT_START)
NORTH_OUTBOUND = (NORTH_RIGHT, NORTH_RIGHT_START)

WEST_STRAIGHT = (WEST_LEFT, EAST_RIGHT)
SOUTH_STRAIGHT = (SOUTH_LEFT, NORTH_RIGHT)
EAST_STRAIGHT = (EAST_LEFT, WEST_RIGHT)
NORTH_STRAIGHT = (NORTH_LEFT, SOUTH_RIGHT)

#WEST_RIGHT_TURN = turn_road(WEST_LEFT, NORTH_RIGHT, TURN_RIGHT, n)
#WEST_LEFT_TURN = turn_road(WEST_LEFT, SOUTH_RIGHT, TURN_LEFT, n)
WEST_RIGHT_TURN = turn_road(WEST_LEFT, NORTH_RIGHT, (0, 0), n)
WEST_LEFT_TURN = turn_road(WEST_LEFT, SOUTH_RIGHT, (0, 0), n)

#SOUTH_RIGHT_TURN = turn_road(SOUTH_LEFT, WEST_RIGHT, TURN_RIGHT, n)
#SOUTH_LEFT_TURN = turn_road(SOUTH_LEFT, EAST_RIGHT, TURN_LEFT, n)
SOUTH_RIGHT_TURN = turn_road(SOUTH_LEFT, WEST_RIGHT, (0, 0), n)
SOUTH_LEFT_TURN = turn_road(SOUTH_LEFT, EAST_RIGHT, (0, 0), n)

#EAST_RIGHT_TURN = turn_road(EAST_LEFT, SOUTH_RIGHT, TURN_RIGHT, n)
#EAST_LEFT_TURN = turn_road(EAST_LEFT, NORTH_RIGHT, TURN_LEFT, n)
EAST_RIGHT_TURN = turn_road(EAST_LEFT, SOUTH_RIGHT, (0, 0), n)
EAST_LEFT_TURN = turn_road(EAST_LEFT, NORTH_RIGHT, (0, 0), n)

#NORTH_RIGHT_TURN = turn_road(NORTH_LEFT, EAST_RIGHT, TURN_RIGHT, n)
#NORTH_LEFT_TURN = turn_road(NORTH_LEFT, WEST_RIGHT, TURN_LEFT, n)
NORTH_RIGHT_TURN = turn_road(NORTH_LEFT, EAST_RIGHT, (0, 0), n)
NORTH_LEFT_TURN = turn_road(NORTH_LEFT, WEST_RIGHT, (0, 0), n)

sim.create_roads([
    WEST_INBOUND,   #0
    SOUTH_INBOUND,  #1
    EAST_INBOUND,   #2
    NORTH_INBOUND,  #3

    WEST_OUTBOUND,  #4
    SOUTH_OUTBOUND, #5
    EAST_OUTBOUND,  #6
    NORTH_OUTBOUND, #7

    WEST_STRAIGHT,  #8
    SOUTH_STRAIGHT, #9
    EAST_STRAIGHT,  #10
    NORTH_STRAIGHT, #11

    *WEST_RIGHT_TURN,
    *WEST_LEFT_TURN,

    *SOUTH_RIGHT_TURN,
    *SOUTH_LEFT_TURN,

    *EAST_RIGHT_TURN,
    *EAST_LEFT_TURN,

    *NORTH_RIGHT_TURN,
    *NORTH_LEFT_TURN,
])

def road(a): return range(a, a+n)

sim.create_gen({
'vehicle_rate': VEHICLE_RATE,
'vehicles':[
    # 1st Lane
    [2, {'path': [0, 8, 6]}],
    [2, {'path': [0, *road(NUM_OF_ROADS), 5]}],
    # [2, {'path': [0, *road(24+n), 7]}],

    [2, {'path': [1, 9, 7]}],
    [2, {'path': [1, *road(NUM_OF_ROADS+2*n), 6]}],
    # [1, {'path': [1, *road(24+3*n), 4]}],

    [3, {'path': [2, 10, 4]}],
    [3, {'path': [2, *road(NUM_OF_ROADS+4*n), 7]}],
    # [1, {'path': [2, *road(24+5*n), 5]}],

    [3, {'path': [3, 11, 5]}],
    [3, {'path': [3, *road(NUM_OF_ROADS+6*n), 4]}],
    # [2, {'path': [3, *road(24+7*n), 6]}],
]})

sim.create_signal([[0], [1], [2], [3]])
#sim.create_signal([[12], [13], [14], [15]])

# Start simulation
win = Window(sim)
win.zoom = 10
if(sim.isPaused == False):
    win.run(steps_per_update=STEPS_PER_UPDATE)
