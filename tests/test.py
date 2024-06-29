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
    
    
    assert not (original_individual.__eq__ (mutated_individual))