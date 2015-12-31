#! /usr/bin/python3

from copy import deepcopy
from math import exp
import random

from vector import Vector
from mutation import do_mutation

verbose = False

# SIMULATED ANNEALING
def do_simulated_annealing ( individual, INITAL_TEMPERATURE=10000, MIN_TEMPERATURE=1, COOLING_RATE=0.9 ):
	"""
	Main method for simulated annealing
	"""
	if verbose:
		print ( "Simulated Annealing" )

	temperature = INITAL_TEMPERATURE

	# Get current solution from population
	current_solution = deepcopy(individual)

	while temperature > MIN_TEMPERATURE:

		# Get new solution by mutation
		new_solution = None

		new_solution = do_mutation ( current_solution, 0.1, temperature, INITAL_TEMPERATURE )

		# Compute energy of both solutions
		energy_of_current_solution = current_solution.get_free_energy()
		energy_of_new_solution = new_solution.compute_free_energy()

		# Decide if solution is good enough
		if new_solution.check_valid_configuration():
			if ( acceptanceProbability(energy_of_current_solution,energy_of_new_solution, temperature ) > random.random() ):
				current_solution = deepcopy ( new_solution )

			temperature = update_temperature ( temperature, COOLING_RATE )
			# print("temperature: ", temperature)


	return current_solution

def update_temperature ( temperature, COOLING_RATE ):
	# Update given temperature
	temperature *= COOLING_RATE
	return temperature

def acceptanceProbability ( energy, new_energy, temperature ):
	if ( energy > new_energy ):
		return 1;

	return exp((energy - new_energy) / temperature)