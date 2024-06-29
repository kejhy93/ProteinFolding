#! /usr/bin/python3

from gen_algo.mutation import do_mutation

verbose = True

COUNT_OF_ITERATION = 10
COUNT_OF_NEIGHBOR = 12


def do_hill_climbing(individual, COUNT_OF_ITERATION=5, COUNT_OF_NEIGHBOR=6):
    """
    Main method for hill-climbing
    """
    # if verbose:
    # 	print ( "Hill climbing")

    new_individual = hill_climbing(individual, COUNT_OF_ITERATION, COUNT_OF_NEIGHBOR)

    return new_individual


def hill_climbing(individual, iteration, count_of_neighour):
    """
    Recursive hill climbing
    Generate count_of_neighour and pick with lowest energy
    """
    best_neighbor = individual
    init_score = individual.get_free_energy()
    best_score = init_score

    for i in range(count_of_neighour):
        indi = do_mutation(individual)
        score = indi.compute_free_energy()

        if score < best_score:
            best_neighbor = indi
            best_score = score

    if init_score == best_score or iteration == 0:
        return best_neighbor
    else:
        new_iter = iteration - 1
        return hill_climbing(individual, new_iter, count_of_neighour)
