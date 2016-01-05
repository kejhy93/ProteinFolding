#! /usr/bin/python3

import random
from copy import deepcopy

from vector import Vector

from individual import Individual

SIZE_OF_CANDICATE_LIST=10

class Population:
	def __init__ ( self, size_of_population ):
		self.verbose = False

		if self.verbose:
			print("Create populatin")

		self.size_of_population = size_of_population

		self.individuals = []

	def count_of_individuals ( self ):
		return len(self.individuals)

	def init_population ( self, vector ):
		"""
		Init population
		"""
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

		candidate_list = self.generate_candidate_list()

		index = self.find_best_individual ( candidate_list )

		return self.individuals[index],index

	def generate_candidate_list ( self ):
		"""
		Generate list of candidates before select
		"""
		candidate_list = []
		for candicate in range ( SIZE_OF_CANDICATE_LIST ):
			candidate_list . append ( random.randint( 0, self.size_of_population-1 ) )

		return candidate_list

	def find_best_individual ( self, candidate_list ):
		"""
		Find solution with lowest score
		"""
		best_index = -1
		best_score = 10000000

		for candicate in candidate_list:
			energy_of_individual = self.individuals[candicate].get_free_energy()
			if energy_of_individual < best_score:
				best_score = energy_of_individual
				best_index = candicate

		return best_index

	def find_worst_individuals ( self, count ):
		"""
		Find worst individuals
		"""
		list_of_values = []
		list_of_index = []

		for i in range(count):
			list_of_values.append(i)
			list_of_index.append(i)

		counter = 0
		for individual in self.individuals:
			exist,index =  self.exist_lower_value_in ( individual.get_free_energy(), list_of_values )
			if exist:
				list_of_index,list_of_values = self.move ( list_of_index,list_of_values, index, counter, individual.get_free_energy()  )

			counter += 1

		return list_of_index

	def exist_lower_value_in ( self, val, list_of_values ):
		for index in range(len(list_of_values)):
			if list_of_values[index] < val:
				return True,index
		return False,-1

	def move ( self,list_of_index,list_of_values, index, new_index,new_value ):
		for idx in range (len(list_of_values)-1, index, -1):
			list_of_values[idx] = list_of_values[idx-1]
			list_of_index[idx] = list_of_index[idx-1]

		list_of_values[index] = new_value
		list_of_index[index] = new_index

		return list_of_index,list_of_values

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
			res += "Individual " + str(index_of_individual+1) + ": " + str(self.individuals[index_of_individual]) + "\n"

		return res

if __name__ == "__main__":
	sequance = Vector([0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0])

	pop = Population(15)
	pop.init_population(sequance)

	list_of_worst_index, list_of_worst_value = pop.find_worst_individuals(5)

	print("Worst indi: ", list_of_worst_index)
	print("Worst indi: ", list_of_worst_value)

	print(pop)