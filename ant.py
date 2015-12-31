#! /usr/bin/python3

from vector import Vector
from individual import Individual

import math
import random
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

	def get_id ( self ):
		return self.ID

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

		return individual,self.tabu_list

	def create_configuration ( self, index, pheronome ):
		"""
		Create configuration
		"""
		# print ( "Evaluate config on index: ", index )
		# print(index,len(self.vector.get_amino_sequance())-1)
		if index >= len(self.vector.get_amino_sequance())-1:
			return True

		# Compute free energy of possible moves
		free_energy = self.compute_free_energy_of_possible_moves ( index )
		# print("Free energy of directions: ", free_energy)

		probability = self.compute_probability_of_next_move ( index, pheronome[index], free_energy )
		# print("Probability of next move: ", probability)

		next_move,next_move_values = self.pick_next_moves ( probability )
		# print("Next moves: ", next_move )

		counter_of_success = 0
		for move,value in zip(next_move,next_move_values):
			if value != -10000000000000000000:
				direction = self.get_direction ( move, index )
				self.vector.set_configuration_at_index(index,direction)

				self.add_to_tabu_list ( index, move )

				counter_of_success += 1

				new_index = index + 1
				if self.create_configuration ( new_index, pheronome ):
					return True

		if counter_of_success == 0:
			return False

	def add_to_tabu_list ( self, index, move ):
		if len(self.tabu_list) > index:
			self.tabu_list[index] = move
		else:
			self.tabu_list.append(move)


	def get_direction ( self, move, index ):
		last_coord = self.vector.get_configuration_at_index(index-1)

		return last_coord*MULTIPLY[move]

	def pick_next_moves ( self, probability ):
		list_of_index = []
		list_of_values = []

		for prob in range(len(probability)):
			list_of_index.append(prob)
			list_of_values.append(probability[prob])

		list_of_index,list_of_values = self.sort_by ( list_of_index, list_of_values )

		# print(list_of_index,list_of_values)

		return list_of_index,list_of_values

	def sort_by ( self, indexes, values ):
		comparator = self.compare

		for index in range ( len(indexes)-1, 0, -1):
			lowest_index = 0
			for find_index in range (1, index+1):
				if comparator(values[find_index] ,values[lowest_index]):
					lowest_index = find_index

			tmp_index = indexes[index]
			indexes[index] = indexes[lowest_index]
			indexes[lowest_index] = tmp_index

			tmp_values = values[index]
			values[index] = values[lowest_index]
			values[lowest_index] = tmp_values

		# for index in range(len(indexes)-1):
		# 	if values[index] == values[index+1]:
		# 		if random.random() < 0.5:
		# 			print("Switch")
		# 			print(values)
		# 			tmp = indexes[index]
		# 			indexes[index] = indexes[index+1]
		# 			indexes[index+1] = tmp

		# print(indexes)
		return indexes,values

	def compare( self, first, second ):
		if first >  second:
			return True
		else:
			return False

	def compute_probability_of_next_move ( self, index, pheronome, free_energy ):
		probability = []
		total = 0
		for pheronome_val, free_energy_val in zip (pheronome,free_energy):
			if free_energy_val == None:
				probability.append(None)
			else:
				value = math.pow(pheronome_val,PHEROMONE_VAL) * math.pow(1/free_energy_val,HEURISTIC_VAL)

				total += value

				probability . append ( value )

		for prob in range(len(probability)):
			if probability[prob] != None:
				probability[prob] *= 1/total
			else:
				probability[prob] = -10000000000000000000

		return probability

	def compute_free_energy_of_possible_moves ( self, index ):
		"""
		Compute free energy of moves
		"""
		last_coord = self.vector.get_configuration_at_index(index-1)

		directions = []
		for direction in MULTIPLY:
			directions.append(last_coord*direction)

		# print ( "Last coord: ", last_coord)
		# print ( "Directions: ", directions)

		# Get space cumulative add configuration to index-1
		space_config = self.vector.compute_space_configuration(index-1)
		space_config_counter = Counter ( space_config )
		# Get free energy to index-1
		free_energy = self.vector.compute_free_energy(index-1)

		valid = []
		free_energy_of_all_directions = []
		for direction in directions:
			new_space_config = space_config[-1]+direction
			# Check valid of configuration
			if new_space_config in space_config_counter:
				# Record exist
				valid.append(False)
			else:
				# Record NOT exist
				valid.append(True)

			if valid[-1]:
				self.vector.set_configuration_at_index(index, direction )
				free_energy_of_all_directions.append ( self.vector.compute_free_energy(index))
			else:
				free_energy_of_all_directions.append ( None )


		return free_energy_of_all_directions


