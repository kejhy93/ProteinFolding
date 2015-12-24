#! /usr/bin/python3

from collections import *
# import matplotlib.pyplot as plt
import random
from copy import deepcopy

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
		# for i in range(len(self.sequance)-1):
		# 	self.configuration.append ( complex (0,1))

		self.generate_random()

		self.free_energy = -1
		self.space_configuration = []

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

	def compute_space_configuration ( self ):
		"""
		Compute space configuration of sequance
		"""
		# Init array with space configuration
		self.space_configuration = []
		self.space_configuration.append ( 0 )

		sum_of_space_config = complex ( 0, 0)

		for index in range(0,len(self.configuration)):
			real = sum_of_space_config.real + self.configuration[index].real
			imag = sum_of_space_config.imag + self.configuration[index].imag

			sum_of_space_config = complex ( real, imag )

			self.space_configuration.append ( sum_of_space_config )

		if self.verbose:
			print ( "Space configuration: ", self.space_configuration )
		return self.space_configuration

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
		counter = Counter ( self.space_configuration )

		for key in counter:
			if counter[key] > 1:
				return NOT_VALID_CONFIGURATION

		return VALID_CONFIGURATION

	def compute_free_energy ( self ):
		"""
		Compute free energy
		"""
		free_energy = 0
		# Get space configuration
		self.compute_space_configuration()

		# Iterate all amino
		for index in range ( len(self.sequance)):
			# Check if amino is hydropohoboli ( free energy is depedent on it )
			if self.sequance[index] == HYDROPHOBILIC:
				# Iterate amino to end of protein
				for rest_of_amino_index in range ( index+1, len(self.sequance)):
					# Check if amino is hydropohoboli ( free energy is depedent on it )
					if self.sequance[rest_of_amino_index] == HYDROPHOBILIC:
						# Add to free energy ( absolute value of two complex numbers)
						free_energy += self.length_between_amino ( self.space_configuration[index], self.space_configuration[rest_of_amino_index])

		if self.verbose:
			print ("Free energy: ", free_energy)

		return free_energy

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

	def set_configuration ( self, new_config ):
		self.configuration = deepcopy ( new_config )

	def generate_random ( self ):
		for i in range(len(self.sequance)-1):
			self.configuration.append(complex(1,0))

		RIGHT=True
		UP=False
		DOWN=False

		for config in self.configuration:
			if RIGHT:
				change_of_direction = random.random()
				if change_of_direction < 0.3:
					direction = random.random()
					if direction < 0.5:
						config = complex(0,1)
						RIGHT = False
						UP = True
					else:
						config = complex(0,-1)
						RIGHT = False
						DOWN = True
				else:
					config = complex(1,0)
					RIGHT = True
					UP = False
					DOWN = False

			elif UP:
				change_of_direction = random.random()
				if change_of_direction < 0.3:
					config = complex(1,0)
					RIGHT = True
					UP = False
					DOWN = False
				else:
					config = complex(0,1)
					UP = True
					DOWN = False
					RIGHT = False
			elif DOWN:
				change_of_direction = random.random()
				if change_of_direction < 0.3:
					config=complex(1,0)
					RIGHT = True
					DOWN = False
					UP = False
				else:
					config = complex(0,-1)
					UP = True
					DOWN = False
					RIGHT = False




	def plot_config( self ):
		"""
		Plot configuration of vector
		"""
		list_of_real = []
		list_of_imag = []

		list_of_hydrophobilic = []

		min_x, min_y = -1, -1
		max_x, max_y = 1, 1

		# Init list of all points
		for space_config_item in self.space_configuration:

			if min_x > space_config_item.real:
				min_x = space_config_item.real
			elif max_x < space_config_item.real:
				max_x = space_config_item.real

			if min_y > space_config_item.imag:
				min_y = space_config_item.imag
			elif max_y < space_config_item.imag:
				max_y = space_config_item.imag

			list_of_real.append ( space_config_item.real )
			list_of_imag.append ( space_config_item.imag )


		plt.figure()

		plt.plot ( list_of_real, list_of_imag )

		for index_of_amino in range(len(self.sequance)):
			if self.sequance[index_of_amino] == HYDROPHOBILIC:
				plt.scatter ( list_of_real[index_of_amino], list_of_imag[index_of_amino], marker="o", color="red")
			else:
				plt.scatter ( list_of_real[index_of_amino], list_of_imag[index_of_amino], marker="o",color="blue")


		plt.axis([min_x-1,max_x+1, min_y-1, max_y+1])
		plt.show()