#! /usr/bin/python3

from copy import deepcopy
import random
from math import exp

from abstract_solver import AbstractSolver

from population import Population
from individual import Individual


NOT_VALID_CONFIGURATION = False
VALID_CONFIGURATION = True

# HILL CLIMBING
HILL_CLIMBING_COUNT_OF_NEIGHOUR = 4
HILL_CLIMBING_COUNT_OF_ITERATION = 2

# SIMULATED ANNEALING
COUNT_OF_SIMULATED_ANNEALING = 25
SIMULATED_ANNEALING_COOLING_RATE = 0.85
INITAL_TEMPERATE=10000
MIN_TEMPERATURE = 1

# ANT-COLONY OPTIMISATION
COUNT_OF_ANTS = 5

class GeneticsAlgorithm ( AbstractSolver ):
	def __init__ ( self, sequance, MAX_GENERATION, POPULATION_SIZE, 
		COUNT_OF_MUTATION_PER_GENERATION, COUNT_OF_CROSSOVER_PER_GENERATION, 
		MUTATE_RATE, CROSSOVER_RATE ):

		self.MAX_GENERATION = MAX_GENERATION
		self.POPULATION_SIZE = POPULATION_SIZE

		self.FREQUANCY_OF_SIMULATED_ANNEALING= (int)(MAX_GENERATION/COUNT_OF_SIMULATED_ANNEALING)

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

		best_individual_of_population = population.pick_random_individual()
		energy_of_best_individual_of_population = 100000000

		if self.verboseGeneticsSolver:
			print ( " Init population: ", population)

		for iteration in range ( 1,self.MAX_GENERATION+1 ):
			iterationStr = ""
			iterationStr = "Iteration: " + str ( iteration ) + "\n"

			# MUTATION
			population = self.do_mutation( population )

			# CROSS-OVER
			population = self.do_crossover ( population )

			# SIMULATED ANNEALING
			if iteration%self.FREQUANCY_OF_SIMULATED_ANNEALING == 0:
				population = self.do_simulated_annealing ( population )

			# Pick best individual from population and compare with best individual found
			best_individual_of_iteration,average_fitness = population.pick_best_individual ()

			energy_of_best_individual_of_iteration = best_individual_of_iteration.compute_free_energy()

			if energy_of_best_individual_of_iteration < energy_of_best_individual_of_population:
				energy_of_best_individual_of_population = energy_of_best_individual_of_iteration

				best_individual_of_population = deepcopy ( best_individual_of_iteration )

			iterationStr += "Energy of best individual: {:10.3f}, Average fitness: {:10.3f}".format(energy_of_best_individual_of_population, average_fitness)
			# Print best individual
			if self.verboseGeneticsSolver:
				if iteration%25 == 0:
					print ( iterationStr )
				# 	best_individual_of_population.get_individual().plot_config()

		return best_individual_of_population.get_individual()


	def ant_colony ( self, population ):
		"""
		Ant colony optimisation
		"""

		COUNT_OF_ANTS = 5
		ant_colony = []
		for ant_number in range(COUNT_OF_ANTS):
			ant_colony.append ( Ant(ant_number) )

		return population

	# SIMULATED ANNEALING
	def do_simulated_annealing ( self, population ):
		# if self.verboseGeneticsSolver:
		# 	print ( "GeneticsAlgorithm -> Simulated Annealing" )
		temperature = INITAL_TEMPERATE

		# Get current solution from population
		current_solution,index = population.pick_random_individual()

		while temperature > MIN_TEMPERATURE:
			# Get current solution from population
			current_solution = population.get_individual_at(index)

			# Get new solution by mutation
			new_solution = self.mutate(current_solution)

			# Compute energy of both solutions
			energy_of_current_solution = current_solution.get_free_energy()
			energy_of_new_solution = new_solution.compute_free_energy()

			# Decide if solution is good enough
			if new_solution.check_valid_configuration():
				if ( self.acceptanceProbability(energy_of_current_solution,energy_of_new_solution, temperature ) > random.random() ):
					population.set_individual_at ( index, new_solution )

				temperature = self.update_temperature ( temperature )
				# print("temperature: ", temperature)


		return population

	def update_temperature ( self, temperature ):
		# Update given temperature
		temperature *= SIMULATED_ANNEALING_COOLING_RATE
		return temperature

	def acceptanceProbability ( self, energy, new_energy, temperature ):
		if ( energy > new_energy ):
			return 1;

		return exp((energy - new_energy) / temperature)


	def generate_random ( self, individual ):
		individual = Individual ( self.sequance )

		return individual

	# MUTATION
	def do_mutation ( self, population ):
		"""
		Main method for mutation

		Return mutated population
		"""
		for i in range(self.COUNT_OF_MUTATION_PER_GENERATION):
			# Pick two random individuals
			first_individual, first_index = population.pick_random_individual()
			second_individual, second_index = population.pick_random_individual()

			while second_index == first_index:
				second_individual, second_index = population.pick_random_individual()				

			# Mutate two random individuals
			# mutated_first_individual = self.hill_climbing ( first_individual, HILL_CLIMBING_COUNT_OF_NEIGHOUR, HILL_CLIMBING_COUNT_OF_ITERATION )
			mutated_first_individual = self.mutate ( first_individual )

			# Compute free energy of mutated individuals
			energy_of_first_mutate_individual = mutated_first_individual.compute_free_energy ()

			# Compute free energy of original indivudals
			energy_of_first_individual = first_individual.compute_free_energy()

			# If free energy of mutated individual is lower then original replace him
			if energy_of_first_individual > energy_of_first_mutate_individual:
				if mutated_first_individual.check_valid_configuration():
					first_individual = deepcopy ( mutated_first_individual )
					first_individual.compute_free_energy()
					population.set_individual_at ( first_index, first_individual )

		return population

	def mutate ( self, individual ):
		"""
		Mutate individual with MUTATE_RATE

		return mutated individual
		"""
		# if self.verboseGeneticsSolver:
		# 	print ( "GeneticsAlgorithm -> mutate")

		mutate_individual = deepcopy ( individual )

		mutate_vector = mutate_individual.get_individual ()

		mutate_config = mutate_vector.get_configuration()

		for config_index in range ( len(mutate_config) ):
			random_number = random.random()

			if random_number < self.MUTATE_RATE:
				mutate_config[config_index] *= complex(0,1)

		# for config in mutate_config:
		# 	random_number = random.random()

		# 	if random_number < MUTATE_RATE:
		# 		config *= complex(0,1)

		mutate_vector . set_configuration ( mutate_config )
		mutate_individual . set_individual ( mutate_vector )

		return mutate_individual

	# Hill-Climbing
	def hill_climbing ( self, individual, count_of_neighbor, iteration ):
		"""
		Recursive hill climbing 
		Generate count_of_neighour and pick with lowest energy
		"""
		# if self.verboseGeneticsSolver:
		# 	print ( "Hill climbing")

		best_neighbor = individual
		init_score = individual.get_free_energy()
		best_score = init_score

		for i in range ( count_of_neighbor ):
			indi = self.mutate ( individual )
			score = indi.compute_free_energy()

			if score < best_score:
				best_neighbor = indi
				best_score = score

		if init_score == best_score or iteration == 0:
			return best_neighbor
		else:
			new_iter = iteration - 1
			return self.hill_climbing(individual, count_of_neighbor , new_iter)

	# CROSSOVER
	def do_crossover ( self, population ):
		"""
		Main method for crossover

		Return crossovered population
		"""
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
		# if self.verboseGeneticsSolver:
		# 	print ( "GeneticsAlgorithm -> crossover")

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
