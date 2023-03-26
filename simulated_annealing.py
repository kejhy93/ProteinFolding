#! /usr/bin/python3

import random
from copy import deepcopy
from math import exp

from mutation import do_mutation

verbose = False

MAX_COOLING_RATE = 1
MIN_COOLING_RATE = 0

COOLING_RATE_TOO_HIGH = -1
COOLING_RATE_TOO_LOW = -2
COOLING_RATE_OK = 1

TEMPERATURE_INVALID = -1
TEMPERATURE_VALID = 1


# SIMULATED ANNEALING
def do_simulated_annealing(individual, COOLING_RATE=0.99, INITAL_TEMPERATURE=10000, MIN_TEMPERATURE=1):
    """
    Main method for simulated annealing
    """
    # Initial check
    # Check valid of cooling rate
    valid_of_cooling_rate = check_valid_of_cooling_rate(COOLING_RATE)
    # Check of valid temperatures
    valid_of_temperatures = check_temperatures(INITAL_TEMPERATURE, MIN_TEMPERATURE)

    if valid_of_cooling_rate == COOLING_RATE_TOO_HIGH:
        print("Simulated Annealing -> Cooling rate is equal or higher then 1")
        return None
    elif valid_of_cooling_rate == COOLING_RATE_TOO_LOW:
        print("Simulated Annealing -> Cooling rate is equal or lower then 0")
        return None

    if valid_of_temperatures == TEMPERATURE_INVALID:
        print("Simulated Annealing -> Temperature invalid")
        return None

    if verbose:
        print("Simulated Annealing")

    temperature = INITAL_TEMPERATURE

    # Get current solution from population
    current_solution = deepcopy(individual)

    # Until temperature is low
    while temperature > MIN_TEMPERATURE:

        # Init new solution
        new_solution = None
        # Get new solution by mutation
        new_solution = do_mutation(current_solution, 0.1, temperature, INITAL_TEMPERATURE)

        # Get energy of both solutions
        energy_of_current_solution = current_solution.get_free_energy()
        energy_of_new_solution = new_solution.get_free_energy()

        if new_solution != current_solution:
            if energy_of_new_solution == energy_of_current_solution:
                print("Current solution: ", current_solution)
                print("New solution: ", new_solution)
                print("Energy are wrong")

        # Decide if solution is good enough
        if new_solution.check_valid_configuration():
            # Compute acceptance probability of new solution
            acceptance_prob = acceptance_probability(energy_of_current_solution, energy_of_new_solution, temperature)
            # Compare if new solution is accept
            if (acceptance_prob > random.random()):
                current_solution = new_solution

            # Update temperature
            temperature = update_temperature(temperature, COOLING_RATE)

    return current_solution


def update_temperature(temperature, COOLING_RATE):
    """
    Update temperature by COOLING_RATE
    """
    # Update given temperature
    temperature *= COOLING_RATE
    # Return updated temperature
    return temperature


def acceptance_probability(energy, new_energy, temperature):
    """
    Get acceptance probability of new solution given by temperature
    """
    if (energy > new_energy):
        return 1;

    return exp((energy - new_energy) / temperature)


def check_valid_of_cooling_rate(cooling_rate):
    """
    Check if cooling rate is valid
    """
    if cooling_rate >= MAX_COOLING_RATE:
        return COOLING_RATE_TOO_HIGH
    elif cooling_rate <= MIN_COOLING_RATE:
        return COOLING_RATE_TOO_LOW
    else:
        return COOLING_RATE_OK


def check_temperatures(INITAL_TEMPERATURE, MIN_TEMPERATURE):
    """
    Check if temperatures are valid
    """
    if INITAL_TEMPERATURE < MIN_TEMPERATURE:
        return TEMPERATURE_INVALID
    else:
        return TEMPERATURE_VALID
