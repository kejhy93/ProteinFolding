#! /usr/bin/python3

import random
from copy import deepcopy

from multiprocessing.dummy import Pool as ThreadPool 
import itertools

from ant import Ant

from mutation import do_mutation
from hill_climbing import do_hill_climbing
from simulated_annealing import do_simulated_annealing

# ANT-COLONY PARAMETERS
EVAPORATE_CONSTANT = 0.3
DELTA_PHERONOME_CONSTANT = 1000

# PARAMETERS FOR LOCAL SEARCH
SIMULATED_ANNEALING_COOLING_RATE = 0.8

HILL_CLIMBING_COUNT_OF_ITERATION = 15
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
	def __init__ ( self, count_of_ants, sequance, iteration, max_iteration ):
		self.verbose = False

		if self.verbose:
			print ( "\tAnt Colony -> Init")

		self.COUNT_OF_ANTS = count_of_ants
		self.ants = []
		self.sequance = sequance

		self.pheronome = []

		self.pheronome = self.init_pheronome_trails ()

		self.heuristic_val, self.pheronome_val = self.update_heuristic_pheronome_value ( iteration, max_iteration )

	def init_ants ( self ):
		self.ants = []

	def update_heuristic_pheronome_value ( self, iteration, max_iteration ):
		if iteration < (1/5)*max_iteration:
			return 10,1
		elif iteration < (2/5)*max_iteration:
			return 6,3
		elif iteration < (3/5)*max_iteration:
			return 5,4
		else:
			return 4,4

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

	def search ( self ):
		"""
		Create new solution by ant 
		"""
		self.init_ants()
		if self.verbose:
			print ( "\tAnt-Colont -> Ant's search")
			# print ( "Pheronome: ")
			# for i in self.pheronome:
				# print(i)

		for ant_index in range ( self.COUNT_OF_ANTS ):
			self.ants . append ( Ant(ant_index, self.sequance, self.pheronome, self.heuristic_val, self.pheronome_val ))

		new_individuals = []
		tabu_lists = []

		# Multi-threaded
		for ant in self.ants:
			ant.start()

		for ant in self.ants:
			ant.join()

			new_individual = ant.get_individual()
			if self.check_valid_of_new_individual ( new_individuals ):
				# Remove invalid individuals
				new_individuals.append( ant.get_individual() )
				tabu_lists.append( ant.get_tabu_list() )

		results = []
		counter = 0

		# new_individuals[0].get_individual().plot_config()

		if self.verbose:
			print("\tAnt-Colony -> Local search")

		# Local search
		results,tabu_lists = self.local_search ( new_individuals, tabu_lists )

		# Update pheronome trails
		validIndividuals = self.check_valid_of_new_individuals ( results )

		# if validIndividuals:
		self.update_pheronome_trails ( results, tabu_lists )
		# self.update_pheronome_trails ( new_individuals, tabu_lists )


		return results
		# return new_individuals

	def check_valid_of_new_individual ( self, individual ):
		if individual == None:
			return False
		else:
			return True

	def check_valid_of_new_individuals ( self, results ):
		valid = False
		for result in results:
			if result != None:
				valid = True
		return valid

	def local_search ( self, individuals, tabu_lists ):
		if self.verbose:
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
		if local_search_method_probability < 0.5:
			if self.verbose:
				print ( "\tAnt-Colony -> Simulated Annealing")
			results = pool.starmap(do_simulated_annealing, zip(individuals, itertools.repeat(SIMULATED_ANNEALING_COOLING_RATE) ) )
		else:
			if self.verbose:
				print ( "\tAnt-Colony -> Hill-Climbing")
			results = pool.starmap(do_hill_climbing, zip(individuals, itertools.repeat(HILL_CLIMBING_COUNT_OF_NEIGHBOUR), itertools.repeat(HILL_CLIMBING_COUNT_OF_ITERATION)))


		for index in range(len(results)):
			if results[index] == None:
				del tabu_lists[index]
				del individuals[index]

		for mutated, original,tabu_list in zip(results,individuals,tabu_lists):
			if mutated != original and mutated != None:
				tabu_lists[counter] = self.update_tabu_list ( mutated, tabu_list )

			counter += 1

		pool.close()

		return results,tabu_lists

	def update_pheronome_trails ( self, new_individuals, tabu_lists ):
		"""
		Update pheronomes
		"""
		if self.verbose:
			print ( "\tAntColony -> Update pheronome trails")

		# Compute delta pheronome
		delta_pheronome = self.compute_delta_pheronome ( new_individuals, tabu_lists )

		# print("Delta pheronome: ")
		# for i in delta_pheronome:
			# print(i)

		for index_of_pheronome in range(1,len(self.pheronome)):
			# new_pheronome = self.pheronome[index_of_pheronome]

			for index_of_pher in DIRECTIONS:
				self.pheronome[index_of_pheronome][index_of_pher] *= EVAPORATE_CONSTANT
				self.pheronome[index_of_pheronome][index_of_pher] += delta_pheronome[index_of_pheronome-1][index_of_pher]

				# self.pheronome[index_of_pheronome][index_of_pher] = new_pheronome[index_of_pher]

			# print(self.pheronome[index_of_pheronome], new_pheronome)
			# self.pheronome[index_of_pheronome] = new_pheronome
			# print("After: ",self.pheronome[index_of_pheronome], new_pheronome)

	def compute_delta_pheronome ( self, individuals, tabu_lists ):
		if self.verbose:
			print ( "\tAntColony -> Update pheronome trails -> Compute Delta Pheronome")
		delta = []

		for index in range(1,len(self.pheronome)):
			deltas = [0,0,0]
			for direction in DIRECTIONS:
				for tabu_list,individual in zip(tabu_lists,individuals):
					# if index >= len(tabu_list):
					# 	tabu_list.append(STRAIGHT)

					if tabu_list[index] == direction:
						# deltas.append(DELTA_PHERONOME_CONSTANT/individual.get_free_energy() )
						DELTA = DELTA_PHERONOME_CONSTANT/individual.get_free_energy()

						# print(tabu_list[index-1], direction, DELTA)
						deltas = self.add_to_delta_pheronome ( deltas, direction, DELTA )
						# print(deltas)
					else:
						# deltas.append ( 0 )
						deltas = self.add_to_delta_pheronome ( deltas, direction, 0 )
			delta.append(deltas)

		return delta

	def add_to_delta_pheronome ( self, deltas, direction, new_record ):
		# print(direction)
		# print(len(deltas), direction)
		# print("Delta before: ", deltas[direction])
		# print(new_record)
		deltas[direction] += new_record
		# print("Delta after: ", deltas[direction])

		return deltas

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


