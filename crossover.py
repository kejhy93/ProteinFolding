#! /usr/bin/python3

import random
from copy import deepcopy


def do_crossover(first_individual, second_individual, CROSSOVER_RATE=0.3):
    # Crossover two individual
    crossover_mode_probability = random.random()

    first_crossover_point = -1
    second_crossover_point = -1

    if (crossover_mode_probability < (float)(1 / 3)):
        # One-point crossover
        first_crossover_point = random.randint(0, len(first_individual.get_configuration()))
        second_crossover_point = -1
    elif (crossover_mode_probability < (float)(2 / 3)):
        # Two point crossover
        first_crossover_point = random.randint(0, len(first_individual.get_configuration()))
        second_crossover_point = random.randint(first_crossover_point, len(first_individual.get_configuration()))
    else:
        # Uniform crossover
        first_crossover_point = second_crossover_point = -1

    crossover_first_individual, crossover_second_individual = crossover(first_individual, second_individual,
                                                                        first_crossover_point, second_crossover_point)

    # Compute free energy of crossovered individuals
    energy_of_first_crossover_individual = crossover_first_individual.compute_free_energy()
    energy_of_second_crossover_individual = crossover_second_individual.compute_free_energy()

    # Compute free energy of original indivudals
    energy_of_first_individual = first_individual.compute_free_energy()
    energy_of_second_individual = second_individual.compute_free_energy()

    # If free energy of crosovered individual is lower then original replace him
    if crossover_first_individual.check_valid_configuration():
        if energy_of_first_individual > energy_of_first_crossover_individual:
            first_individual = deepcopy(crossover_first_individual)
            first_individual.compute_free_energy()

    # If free energy of crosovered individual is lower then original replace him
    if energy_of_second_individual > energy_of_second_crossover_individual:
        if crossover_second_individual.check_valid_configuration():
            second_individual = deepcopy(crossover_second_individual)
            second_individual.compute_free_energy()

    return first_individual, second_individual


def crossover(first_individual, second_individual, first_crossover_point=-1, second_crossover_point=-1):
    """
    Crossover two random individuals

    first_crossover_point = second_crossover_point = -1 -> swap every odd index
    first_crossover_point = second_crossover_point != -1 ||
    first_crossover_point != -1 && second_crossover_point == -1 -> Swap every index from first_crossover_point to end

    first_crossover_point != second_crossover_point
    return tuple of two crossovered individuals
    """
    # Copy original individuals
    crossover_first_individual = deepcopy(first_individual)
    crossover_second_individual = deepcopy(second_individual)

    if check_every_odd_index_swap_crossover(first_crossover_point, second_crossover_point):
        # Check if swap every odd gene
        crossover_first_individual, crossover_second_individual = crossover_every_odd_index(crossover_first_individual,
                                                                                            crossover_second_individual)
    elif check_one_crossover_point(first_crossover_point, second_crossover_point):
        # Check if one-point crossover
        crossover_first_individual, crossover_second_individual = crossover_one_point(crossover_first_individual,
                                                                                      crossover_second_individual,
                                                                                      first_crossover_point)
    elif check_two_crossover_points(first_crossover_point, second_crossover_point):
        # Check if two-point crossover
        crossover_first_individual, crossover_second_individual = crossover_two_points(crossover_first_individual,
                                                                                       crossover_second_individual,
                                                                                       first_crossover_point,
                                                                                       second_crossover_point)

    return crossover_first_individual, crossover_second_individual


def check_every_odd_index_swap_crossover(first_point, second_point):
    """
    Check crossover mode
    """
    if first_point == second_point and first_point == -1:
        return True
    else:
        return False


def crossover_every_odd_index(first, second):
    """
    Swap every odd index
    """
    # Get configurations of individuals
    first_config = first.get_configuration()
    second_config = second.get_configuration()

    # Swap odd indexes
    for index_of_config in range(0, len(first_config), 2):
        tmp = first_config[index_of_config]
        first_config[index_of_config] = second_config[index_of_config]
        second_config[index_of_config] = tmp

    # Save configurations of individuals
    first.set_configuration(first_config)
    second.set_configuration(second_config)

    return first, second


def check_one_crossover_point(first_point, second_point):
    """
    Check crossover mode
    """
    if first_point != second_point and second_point == -1:
        return True
    else:
        return False


def crossover_one_point(first, second, index):
    """
    Swap every gen from index to end
    """
    # Get configurations of individuals
    first_config = first.get_configuration()
    second_config = second.get_configuration()

    # Swap from index to end
    for index_of_config in range(index, len(first_config)):
        tmp = first_config[index_of_config]
        first_config[index_of_config] = second_config[index_of_config]
        second_config[index_of_config] = tmp

    # Save configurations of individuals
    first.set_configuration(first_config)
    second.set_configuration(second_config)

    return first, second


def check_two_crossover_points(first_point, second_point):
    """
    Check crossover mode
    """
    if first_point != second_point and second_point != -1:
        return True
    else:
        return False


def crossover_two_points(first, second, first_point, second_point):
    """
    Swap every gen from index to end
    """
    # Get configurations of individuals
    first_config = first.get_configuration()
    second_config = second.get_configuration()

    # Swap from first_point to second_point
    for index_of_config in range(first_point, second_point):
        tmp = first_config[index_of_config]
        first_config[index_of_config] = second_config[index_of_config]
        second_config[index_of_config] = tmp

    # Save configurations of individuals
    first.set_configuration(first_config)
    second.set_configuration(second_config)

    return first, second
