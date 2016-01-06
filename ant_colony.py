#! /usr/bin/python3

import random
from copy import deepcopy

from multiprocessing.dummy import Pool as ThreadPool 
import itertools

from ant import Ant

from mutation import do_mutation
from hill_climbing import do_hill_climbing
from simulated_annealing import do_simulated_annealing

EVAPORATE_CONSTANT = 0.3

# PARAMETERS FOR LOCAL SEARCH
SIMULATED_ANNEALING_COOLING_RATE = 0.5

HILL_CLIMBING_COUNT_OF_ITERATION = 5
HILL_CLIMBING_COUNT_OF_NEIGHBOUR = 5


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
		return random.random()
		# return 1.0

	def search ( self ):
		"""
		Create new solution by ant 
		"""

		for ant_index in range ( self.COUNT_OF_ANTS ):
			self.ants . append ( Ant(ant_index, self.sequance, self.pheronome ))

		new_individuals = []
		tabu_lists = []
		# for ant in self.ants:
			# print("AntColony -> Ant ", ant.get_id()+1 , ": Started")

			# Single-threaded
			# new_individual,tabu_list = ant.search( self.pheronome )
			# if new_individual != None:
				# new_individuals.append(new_individual)
				# tabu_lists.append (tabu_list )

			# Multi-threaded

		for ant in self.ants:
			ant.start()

		for ant in self.ants:
			ant.join()
			# print("AntColony -> Ant ", ant.get_id()+1 , ": Terminated")
			new_individuals.append( ant.get_individual() )
			tabu_lists.append( ant.get_tabu_list() )

		# for individual in new_individuals:
		# 	print(individual.get_individual())
		# 	individual.get_individual().plot_config()

		results = []
		counter = 0


		if self.verbose:
			print("Ant-Colony -> Local search")

		results,tabu_lists = self.local_search ( new_individuals, tabu_lists )

		# Update pheronome trails
		self.update_pheronome_trails ( results, tabu_lists )
		# self.update_pheronome_trails ( new_individuals, tabu_lists )


		return results
		# return new_individuals

	def local_search ( self, individuals, tabu_lists ):
		print("AntColony -> Local Search")
		counter = 0

		index_to_delete = []
		for index in range(len(individuals)):
			if individuals[index] == None:
				index_to_delete.append(index)

		if len(index_to_delete) != 0:
			for index in range(len(index_to_delete),0,-1):
				del individuals[index_to_delete[index-1]]
				del tabu_lists[index_to_delete[index-1]]

		# Multi-threaded
		pool = ThreadPool ( 8 )

		local_search_method_probability = random.random()
		if local_search_method_probability < 0.01:
			print ( "\tAnt-Colony -> Simulated Annealing")
			results = pool.starmap(do_simulated_annealing, zip(individuals, itertools.repeat(SIMULATED_ANNEALING_COOLING_RATE) ) )
		else:
			print ( "\tAnt-Colony -> Hill-Climbing")
			results = pool.starmap(do_hill_climbing, zip(individuals, itertools.repeat(HILL_CLIMBING_COUNT_OF_NEIGHBOUR), itertools.repeat(HILL_CLIMBING_COUNT_OF_ITERATION)))


		for index in range(len(results)):
			if results[index] == None:
				del tabu_lists[index]

		for mutated, original,tabu_list in zip(results,individuals,tabu_lists):
			if mutated != original and mutated != None:
				tabu_lists[counter] = self.update_tabu_list ( mutated, tabu_list )

			counter += 1

		pool.close()

		return results,tabu_lists

	def update_pheronome_trails ( self, new_individuals, tabu_lists ):
		if self.verbose:
			print ( "AntColony -> Update pheronome trails")

		delta_pheronome = self.compute_delta_pheronome ( new_individuals, tabu_lists )

		for index_of_pheronome in range(1,len(self.pheronome)):
			new_pheronome = self.pheronome[index_of_pheronome]

			# Evaporate
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
					if index >= len(tabu_list):
						tabu_list.append(STRAIGHT)

					if tabu_list[index-1] == direction:
						deltas.append(100/individual.get_free_energy() )
					else:
						deltas.append ( 0 )
			delta.append(deltas)

		return delta

	def update_tabu_list ( self, individual, tabu_list ):
		new_tabu_list = []

		vector = individual.get_individual()
		configuration = vector.get_configuration()

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

		return new_tabu_list


