#! /usr/bin/python3

from vector import Vector
from individual import Individual

import math
import random
from collections import Counter

import utils

from threading import *

STRAIGHT=0
LEFT=1
RIGHT=2

UP = complex(0,1)

MULT_TO_STRAIGHT = complex(1,0)
MULT_TO_LEFT = complex(0,1)
MULT_TO_RIGHT = complex(0,-1)

DIRECTIONS = [ STRAIGHT, LEFT, RIGHT ]
MULTIPLY = [ MULT_TO_STRAIGHT, MULT_TO_LEFT, MULT_TO_RIGHT]

NO_ROUTE = -10000000000000000000

SWITCH_PROBABILITY = 0.3
DIFFERENCE = 0.0025
CHANGE_RATE = 0


class Ant(Thread):
	def __init__ ( self, ID, sequance, pheronome, heuristic_val, pheronome_val ):
		Thread.__init__(self)
		self.ID = ID

		# configuration
		self.vector = Vector ( sequance )
		# init tabu list to record ant's route
		self.tabu_list = []

		self.verbose = False

		self.start_time = None

		# Get pheronome
		self.pheronome = pheronome
		# Init result of ant's search
		self.individual = None

		self.PHEROMONE_VAL = pheronome_val
		self.HEURISTIC_VAL = heuristic_val

	def get_id ( self ):
		return self.ID

	def run ( self ):
		self.search(self.pheronome)

	def search ( self, pheronome ):
		"""
		Create candidate and return 
		"""
		self.start_time = utils.get_time_in_millis()
		# Create first connection
		self.vector.clean_configuration()
		self.vector.set_configuration_at_index(0,UP)
		self.tabu_list.append(0)
		# print(self.vector)

		MAX_SIZE_OF_CONFIG = len(self.vector.get_amino_sequance())-1

		self.create_configuration ( 1, pheronome )

		# Check if new individuals was found
		if ( len(self.vector.get_configuration()) != len(self.vector.get_amino_sequance())-1 ):
			# No individuals was found, return None,None

			# print("No indiviudals found")
			return None,None

		self.individual = Individual(self.vector.get_amino_sequance() )

		self.individual.set_individual ( self.vector )

		return self.individual,self.tabu_list

	def create_configuration ( self, index, pheronome ):
		"""
		Create configuration
		"""
		if self.verbose:
			print("Create configuration: ", index )

		if index >= len(self.vector.get_amino_sequance())-1:
			return True

		end_time = utils.get_time_in_millis()

		if ( utils.millis_to_second(end_time-self.start_time) >= 10 ):
			return True

		# Compute free energy of possible moves
		free_energy = self.compute_free_energy_of_possible_moves ( index )
		# print("Free energy of directions: ", free_energy)

		# Compute probability of all possible moves
		probability = self.compute_probability_of_next_move ( index, pheronome[index], free_energy )
		# print("Probability of next move: ", probability)

		# Sort probability list
		next_move,next_move_values = self.pick_next_moves ( probability )
		# print("Next moves: ", next_move )

		counter_of_success = 0
		for move,value in zip(next_move,next_move_values):
			if value != NO_ROUTE:
				direction = self.get_direction ( move, index )
				self.vector.set_configuration_at_index(index,direction)
				self.vector.compute_space_configuration(index)

				self.add_to_tabu_list ( index, move )

				counter_of_success += 1

				new_index = index + 1

				if self.create_configuration ( new_index, pheronome ):
					return True

		if counter_of_success == 0:
			return False

	def add_to_tabu_list ( self, index, move ):
		"""
		Add new ant's move to tabu list
		"""
		if len(self.tabu_list) > index:
			self.tabu_list[index] = move
		else:
			self.tabu_list.append(move)


	def get_direction ( self, move, index ):
		last_coord = self.vector.get_configuration_at_index(index-1)

		return last_coord*MULTIPLY[move]

	def pick_next_moves ( self, probability ):
		"""
		Pick next move from sorted probability list
		"""
		list_of_index = []
		list_of_values = []

		for prob in range(len(probability)):
			list_of_index.append(prob)
			list_of_values.append(probability[prob])

		list_of_index,list_of_values = self.sort_by ( list_of_index, list_of_values )

		return list_of_index,list_of_values

	def sort_by ( self, indexes, values ):
		"""
		Sort computed probabilities by select sort
		"""
		comparator = self.compare

		for index in range ( len(indexes)-1, 0, -1):
			lowest_index = 0
			for find_index in range (1, index+1):
				if comparator(values[find_index] ,values[lowest_index]):
					lowest_index = find_index

			indexes,values = self.swap ( indexes, values, index, lowest_index)


		# Ant colony returns equal solution
		# Make some random change
		change = 0
		# Iterate probability list
		for index in range(len(indexes)-1):
			# Check if two probabilities are almost equal
			if random.random() < 0.2:
				if self.little_diference ( values[index], values[index+1] ) and change < CHANGE_RATE:
					switch_probability = random.random()
					# Check probability
					if switch_probability < SWITCH_PROBABILITY:
						# Swap two probabilities
						print("Swap")
						indexes,values = self.swap(indexes, values, index, index+1)

						change -= 1

		return indexes,values

	def swap ( self, indexes, values, first_index, second_index ):
		"""
		Swap two item in indexes and values lists
		"""
		tmp = indexes[first_index]
		indexes[first_index] = indexes[second_index]
		indexes[second_index] = tmp

		tmp = values[first_index]
		values[first_index] = values[second_index]
		values[second_index] = tmp

		return indexes,values

	def little_diference ( self, first, second ):
		"""
		Check if difference between two probabilities is lower then DIFFERENCE
		"""
		diff = abs(first-second)

		if diff < DIFFERENCE:
			return True
		else:
			return False

	def compare( self, first, second ):
		"""
		Compare function for sort probabilities
		"""
		if first < second:
			return True
		else:
			return False

	def compute_probability_of_next_move ( self, index, pheronome, free_energy ):
		"""
		Compute probability of all possible moves based on pheronome value and free energy

		Return unsorted list of probabilities

		If move is invalid return NO_ROUTE
		"""
		if self.verbose:
			print("Compute probability: ", index )

		# Empty probability list
		probability = []
		normalised_value = 0

		# Iterate all values of pheronome values and free energy values
		for pheronome_val, free_energy_val in zip (pheronome,free_energy):
			if free_energy_val == None:
				probability.append(None)
			else:
				# Unnormalised probability of move
				value = math.pow(pheronome_val,self.PHEROMONE_VAL) * math.pow(1/free_energy_val,self.HEURISTIC_VAL)
				# Computed value add to normalised value
				normalised_value += value
				# Add computed (unnormalised) value to list of probabilities
				probability . append ( value )

		# Normalise computed probabilities
		for prob in range(len(probability)):
			# Check invalid move
			if probability[prob] != None:
				# Move is valid, multiply normalised value
				probability[prob] *= 1/normalised_value
			else:
				# Move is invalid, return NO_ROUTE
				probability[prob] = NO_ROUTE

		return probability

	def compute_free_energy_of_possible_moves ( self, index ):
		"""
		Compute free energy of moves
		"""
		if self.verbose:
			print("Compute free energy: ", index )
		# Last configuration of completed protein
		last_coord = self.vector.get_configuration_at_index(index-1)

		# List with all possible configurations
		directions = []
		for direction in MULTIPLY:
			# Add new possible configuration to the list
			directions.append(last_coord*direction)

		# Get space cumulative add configuration of completed configuration
		space_config = self.vector.get_space_configuration(index)

		# Get space configuration set to detect of invalid move
		space_config_counter = self.vector.get_space_configuration_set()

		# Get free energy of completed configuration
		free_energy = self.vector.compute_free_energy(index-1, space_config)

		valid = None
		free_energy_of_all_directions = []

		for direction in directions:
			new_space_config = space_config[-1]+direction
			# Check valid of configuration
			valid = self.check_valid_move ( new_space_config, space_config_counter )

			if valid:
				# New configuration is valid 
				# Add new configuration
				space_config.append(new_space_config)
				# Compute free energy of completed protein and new configuration
				new_free_energy = self.vector.update_free_energy ( free_energy, index+1, space_config )

				# Delete new configuration
				del space_config[-1]
				# Add computed free energy to list of free energys
				free_energy_of_all_directions.append ( new_free_energy  )
			else:
				# New configuration is invalid
				free_energy_of_all_directions.append ( None )

		return free_energy_of_all_directions

	def get_individual ( self ):
		return self.individual

	def get_tabu_list ( self ):
		return self.tabu_list

	def check_valid_move ( self, tested_configuration, set_of_configuration ):
		"""
		Check if configuration is valid
		"""
		if tested_configuration in set_of_configuration:
			# Record exist
			valid = False
		else:
			# Record NOT exist
			valid = True

		return valid
