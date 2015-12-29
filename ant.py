#! /usr/bin/python3

from vector import Vector
from individual import Individual

import math

STRAIGHT=0
LEFT=1
RIGHT=2

UP = complex(0,1)

MULT_TO_STRAIGHT = complex(1,0)
MULT_TO_LEFT = complex(0,1)
MULT_TO_RIGHT = complex(0,-1)

DIRECTIONS = [ STRAIGHT, LEFT, RIGHT ]
MULTIPLY = [ MULT_TO_STRAIGHT, MULT_TO_LEFT, MULT_TO_RIGHT]


PHEROMONE_VAL = 2
HEURISTIC_VAL = 1

class Ant:
	def __init__ ( self, ID, sequance ):
		self.ID = ID

		self.vector = Vector ( sequance )

	def search ( self, pheronome ):
		"""
		Create candidate and return 
		"""

		# Create first connection
		self.vector.clean_configuration()
		self.vector.set_configuration_at_index(0,UP)
		print(self.vector)


		
		individual = Individual(self.vector.get_amino_sequance() )

		individual.set_configuration ( self.vector )

		return individual
