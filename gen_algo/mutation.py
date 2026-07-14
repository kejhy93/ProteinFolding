#! /usr/bin/python3

import random
from copy import deepcopy

MUTATION_TYPE = (2 / 3)

verbose = False


def do_mutation(individual, mutation_rate=0.1, iteration=None, max_iteration=None):
    """
    Main method for mutation
    """
    if verbose:
        print("GeneticsAlgorithm -> Mutation")

    mutated_individual = None

    # Pick mutation method
    mutation = pick_mutation_method(iteration, max_iteration)

    # Mutate individual
    mutated_individual = mutation(individual, mutation_rate)

    # Compute free energy of mutated individuals
    energy_of_first_mutate_individual = mutated_individual.compute_free_energy()

    # Compute free energy of original indivudals
    energy_of_first_individual = individual.get_free_energy()

    if mutated_individual.check_valid_configuration():
        if energy_of_first_mutate_individual < energy_of_first_individual:
            individual = mutated_individual

    return individual


def mutate_one_point(individual, mutation_rate):
    """
    Mutate individual with mutation_rate

    return mutated individual
    """
    # if verbose:
    # 	print ( "GeneticsAlgorithm -> mutate_one_point")

    mutate_individual = deepcopy(individual)
    mutate_vector = mutate_individual.get_individual()
    mutate_config = mutate_vector.get_configuration()

    for config_index in range(len(mutate_config)):
        random_number = random.random()

        if random_number < mutation_rate:
            mutate_config[config_index] *= complex(0, 1)

    mutate_vector.set_configuration(mutate_config)
    mutate_individual.set_individual(mutate_vector)

    return mutate_individual


def mutate_from_point(individual, mutation_rate):
    """
    Mutate individual with from random point to end

    return mutated individual
    """
    # if verbose:
    # 	print ( "GeneticsAlgorithm -> mutate_from_point")

    mutate_individual = deepcopy(individual)
    mutate_vector = mutate_individual.get_individual()
    mutate_config = mutate_vector.get_configuration()

    from_index = random.randint(0, len(mutate_config) - 1)

    for config_index in range(from_index, len(mutate_config)):
        mutate_config[config_index] *= complex(0, 1)

    mutate_vector.set_configuration(mutate_config)
    mutate_individual.set_individual(mutate_vector)

    return mutate_individual


def mutate_from_to_point(individual, mutation_rate):
    """
    Mutate individual from random index to random index

    return mutated individual
    """
    # if verbose:
    # 	print ( "GeneticsAlgorithm -> mutate_from_to_point")

    mutate_individual = deepcopy(individual)
    mutate_vector = mutate_individual.get_individual()
    mutate_config = mutate_vector.get_configuration()

    from_index = random.randint(0, len(mutate_config) - 1)
    to_index = random.randint(from_index, len(mutate_config) - 1)

    for config_index in range(from_index, to_index):
        mutate_config[config_index] *= complex(-1, 0)

    mutate_vector.set_configuration(mutate_config)
    mutate_individual.set_individual(mutate_vector)

    return mutate_individual


def pick_mutation_method(iteration, max_iteration):
    """
    Pick mutation method from iteration and max iteration
    """
    random_choice = random.random()

    if iteration == None or max_iteration == None:
        if random_choice < 0.5:
            return mutate_one_point
        else:
            return mutate_from_point

    if iteration < (MUTATION_TYPE) * max_iteration:
        if random_choice < 0.9:
            return mutate_from_point
        else:
            return mutate_from_to_point
    else:
        if random_choice < 0.9:
            return mutate_one_point
        else:
            return mutate_from_to_point
