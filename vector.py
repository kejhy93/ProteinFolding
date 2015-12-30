#! /usr/bin/python3

from collections import *
import matplotlib.pyplot as plt

import random
from copy import deepcopy
	
import numpy

from sequance_optimization import optimize_sequance

HYDROPHOBILIC = 1

NOT_VALID_CONFIGURATION = False
VALID_CONFIGURATION = True

class Vector:
	def __init__ ( self, protein_sequance ):
		self.verbose = False

		if self.verbose:
			print ("Vector -> init")

		self.sequance = protein_sequance

		self.configuration = []
		for i in range(len(self.sequance)-1):
			self.configuration.append ( complex (0, 1))

		# self.generate_random()

		self.free_energy = None
		self.space_configuration = []

		self.space_configuration_counter = Counter()

	def __str__ ( self ):
		res = ""
		res = " [ "

		first_print = True

		for config in self.configuration:
			if first_print:
				first_print = False
				res += " " + self.print_config(config)
			else:
				res += ", " + self.print_config(config)

		res += " ] "

		return res

	def clean_configuration ( self ):
		self.configuration = []

	def update_space_configuration_counter ( self, direction ):
		self.space_configuration = self.compute_space_configuration()

		self.space_configuration_counter = Counter ( self.space_configuration )

	def check_space_configuration_counter ( self, direction, index ):
		self.space_configuration = self.compute_space_configuration_to_index(index)
		print( "Space configuration: ",self.space_configuration)

		new_space_config = self.space_configuration[-1]+direction
		self.space_configuration_counter = Counter(self.space_configuration)

		print(self.space_configuration_counter)
		print(new_space_config)
		print( " ================================== ")
		if self.space_configuration_counter[new_space_config] == 0:
			return True
		else:
			return False

	def print_config ( self, config ):
		if config == complex(1,0):
			return "1"
		elif config == complex(-1,0):
			return "-1"
		elif config == complex(0,1):
			return "i"
		elif config == complex(0,-1):
			return "-i"

		return ""

	def check_valid_of_configuration ( self ):
		"""
		Check if configuration is valid

		Get space config and check if value of any cell is higher then 1

		True -> configuration is valid
		False -> configuration is NOT valid
		"""
		counter = Counter ( self.space_configuration )

		for key in counter:
			if counter[key] > 1:
				return False

		return True

	def length_between_amino ( self, first, second ):
		"""
		Return absolute value of two complex numbers
		"""
		diff_of_complex = first - second

		return (diff_of_complex.real**2 + diff_of_complex.imag**2)**0.5

	def check_valid_configuration ( self ):
		"""
		Check if configuration is valid
		"""
		self.compute_space_configuration()
		counter = Counter ( self.space_configuration )

		for key in counter:
			if counter[key] > 1:
				return NOT_VALID_CONFIGURATION

		return VALID_CONFIGURATION

	def set_configuration_at_index ( self, index, direction ):
		if index >= len(self.configuration):
			self.configuration.append(direction)
		else:
			self.configuration[index] = direction

	def get_configuration_at_index ( self, index ):
		return self.configuration[index]

	def multiply_configuration ( self, direction, index=0 ):
		"""
		Multiply vector from index by complex number direction
		"""
		if self.verbose:
			print ( "Original configration: ", self.configuration )

		for mult_index in range ( index, len(self.configuration)):
			self.configuration[mult_index] *= direction

		if self.verbose:
			print ( "Updated configration: ", self.configuration )

	def optimize_sequance ( self ):
		self.sequance = optimize_sequance ( self.sequance )
		for i in range(len(self.sequance)-1):
			self.configuration.append ( complex (0,1))

		return self.sequance

	def get_amino_sequance ( self ):
		return self.sequance

	def get_configuration ( self ):
		return self.configuration

	def get_space_configuration ( self ):
		if not self.space_configuration:
			self.compute_space_configuration()

		return self.space_configuration


	def get_count_of_hydro ( self ):
		count = 0

		for amino in self.sequance:
			if amino == HYDROPHOBILIC:
				count += 1

		return count

	def set_configuration ( self, new_config ):
		self.configuration = deepcopy ( new_config )

	def generate_random ( self ):
		"""
		Generate random valid sequance
		"""
		for i in range(len(self.sequance)-1):
			self.configuration.append(complex(1,0))

		RIGHT=True
		UP=False
		DOWN=False

		RIGHT_MOVE = complex ( 1, 0)
		DOWN_MOVE = complex ( 0, 1)
		UP_MOVE = complex ( 0, -1)

		CHANGE_DIRECTION_PROBABILITY = 0.7

		for config in range(len(self.configuration)):
			if RIGHT:
				change_of_direction = random.random()
				if change_of_direction < CHANGE_DIRECTION_PROBABILITY:
					direction = random.random()
					if direction < 0.5:
						self.configuration[config] = UP_MOVE
						RIGHT = False
						UP = True
					else:
						self.configuration[config] = DOWN_MOVE
						RIGHT = False
						DOWN = True
				else:
					self.configuration[config] = RIGHT_MOVE
					RIGHT = True
					UP = False
					DOWN = False

			elif UP:
				change_of_direction = random.random()
				if change_of_direction < CHANGE_DIRECTION_PROBABILITY:
					self.configuration[config] = RIGHT_MOVE
					RIGHT = True
					UP = False
					DOWN = False
				else:
					self.configuration[config] = UP_MOVE
					UP = True
					DOWN = False
					RIGHT = False
			elif DOWN:
				change_of_direction = random.random()
				if change_of_direction < CHANGE_DIRECTION_PROBABILITY:
					self.configuration[config]=RIGHT_MOVE
					RIGHT = True
					DOWN = False
					UP = False
				else:
					self.configuration[config] = DOWN_MOVE
					UP = False
					DOWN = True
					RIGHT = False

	def plot_config ( self, index=None ):
		"""
		Plot configuration of vector
		"""
		list_of_real = []
		list_of_imag = []

		list_of_hydrophobilic = []

		min_x, min_y = -1, -1
		max_x, max_y = 1, 1

		self.compute_space_configuration(index)

		# Init list of all points
		for space_config_item in self.space_configuration:
			list_of_real.append ( space_config_item.real )
			list_of_imag.append ( space_config_item.imag )

		fig = plt.figure()

		ax = fig.gca()
		plt.plot ( list_of_real, list_of_imag )

		if index != None:
			final_index = index+2
		else:
			final_index = len(self.sequance)

		# print ( list_of_real, list_of_imag)

		for index_of_amino in range(final_index):
			if self.sequance[index_of_amino] == HYDROPHOBILIC:
				plt.scatter ( list_of_real[index_of_amino], list_of_imag[index_of_amino], marker="o", color="red")
			else:
				plt.scatter ( list_of_real[index_of_amino], list_of_imag[index_of_amino], marker="o",color="blue")

		axis = self.get_axis()
		plt.axis(axis)

		ax.set_xticks(numpy.arange(axis[0],axis[1],1))
		ax.set_yticks(numpy.arange(axis[2],axis[3],1))
		
		plt.grid()

		plt.show()

	def get_axis ( self ):
		min_x, min_y = -1, -1
		max_x, max_y = 1, 1
		for space_config_item in self.space_configuration:
			if min_x > space_config_item.real:
				min_x = space_config_item.real
			elif max_x < space_config_item.real:
				max_x = space_config_item.real

			if min_y > space_config_item.imag:
				min_y = space_config_item.imag
			elif max_y < space_config_item.imag:
				max_y = space_config_item.imag

		return min_x-1, max_x+1, min_y-1, max_y+1

	def compute_space_configuration ( self, index=None ):
		"""
		Compute space configuration of sequance up to index or to the end
		"""
		# Init array with space configuration
		self.space_configuration = []
		self.space_configuration.append(complex(0,0))

		sum_of_space_config = complex ( 0, 0)

		if index:
			final_index = index+1
		else:
			final_index = len(self.configuration)

		for index in range(0,final_index):
			real = sum_of_space_config.real + self.configuration[index].real
			imag = sum_of_space_config.imag + self.configuration[index].imag

			sum_of_space_config = complex ( real, imag )

			self.space_configuration.append ( sum_of_space_config )

		if self.verbose:
			print ( "Space configuration: ", self.space_configuration )


		self.space_configuration_counter = Counter ( self.space_configuration )

		return self.space_configuration

	def compute_free_energy ( self, index=None ):
		"""
		Compute free energy of configuration up to index
		"""
		free_energy = 0
		self.compute_space_configuration ( index )

		final_index_of_amino = None
		if index == None:
			final_index_of_amino = len(self.sequance)-1
		else:
			final_index_of_amino = index+1


		# Iterate all amino
		for first in range ( 0, final_index_of_amino ):
			# Check if amino is hydropohoboli ( free energy is depedent on it )
			if self.sequance[first] == HYDROPHOBILIC:
				# Iterate amino to end of protein
				for second in range ( first+1, final_index_of_amino+1 ):
					# Check if amino is hydropohoboli ( free energy is depedent on it )
					if self.sequance[second] == HYDROPHOBILIC:
						# Add to free energy ( absolute value of two complex numbers)
						energy = self.length_between_amino(self.space_configuration[first],self.space_configuration[second])
				
						free_energy += energy
		if self.verbose:
			print ("Free energy: ", free_energy)
			
		if free_energy == 0:
			return 1

		return free_energy

if __name__ == "__main__":
	vector = Vector ( [ 1, 1, 1, 1, 1 ] )
	UP = complex (0, 1)
	DOWN = complex (0, -1)
	LEFT = complex (-1,0)
	RIGHT = complex (1,0)

	directions = [ UP, DOWN, LEFT, RIGHT ]

	vector.set_configuration_at_index(0, UP )
	print(vector)
	space_config = vector.compute_space_configuration(0)
	free_energy = vector.compute_free_energy(0)
	print("Space configuration: ", space_config)
	print("Free energy: ", free_energy, " ( 1 )")	
	vector.plot_config(0)

	print("Param: ", vector.compute_space_configuration(3) )
	print("NoParam: ", vector.compute_space_configuration() )
	print("Param: ", vector.compute_free_energy(3) )
	print("NoParam: ", vector.compute_free_energy() )
	print(len(vector.get_amino_sequance())-1)
	for index_of_config in range(1, len(vector.get_amino_sequance())-1):
		print(" ================= Index: ", index_of_config, " ============= " )

		min_of_free_energy = 100000000
		min_index = 0
		counter = 0

		for direction in directions:
			vector.set_configuration_at_index ( index_of_config, direction )
			print(vector)
			space_config = vector.compute_space_configuration(index_of_config)
			free_energy = vector.compute_free_energy(index_of_config)

			invalid = False
			counter_config = Counter ( space_config )
			for key in counter_config:
				if counter_config[key] > 1:
					invalid = True

			if not invalid:
				if free_energy < min_of_free_energy:	
					min_index = counter
					min_of_free_energy = free_energy

			print("Space configuration: ", space_config)
			print("Free energy: ", free_energy)
			print("Validity: ", not invalid)

			vector.plot_config(index_of_config)

			counter += 1

		print ("Minimal free energy: ", min_of_free_energy)
		print ("Direction: ", min_index)

		vector.set_configuration_at_index(index_of_config, directions[min_index] )

		print(vector.compute_free_energy(index_of_config))
		vector.plot_config(index_of_config)
		print ( " ============ ")

	print("Space configuration: ", vector.compute_space_configuration() )

	print("Free energy: ", vector.compute_free_energy() )
	print(vector)
	vector.plot_config()