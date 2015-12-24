#! /usr/bin/python3

import random
from copy import deepcopy

from vector import Vector

from individual import Individual

class Population:
	def __init__ ( self, size_of_population ):
		self.verbose = False

		if self.verbose:
			print("Create populatin")

		self.size_of_population = size_of_population

		self.individuals = []

	def init_population ( self, vector ):
		if self.verbose:
			print ( "Init of population" )
		for index_of_individual in range(self.size_of_population):
			indi = Individual ( vector.get_amino_sequance() )
			indi.compute_free_energy()
			
			self.individuals.append ( indi )

	def pick_random_individual ( self ):
		"""
		Return random individual 
		"""
		index = random.randint( 0, self.size_of_population-1 )

		return self.individuals[index],index

	def set_individual_at ( self, index, new_individual ):
		self.individuals[index] = deepcopy ( new_individual )

	def get_individual_at ( self, index ):
		return self.individuals[index]
		
	def pick_best_individual ( self ):
		"""
		Return best individual
		"""
		min_energy,index = None,0
		sum_energy = 0

		for index_of_individual in range(len(self.individuals)):
			energy = self.individuals[index_of_individual].get_free_energy()
			sum_energy += energy

			if not min_energy:
				min_energy = energy
				index = index_of_individual

			if min_energy > energy:
				min_energy = energy
				index = index_of_individual

		return self.individuals[index], sum_energy/self.size_of_population

	def __str__ ( self ):
		if self.verbose:
			print ( "Print population")

		res = ""
		for index_of_individual in range(len(self.individuals)):
			res += "Individual " + str(index_of_individual) + ": " + str(self.individuals[index_of_individual]) + "\n"

		return res