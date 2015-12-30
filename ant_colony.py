#! /usr/bin/python3

import random
from copy import deepcopy

from ant import Ant

from mutation import do_mutation

EVAPORATE_CONSTANT = 0.4

STRAIGHT=0
LEFT=1
RIGHT=2

DIRECTIONS = [ STRAIGHT, LEFT, RIGHT ]

class AntColony:
	def __init__ ( self, count_of_ants, sequance ):
		self.verbose = False

		if self.verbose:
			print ( "Ant Colony -> Init")

		self.COUNT_OF_ANTS = count_of_ants
		self.ants = []
		self.sequance = sequance
		for ant_index in range ( self.COUNT_OF_ANTS ):
			self.ants . append ( Ant(ant_index, sequance ))

		self.pheronome = []

		self.pheronome = self.init_pheronome_trails ()

	def init_pheronome_trails ( self ):
		"""
		Init pheronome trails
		"""
		pheronome = []
		for index in range(len(self.sequance)-1):
			pheronome.append ( [self.init_pheronome(), self.init_pheronome(), self.init_pheronome()] )

		return pheronome

	def init_pheronome ( self ):
		"""
		Init pheronome
		"""
		return random.random()/100
		# return 1.0

	def search ( self ):
		"""
		Create new solution by ant 
		"""
		new_individuals = []
		tabu_lists = []
		for ant in self.ants:
			new_individual,tabu_list = ant.search( self.pheronome )

			new_individuals.append(new_individual)
			tabu_lists.append (tabu_list )


		mutated_individuals = []
		for individual in new_individuals:
			mutated_individuals.append ( do_mutation(individual ))


		self.update_pheronome_trails ( new_individuals, tabu_lists )
		# print("Individuals from ant: ",new_individuals)

		# for individual in mutated_individuals:
		# 	print(individual.get_individual())
		# 	individual.get_individual().plot_config()

		return mutated_individuals

	def update_pheronome_trails ( self, new_individuals, tabu_lists ):
		if self.verbose:
			print ( "AntColony -> Update pheronome trails")

		delta_pheronome = self.compute_delta_pheronome ( new_individuals, tabu_lists )

		for index_of_pheronome in range(1,len(self.pheronome)):
			new_pheronome = self.pheronome[index_of_pheronome]

			# Evaporate
			# print(len(new_pheronome))
			for index_of_pher in range(len(DIRECTIONS)):
				new_pheronome[index_of_pher] *= EVAPORATE_CONSTANT
				new_pheronome[index_of_pher] += delta_pheronome[index_of_pheronome-1][index_of_pher]

			self.pheronome[index_of_pheronome]=new_pheronome


	def compute_delta_pheronome ( self, individuals, tabu_lists ):
		if self.verbose:
			print ( "AntColony -> Update pheronome trails -> Compute Delta Pheronome")
		delta = []

		for index in range(1,len(self.pheronome)):
			deltas = []
			for direction in DIRECTIONS:
				for tabu_list,individual in zip(tabu_lists,individuals):
					# print(index,len(tabu_list))
					if tabu_list[index-1] == direction:
						deltas.append(100/individual.get_free_energy() )
					else:
						deltas.append ( 0 )
			delta.append(deltas)

		# print(len(delta))
		return delta
