#! /usr/bin/python3

import itertools
import random
from copy import deepcopy
from multiprocessing.dummy import Pool as ThreadPool

import utils
from abstract_solver import AbstractSolver
from gen_algo.ant_colony import AntColony
from gen_algo.crossover import do_crossover
from gen_algo.hill_climbing import do_hill_climbing
from data.individual import Individual
from gen_algo.mutation import do_mutation
from data.population import Population
from gen_algo.simulated_annealing import do_simulated_annealing

NOT_VALID_CONFIGURATION = False
VALID_CONFIGURATION = True

# MUTATION
MUTATION_TYPE = (2 / 3)

# HILL CLIMBING
COUNT_OF_HILL_CLIMBING = 10
HILL_CLIMBING_COUNT_OF_NEIGHOUR = 12
HILL_CLIMBING_COUNT_OF_ITERATION = 5

# SIMULATED ANNEALING
COUNT_OF_SIMULATED_ANNEALING = 2
SIMULATED_ANNEALING_COOLING_RATE = 0.9
INITAL_TEMPERATURE = 10000
MIN_TEMPERATURE = 1

# ANT-COLONY OPTIMISATION
COUNT_OF_ANT_COLONY = 50
COUNT_OF_ANTS = 8


class GeneticsAlgorithm(AbstractSolver):
    def __init__(self, sequance, max_generation, population_size,
                 count_of_mutation_per_generation, count_of_crossover_per_generation,
                 mutate_rate, crossover_rate, store_individuals_per_generation=True):

        self.MAX_GENERATION = max_generation
        self.POPULATION_SIZE = population_size

        self.FREQUANCY_OF_HILL_CLIMBING = (int)(max_generation / COUNT_OF_HILL_CLIMBING)
        self.FREQUANCY_OF_SIMULATED_ANNEALING = (int)(max_generation / COUNT_OF_SIMULATED_ANNEALING)
        self.FREQUANCY_OF_ANT_COLONY = (int)(max_generation / COUNT_OF_ANT_COLONY)

        self.MUTATE_RATE = mutate_rate
        self.CROSSOVER_RATE = crossover_rate

        self.COUNT_OF_MUTATION_PER_GENERATION = count_of_mutation_per_generation
        self.COUNT_OF_CROSSOVER_PER_GENERATION = count_of_crossover_per_generation

        self.STORE_INDIVIDUALS_PER_GENERATION = store_individuals_per_generation
        self.list_individuals = []

        super().__init__(sequance)
        self.verboseGeneticsSolver = True

        print("GeneticsAlgorithm -> init")

        self.counter_before_disaster = 0

        self.ant_colony = None

        self.is_mutation_enabled = True
        self.is_crossover_enabled = True
        self.is_hill_climbing_enabled = False
        self.is_simulated_annealing_enabled = True
        self.is_ant_colony_enabled = True

    def solve(self):
        if self.verboseGeneticsSolver:
            print("GeneticsAlgorithm -> solve")

        # Create population
        population = Population(self.POPULATION_SIZE)

        # Init population
        population.init_population(self.result_vector)

        best_individual_of_population, _ = population.pick_random_individual()

        if self.verboseGeneticsSolver:
            print(" Init population: ", population)

        for iteration in range(1, self.MAX_GENERATION + 1):
            population, best_individual_of_population = self.run_generation(population, iteration,
                                                                            best_individual_of_population)

        return best_individual_of_population.get_individual()

    def run_generation(self, population, iteration, best_individual_of_population):
        """
        Run mutation, crossover, hill-climbing, simulated annealing, and
        ant-colony for a single generation, then track timing and the
        best individual found so far
        """
        start_times = []
        end_times = []
        methods = []

        start_times.append(utils.get_time_in_millis())
        # MUTATION
        if self.is_mutation_enabled:
            print("GeneticsAlgorithm -> Mutation")
            self.mutate(population, iteration)

        methods.append("Mutation")
        end_times.append(utils.get_time_in_millis())

        # CROSS-OVER
        start_times.append(utils.get_time_in_millis())

        crossover_probability = random.random()  # NOSONAR python:S2245 - non-cryptographic use, algorithmic randomness only
        if self.is_crossover_enabled and crossover_probability < self.CROSSOVER_RATE:
            print("GeneticsAlgorithm -> Crossover")
            population = self.do_crossover(population, self.COUNT_OF_CROSSOVER_PER_GENERATION)
        methods.append("Crossover")
        end_times.append(utils.get_time_in_millis())

        # HILL-CLIMBING
        start_times.append(utils.get_time_in_millis())

        if self.is_hill_climbing_enabled:
            print("GeneticsAlgorithm -> Hill-Climbing")
            population = self.run_hill_climbing_step(population, iteration)

        methods.append("Hill-Climbing")
        end_times.append(utils.get_time_in_millis())

        # SIMULATED ANNEALING
        start_times.append(utils.get_time_in_millis())

        if self.is_simulated_annealing_enabled:
            print("GeneticsAlgorithm -> Simulated Annealing")
            population = self.run_simulated_annealing_step(population)

        methods.append("Simulated Annealing")
        end_times.append(utils.get_time_in_millis())

        # ANT-COLONY
        start_times.append(utils.get_time_in_millis())

        if self.is_ant_colony_enabled:
            print("GeneticsAlgorithm -> Ant-Colony")
            population = self.do_ant_colony(population, iteration)

        methods.append("Ant-Colony")
        end_times.append(utils.get_time_in_millis())

        time_to_print = utils.get_string_of_computed_times(start_times, end_times, methods)

        # Pick best individual from population and compare with best individual found
        best_individual_of_iteration, average_fitness = population.pick_best_individual()

        best_individual_of_population = self.get_best_individual(best_individual_of_iteration,
                                                                 best_individual_of_population)

        if self.STORE_INDIVIDUALS_PER_GENERATION:
            self.list_individuals.append(best_individual_of_iteration)

        # Print best individual
        if self.verboseGeneticsSolver:
            iteration_str = "Iteration: " + str(iteration) + "\n"
            iteration_str += "Energy of best individual: {:10.3f}, Average fitness: {:10.3f}".format(
                best_individual_of_population.get_free_energy(), average_fitness)
            print(time_to_print)
            print(iteration_str)

        return population, best_individual_of_population

    def run_hill_climbing_step(self, population, iteration):
        """
        Occasionally replace a random individual with a hill-climbed one
        """
        if iteration % self.FREQUANCY_OF_HILL_CLIMBING == 0:
            # Pick random individual from population
            parent, index_of_parent = population.pick_random_individual()
            # Hill-Climbing
            mutated_individual = do_hill_climbing(parent, HILL_CLIMBING_COUNT_OF_ITERATION,
                                                  HILL_CLIMBING_COUNT_OF_NEIGHOUR)
            # New individual to population
            population.set_individual_at(index_of_parent, mutated_individual)

        return population

    def run_simulated_annealing_step(self, population):
        """
        Replace a random sample of individuals with simulated-annealed ones
        """
        # Get random unique indexes of individuals
        index_of_individuals = random.sample(range(0, population.count_of_individuals()),  # NOSONAR python:S2245 - non-cryptographic use, algorithmic randomness only
                                             COUNT_OF_SIMULATED_ANNEALING)

        # Fill individuals
        individuals_to_simulated_annealing = []
        for index in index_of_individuals:
            individuals_to_simulated_annealing.append(population.get_individual_at(index))

        # Init thread pool
        simulated_annealing_pool = ThreadPool(8)
        # Simulated Annealing
        results = simulated_annealing_pool.starmap(do_simulated_annealing,
                                                   zip(individuals_to_simulated_annealing))
        # Replace new individuals to population
        for mutated_individual, index in zip(results, index_of_individuals):
            population.set_individual_at(index, mutated_individual)
        # Clear thread pool
        simulated_annealing_pool.close()

        return population

    def mutate(self, population, iteration):
        index_of_individuals = random.sample(range(0, population.count_of_individuals()),  # NOSONAR python:S2245 - non-cryptographic use, algorithmic randomness only
                                             self.COUNT_OF_MUTATION_PER_GENERATION)
        individuals_to_mutate = []
        mutation_pool = ThreadPool(4)

        for index in index_of_individuals:
            individuals_to_mutate.append(population.get_individual_at(index))

        results = mutation_pool.starmap(do_mutation, zip(individuals_to_mutate, itertools.repeat(self.MUTATE_RATE),
                                                         itertools.repeat(iteration),
                                                         itertools.repeat(self.MAX_GENERATION)))

        for mutated_individual, index in zip(results, index_of_individuals):
            population.set_individual_at(index, mutated_individual)

        mutation_pool.close()

    def get_best_individual(self, best_iteration, best_population):
        if best_iteration.get_free_energy() < best_population.get_free_energy():
            best_population = deepcopy(best_iteration)
            best_population.compute_free_energy()

        return best_population

    def do_ant_colony(self, population, iteration):
        """
        Ant colony optimisation
        """
        if self.ant_colony == None:
            self.ant_colony = AntColony(COUNT_OF_ANTS, self.sequance, iteration, self.MAX_GENERATION)

        new_individuals = self.ant_colony.search()

        population = self.replace_worst_individuals(new_individuals, len(new_individuals), population)

        return population

    def replace_worst_individuals(self, list_of_of_new_individuals, count_of_new, population):
        """
        Find n individuals with highest score and replace them with new individuals
        """
        indexes_of_worst_individuals = population.find_worst_individuals(count_of_new)

        for index in range(len(indexes_of_worst_individuals)):
            population.set_individual_at(indexes_of_worst_individuals[index], list_of_of_new_individuals[index])
            population.get_individual_at(indexes_of_worst_individuals[index]).compute_free_energy()

        return population

    def generate_random(self):
        return Individual(self.sequance)

    # CROSSOVER
    def do_crossover(self, population, count_of_crossover):
        """
        Crossover
        """
        for _ in range(count_of_crossover):
            first_individual, first_index = population.pick_random_individual()
            second_individual, second_index = population.pick_random_individual()

            crossover_individuals = do_crossover(first_individual, second_individual)

            if crossover_individuals[0] != first_individual:
                population.set_individual_at(first_index, crossover_individuals[0])
            if crossover_individuals[1] != second_individual:
                population.set_individual_at(second_index, crossover_individuals[1])

        return population
