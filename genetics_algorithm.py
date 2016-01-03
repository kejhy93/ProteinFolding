#! /usr/bin/python3

from copy import deepcopy
import random
from math import exp

import utils

from abstract_solver import AbstractSolver

from population import Population
from individual import Individual

from mutation import do_mutation
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
HILL_CLIMBING_COUNT_OF_ITERATION = 12

# SIMULATED ANNEALING
COUNT_OF_SIMULATED_ANNEALING = 15
SIMULATED_ANNEALING_COOLING_RATE = 0.95
INITAL_TEMPERATURE=10000
MIN_TEMPERATURE = 1

# ANT-COLONY OPTIMISATION
COUNT_OF_ANT_COLONY = 20
COUNT_OF_ANTS = 10

class GeneticsAlgorithm ( AbstractSolver ):
	def __init__ ( self, sequance, MAX_GENERATION, POPULATION_SIZE, 
		COUNT_OF_MUTATION_PER_GENERATION, COUNT_OF_CROSSOVER_PER_GENERATION, 
		MUTATE_RATE, CROSSOVER_RATE ):

		self.MAX_GENERATION = MAX_GENERATION
		self.POPULATION_SIZE = POPULATION_SIZE

		self.FREQUANCY_OF_HILL_CLIMBING = (int)(MAX_GENERATION/COUNT_OF_HILL_CLIMBING)
		self.FREQUANCY_OF_SIMULATED_ANNEALING= (int)(MAX_GENERATION/COUNT_OF_SIMULATED_ANNEALING)
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

		for iteration in range ( 1,self.MAX_GENERATION+1 ):
			iterationStr = ""
			iterationStr = "Iteration: " + str ( iteration ) + "\n"

			# MUTATION
			# print ( "GeneticsAlgorithm -> Mutation")
			# for i in range(self.COUNT_OF_MUTATION_PER_GENERATION):
			# 	parent,index_of_parent = population.pick_random_individual()
			# 	mutated_individual = do_mutation( parent, self.MUTATE_RATE, iteration, self.MAX_GENERATION )

			# 	population.set_individual_at(index_of_parent, mutated_individual)

			# CROSS-OVER
			# population = self.do_crossover ( population )

			# HILL-CLIMBING
			# print ( "GeneticsAlgorithm -> Hill-Climbing")
			# if iteration%self.FREQUANCY_OF_HILL_CLIMBING == 0:
			# 	# Pick random individual from population
			# 	parent,index_of_parent = population.pick_random_individual()
			# 	# Hill-Climbing
			# 	mutated_individual = do_hill_climbing ( parent,HILL_CLIMBING_COUNT_OF_ITERATION, HILL_CLIMBING_COUNT_OF_NEIGHOUR )
			# 	# New individual to population
			# 	population.set_individual_at(index_of_parent, mutated_individual)

			# SIMULATED ANNEALING
			# if iteration%self.FREQUANCY_OF_SIMULATED_ANNEALING == 0:
			# 	print ( "GeneticsAlgorithm -> Simulated Annealing")
			# 	# Pick random individual from population
			# 	parent,index_of_parent = population.pick_random_individual()
			# 	# Simulated annealing
			# 	mutated_individual = do_simulated_annealing ( parent )
			# 	# New individual to population
			# 	population.set_individual_at(index_of_parent, mutated_individual)

			start_ant_colony = utils.get_time_in_millis ()

			# ANT-COLONY
			# if iteration%self.FREQUANCY_OF_ANT_COLONY == 0:
			# 	population = self.do_ant_colony( population )	

			population = self.do_ant_colony( population )

			end_ant_colony = utils.get_time_in_millis ()	

			time_in_ant_colony = end_ant_colony-start_ant_colony;

			print("Time in Ant Colony: ", utils.millis_to_second(time_in_ant_colony), " sec" )

			# Pick best individual from population and compare with best individual found
			best_individual_of_iteration,average_fitness = population.pick_best_individual ()

			energy_of_best_individual_of_iteration = best_individual_of_iteration.compute_free_energy()

			best_individual_of_population = self.get_best_individual ( best_individual_of_iteration, best_individual_of_population )

			iterationStr += "Energy of best individual: {:10.3f}, Average fitness: {:10.3f}".format(best_individual_of_population.get_free_energy(), average_fitness)
			# Print best individual
			if self.verboseGeneticsSolver:
				print ( iterationStr )
				# if iteration%25 == 0:
				# 	best_individual_of_population.get_individual().plot_config()

		return best_individual_of_population.get_individual()

	def get_best_individual ( self, best_iteration, best_population ):
		if best_iteration.get_free_energy() < best_population.get_free_energy():
			best_population = deepcopy ( best_iteration )
			best_population.compute_free_energy()

		return best_population

	def do_ant_colony ( self, population ):
		"""
		Ant colony optimisation
		"""
		if self.verboseGeneticsSolver:
			print ("GeneticsAlgorithm -> Ant-Colony")

		ant_colony = AntColony ( COUNT_OF_ANTS, self.sequance  )

		new_individuals = ant_colony.search ()

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
	def do_crossover ( self, population ):
		"""
		Main method for crossover

		Return crossovered population
		"""
		if self.verboseGeneticsSolver:
			print ( "GeneticsAlgorithm -> crossover")

		for i in range(self.COUNT_OF_CROSSOVER_PER_GENERATION):
			# Pick two random individual
			first_individual, first_index = population.pick_random_individual()
			second_individual, second_index = population.pick_random_individual()

			while second_index == first_index:
				second_individual, second_index = population.pick_random_individual()

			# Crossover two individual
			crossover_probability = random.random()

			if crossover_probability < self.CROSSOVER_RATE:
				first_crossover_point = random.randint ( 0, len(first_individual.get_configuration()))
				crossover_first_individual,crossover_second_individual = self.crossover ( first_individual, second_individual, first_crossover_point )

				# Compute free energy of crossovered individuals
				energy_of_first_crossover_individual = crossover_first_individual.compute_free_energy ()
				energy_of_second_crossover_individual = crossover_second_individual.compute_free_energy ()

				# Compute free energy of original indivudals
				energy_of_first_individual = first_individual.compute_free_energy()
				energy_of_second_individual = second_individual.compute_free_energy()

				# If free energy of crosovered individual is lower then original replace him
				if energy_of_first_individual > energy_of_first_crossover_individual:
					if crossover_first_individual.check_valid_configuration():
						first_individual = deepcopy ( crossover_first_individual )
						first_individual.compute_free_energy()
						population.set_individual_at ( first_index, first_individual )

				# If free energy of crosovered individual is lower then original replace him
				if energy_of_second_individual > energy_of_second_crossover_individual:
					if crossover_second_individual.check_valid_configuration():
						second_individual = deepcopy ( crossover_second_individual )
						second_individual.compute_free_energy()
						population.set_individual_at ( second_index, second_individual )

		return population

	def crossover ( self, first_individual, second_individual, first_crossover_point=-1, second_crossover_point=-1 ):
		"""
		Crossover two random individuals

		first_crossover_point = second_crossover_point = -1 -> swap every odd index
		first_crossover_point = second_crossover_point != -1 ||
		first_crossover_point != -1 && second_crossover_point == -1 -> Swap every index from first_crossover_point to end

		first_crossover_point != second_crossover_point 
		return tuple of two crossovered individuals
		"""
		crossover_first_individual = deepcopy ( first_individual )
		crossover_second_individual = deepcopy ( second_individual )

		if self.check_every_odd_index_swap_crossover ( first_crossover_point, second_crossover_point ):
			crossover_first_individual,crossover_second_individual = self.crossover_every_odd_index ( crossover_first_individual,crossover_second_individual )
		elif self.check_one_crossover_point ( first_crossover_point, second_crossover_point ):
			crossover_first_individual,crossover_second_individual = self.crossover_one_point (crossover_first_individual,crossover_second_individual, first_crossover_point)
		elif self.check_two_crossover_points ( first_crossover_point, second_crossover_point ):
			crossover_first_individual,crossover_second_individual = self.crossover_two_points (crossover_first_individual,crossover_second_individual, first_crossover_point, second_crossover_point)

		return crossover_first_individual, crossover_second_individual

	def check_every_odd_index_swap_crossover ( self, first_point, second_point ):
		"""
		Check crossover mode
		"""
		if first_point == second_point and first_point == -1:
			return True
		else:
			return False
	def crossover_every_odd_index ( self, first, second ):
		"""
		Swap every odd index
		"""
		# Get configurations of individuals
		first_config = first.get_configuration()
		second_config = second.get_configuration()

		# Swap odd indexes
		for index_of_config in range ( 0, len(first_config), 2 ):
			tmp = first_config[index_of_config]			
			first_config[index_of_config] = second_config[index_of_config]
			second_config[index_of_config] = tmp

		# Save configurations of individuals
		first . set_configuration ( first_config )
		second . set_configuration ( second_config )

		return first, second

	def check_one_crossover_point ( self, first_point, second_point ):
		"""
		Check crossover mode
		"""
		if first_point != second_point and second_point == -1:
			return True
		else:
			return False
	def crossover_one_point ( self, first, second, index ):
		"""
		Swap every gen from index to end
		"""
		# Get configurations of individuals
		first_config = first.get_configuration()
		second_config = second.get_configuration()

		# Swap from index to end
		for index_of_config in range ( index, len(first_config) ):
			tmp = first_config[index_of_config]			
			first_config[index_of_config] = second_config[index_of_config]
			second_config[index_of_config] = tmp

		# Save configurations of individuals
		first . set_configuration ( first_config )
		second . set_configuration ( second_config )

		return first, second
		
	def check_two_crossover_points ( self, first_point, second_point ):
		"""
		Check crossover mode
		"""
		if first_point != second_point and second_point != -1:
			return True
		else:
			return False
	def crossover_two_points ( self, first, second, first_point, second_point ):
		"""
		Swap every gen from index to end
		"""
		# Get configurations of individuals
		first_config = first.get_configuration()
		second_config = second.get_configuration()

		# Swap from first_point to second_point
		for index_of_config in range ( first_point, second_point):
			tmp = first_config[index_of_config]			
			first_config[index_of_config] = second_config[index_of_config]
			second_config[index_of_config] = tmp

		# Save configurations of individuals
		first . set_configuration ( first_config )
		second . set_configuration ( second_config )

		return first, second
