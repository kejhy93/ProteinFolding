#! /usr/bin/python3

from vector import Vector
from individual import Individual

import math
from collections import Counter

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

		# configuration
		self.vector = Vector ( sequance )

		self.tabu_list = []

	def search ( self, pheronome ):
		"""
		Create candidate and return 
		"""

		# Create first connection
		self.vector.clean_configuration()
		self.vector.set_configuration_at_index(0,UP)
		# print(self.vector)

		MAX_SIZE_OF_CONFIG = len(self.vector.get_amino_sequance())-1

		self.create_configuration ( 1, pheronome )
		
		individual = Individual(self.vector.get_amino_sequance() )

		individual.set_individual ( self.vector )

		return individual

	def create_configuration ( self, index, pheronome ):
		"""
		Create configuration
		"""
		print ( "Evaluate config on index: ", index )

		print(self.vector)
		self.vector.plot_config(index)
		if index >= len(self.vector.get_amino_sequance())-1:
			return

		probability = self.compute_probability_of_next_move ( pheronome, index )
		print ( self.vector )
		print("Probability: ", probability)
		next_direction = self.get_direction ( probability )
		print("Next move: ", next_direction)

		if probability[next_direction] < 0:
			return

		if next_direction == STRAIGHT:
			self.make_next_move ( MULT_TO_STRAIGHT, index )
		elif next_direction == LEFT:
			self.make_next_move ( MULT_TO_LEFT, index )
		elif next_direction == RIGHT:
			self.make_next_move ( MULT_TO_RIGHT, index )

		self.vector.compute_space_configuration(index)

		new_index = index + 1
		self.create_configuration ( new_index, pheronome )

		print ( " ========================== ")
