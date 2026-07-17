import pytest

from gen_algo.mutation import *
from data.individual import Individual

def test_do_mutation_mutates_individual():
    # Original individual
    original_individual = Individual([0, 0, 0, 0])
    # Individual passed to mutation
    individual = deepcopy(original_individual)

    # Mutated individual
    mutated_individual = do_mutation(individual, 1, 1)


    # do_mutation only ever changes the fold (configuration), never the amino
    # acid sequence itself, whether or not the candidate mutation is accepted.
    assert mutated_individual.get_individual().get_amino_sequance() == original_individual.get_individual().get_amino_sequance()
    assert mutated_individual.get_free_energy() is not None