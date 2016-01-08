#! /usr/bin/python3

from copy import deepcopy
import random
from math import exp

from multiprocessing.dummy import Pool as ThreadPool 
import itertools

import utils

from abstract_solver import AbstractSolver

from population import Population
from individual import Individual

from mutation import do_mutation
from crossover import do_crossover
from hill_climbing import do_hill_climbing
from simulated_annealing import do_simulated_annealing


from ant_colony import AntColony

NOT_VALID_CONFIGURATION = False
VALID_CONFIGURATION = True

# MUTATION
MUTATION_TYPE=(2/3)

# HILL CLIMBING
COUNT_OF_HILL_CLIMBING = 10
HILL_CLIMBING_COUNT_OF_NEIGHOUR = 12
HILL_CLIMBING_COUNT_OF_ITERATION = 5

# SIMULATED ANNEALING
COUNT_OF_SIMULATED_ANNEALING = 2
SIMULATED_ANNEALING_COOLING_RATE = 0.9
INITAL_TEMPERATURE=10000
MIN_TEMPERATURE = 1

# ANT-COLONY OPTIMISATION
COUNT_OF_ANT_COLONY = 50
COUNT_OF_ANTS = 8

class GeneticsAlgorithm ( AbstractSolver ):
	def __init__ ( self, sequance, MAX_GENERATION, POPULATION_SIZE, 
		COUNT_OF_MUTATION_PER_GENERATION, COUNT_OF_CROSSOVER_PER_GENERATION, 
		MUTATE_RATE, CROSSOVER_RATE ):

		self.MAX_GENERATION = MAX_GENERATION
		self.POPULATION_SIZE = POPULATION_SIZE

		self.FREQUANCY_OF_HILL_CLIMBING = (int)(MAX_GENERATION/COUNT_OF_HILL_CLIMBING)
		self.FREQUANCY_OF_SIMULATED_ANNEALING = (int)(MAX_GENERATION/COUNT_OF_SIMULATED_ANNEALING)
		self.FREQUANCY_OF_ANT_COLONY = (int)(MAX_GENERATION/COUNT_OF_ANT_COLONY)

		self.MUTATE_RATE = MUTATE_RATE
		self.CROSSOVER_RATE = CROSSOVER_RATE

		self.COUNT_OF_MUTATION_PER_GENERATION = COUNT_OF_MUTATION_PER_GENERATION
		self.COUNT_OF_CROSSOVER_PER_GENERATION = COUNT_OF_CROSSOVER_PER_GENERATION

		super().__init__(sequance)
		self.verboseGeneticsSolver = True

		if self.verboseGeneticsSolver:
			print("GeneticsAlgorithm -> init")

		self.counter_before_disaster = 0

		self.ant_colony = None

	def solve ( self ):
		if self.verboseGeneticsSolver:
			print ( "GeneticsAlgorithm -> solve" )

		# Create population
		population = Population ( self.POPULATION_SIZE )

		# Init population
		population.init_population ( self.result_vector )

		best_individual_of_population,average_fitness = population.pick_random_individual()
		energy_of_best_individual_of_population = 100000000

		if self.verboseGeneticsSolver:
			print ( " Init population: ", population)

		IS_MUTATION = True
		IS_CROSSOVER = True
		IS_HILL_CLIMBING = False
		IS_SIMULATED_ANNEALING = True
		IS_ANT_COLONY = True

		for iteration in range ( 1,self.MAX_GENERATION+1 ):
			iterationStr = ""
			iterationStr = "Iteration: " + str ( iteration ) + "\n"

			start_times = []
			end_times = []

			times = []
			methods = []

			start_times.append ( utils.get_time_in_millis() )
			# MUTATION
			if IS_MUTATION:
				print ( "GeneticsAlgorithm -> Mutation")
				self.mutate ( population, iteration )

			methods.append("Mutation")
			end_times.append(utils.get_time_in_millis())


			# CROSS-OVER
			start_times.append(utils.get_time_in_millis())

			crossover_probability = random.random()
			if IS_CROSSOVER and crossover_probability < self.CROSSOVER_RATE:
				print("GeneticsAlgorithm -> Crossover")
				population = self.do_crossover ( population, self.COUNT_OF_CROSSOVER_PER_GENERATION )
			methods.append ( "Crossover")
			end_times.append(utils.get_time_in_millis())


			# HILL-CLIMBING
			start_times.append( utils.get_time_in_millis() )

			if IS_HILL_CLIMBING:
				print ( "GeneticsAlgorithm -> Hill-Climbing")
				if iteration%self.FREQUANCY_OF_HILL_CLIMBING == 0:
					# Pick random individual from population
					parent,index_of_parent = population.pick_random_individual()
					# Hill-Climbing
					mutated_individual = do_hill_climbing ( parent,HILL_CLIMBING_COUNT_OF_ITERATION, HILL_CLIMBING_COUNT_OF_NEIGHOUR )
					# New individual to population
					population.set_individual_at(index_of_parent, mutated_individual)
			
			methods.append ( "Hill-Climbing")
			end_times.append(utils.get_time_in_millis())

			# SIMULATED ANNEALING
			start_times.append( utils.get_time_in_millis() )

			if IS_SIMULATED_ANNEALING:
				print ( "GeneticsAlgorithm -> Simulated Annealing")
				# Get random unique indexes of individuals
				index_of_individuals = random.sample(range(0, population.count_of_individuals()), COUNT_OF_SIMULATED_ANNEALING)

				# # Fill individuals
				individuals_to_simulated_annealing = []
				for index in index_of_individuals:
					individuals_to_simulated_annealing.append(population.get_individual_at(index) )
				
				# # Init thread pool
				simulated_annealing_pool = ThreadPool(8)
				# # Simulated Annealing
				results = simulated_annealing_pool.starmap ( do_simulated_annealing, zip ( individuals_to_simulated_annealing))
				# # Replace new individuals to population
				for mutated_individual,index in zip(results,index_of_individuals):
					population.set_individual_at(index, mutated_individual )	
				# Clear thread pool
				simulated_annealing_pool.close()

			methods.append ( "Simulated Annealing")

			end_times.append(utils.get_time_in_millis())

			# ANT-COLONY
			start_times.append( utils.get_time_in_millis() )

			if IS_ANT_COLONY:
				print("GeneticsAlgorithm -> Ant-Colony")
				population = self.do_ant_colony( population, iteration )

			methods.append ( "Ant-Colony")
			end_times.append(utils.get_time_in_millis())

			time_to_print = utils.get_string_of_computed_times ( start_times, end_times, methods )

			# Pick best individual from population and compare with best individual found
			best_individual_of_iteration,average_fitness = population.pick_best_individual ()

			energy_of_best_individual_of_iteration = best_individual_of_iteration.compute_free_energy()

			best_individual_of_population = self.get_best_individual ( best_individual_of_iteration, best_individual_of_population )

			iterationStr += "Energy of best individual: {:10.3f}, Average fitness: {:10.3f}".format(best_individual_of_population.get_free_energy(), average_fitness)
			# Print best individual
			if self.verboseGeneticsSolver:
				print(time_to_print)
				print ( iterationStr )
				# best_individual_of_population.get_individual().plot_config()

		return best_individual_of_population.get_individual()

	def mutate ( self, population, iteration ):
		index_of_individuals = random.sample(range(0, population.count_of_individuals()), self.COUNT_OF_MUTATION_PER_GENERATION)
		individuals_to_mutate = []
		mutation_pool = ThreadPool(4)

		for index in index_of_individuals:
			individuals_to_mutate.append(population.get_individual_at(index))

		results = mutation_pool.starmap ( do_mutation, zip ( individuals_to_mutate, itertools.repeat(self.MUTATE_RATE), itertools.repeat(iteration), itertools.repeat(self.MAX_GENERATION)))

		for mutated_individual,index in zip(results,index_of_individuals):
			population.set_individual_at(index, mutated_individual )

		mutation_pool.close()

	def get_best_individual ( self, best_iteration, best_population ):
		if best_iteration.get_free_energy() < best_population.get_free_energy():
			best_population = deepcopy ( best_iteration )
			best_population.compute_free_energy()

		return best_population

	def do_ant_colony ( self, population, iteration  ):
		"""
		Ant colony optimisation
		"""
		# if self.verboseGeneticsSolver:
		# 	print ("GeneticsAlgorithm -> Ant-Colony")

		if self.ant_colony == None:
			self.ant_colony = AntColony ( COUNT_OF_ANTS, self.sequance, iteration, self.MAX_GENERATION  )

		new_individuals = self.ant_colony.search ()

		population = self.replace_worst_individuals ( new_individuals, len(new_individuals), population )

		return population

	def replace_worst_individuals ( self, list_of_of_new_individuals, count_of_new, population ):
		"""
		Find n individuals with highest score and replace them with new individuals
		"""
		indexes_of_worst_individuals = population.find_worst_individuals ( count_of_new )

		for index in range(len(indexes_of_worst_individuals)):
			population.set_individual_at(indexes_of_worst_individuals[index],list_of_of_new_individuals[index] )
			population.get_individual_at(indexes_of_worst_individuals[index]).compute_free_energy()

		return population

	def generate_random ( self, individual ):
		individual = Individual ( self.sequance )

		return individual

	# CROSSOVER
	def do_crossover ( self, population, count_of_crossover ):
		"""
		Crossover
		"""
		for crossover_index in range(count_of_crossover):
			first_individual,first_index = population.pick_random_individual ()
			second_individual,second_index = population.pick_random_individual ()

			crossover_individuals = do_crossover ( first_individual, second_individual, self.CROSSOVER_RATE )

			if crossover_individuals[0] != first_individual:
				population.set_individual_at(first_index, crossover_individuals[0] )
			if crossover_individuals[1] != second_individual:
				population.set_individual_at ( second_index, crossover_individuals[1] )

		return population
