#! /usr/bin/python3

import random
from copy import deepcopy

from ant import Ant

from mutation import do_mutation
from hill_climbing import do_hill_climbing

EVAPORATE_CONSTANT = 0.4

STRAIGHT=0
LEFT=1
RIGHT=2

DIRECTIONS = [ STRAIGHT, LEFT, RIGHT ]

MULT_TO_STRAIGHT = complex(1,0)
MULT_TO_LEFT = complex(0,1)
MULT_TO_RIGHT = complex(0,-1)

MULTIPLY = [ MULT_TO_STRAIGHT, MULT_TO_LEFT, MULT_TO_RIGHT]

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
		return random.random()/1000
		# return 1.0

	def search ( self ):
		"""
		Create new solution by ant 
		"""
		new_individuals = []
		tabu_lists = []
		for ant in self.ants:
			print("AntColony -> Ant ", ant.get_id()+1 , ": ")
			new_individual,tabu_list = ant.search( self.pheronome )

			if new_individual != None:
				new_individuals.append(new_individual)
				tabu_lists.append (tabu_list )



		# for individual in new_individuals:
		# 	print(individual.get_individual())
		# 	individual.get_individual().plot_config()

		mutated_individuals = []
		counter = 0

		print("AntColony -> Hill-climbing")
		for individual,tabu_list in zip(new_individuals,tabu_lists):
			mutated_individuals.append ( do_hill_climbing ( individual ) )
			if mutated_individuals != individual:
				tabu_lists[counter] = self.update_tabu_list ( individual, tabu_list )

			counter += 1


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

	def update_tabu_list ( self, individual, tabu_list ):
		new_tabu_list = []

		vector = individual.get_individual()
		configuration = vector.get_configuration()
		# print(len(tabu_list))

		new_tabu_list.append(STRAIGHT)


		for index_of_config in range(1,len(configuration)):
			last_coord = configuration[index_of_config-1]
			current_coord = configuration[index_of_config]

			if current_coord == last_coord*MULT_TO_STRAIGHT:
				new_tabu_list.append(STRAIGHT)
			elif current_coord == last_coord*MULT_TO_LEFT:
				new_tabu_list.append(LEFT)
			elif current_coord == last_coord*MULT_TO_RIGHT:
				new_tabu_list.append(RIGHT)

		# print(len(new_tabu_list))

		return new_tabu_list


