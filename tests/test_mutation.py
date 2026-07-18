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


class FakeMutatedIndividual:
    def __init__(self, free_energy, valid=True):
        self._free_energy = free_energy
        self._valid = valid

    def compute_free_energy(self):
        return self._free_energy

    def check_valid_configuration(self):
        return self._valid


def test_mutate_one_point_flips_configs_below_mutation_rate(monkeypatch):
    individual = Individual([0, 1, 1, 0])
    original_config = list(individual.get_individual().get_configuration())

    monkeypatch.setattr("gen_algo.mutation.random.random", lambda: 0.05)

    mutated = mutate_one_point(individual, mutation_rate=0.1)

    mutated_config = mutated.get_individual().get_configuration()
    expected = [c * complex(0, 1) for c in original_config]
    assert mutated_config == expected
    assert mutated is not individual


def test_mutate_one_point_leaves_configs_above_mutation_rate_unchanged(monkeypatch):
    individual = Individual([0, 1, 1, 0])
    original_config = list(individual.get_individual().get_configuration())

    monkeypatch.setattr("gen_algo.mutation.random.random", lambda: 0.5)

    mutated = mutate_one_point(individual, mutation_rate=0.1)

    mutated_config = mutated.get_individual().get_configuration()
    assert mutated_config == original_config
    assert mutated is not individual


def test_mutate_from_point_flips_from_random_index_to_end(monkeypatch):
    individual = Individual([0, 1, 1, 0, 1])
    original_config = list(individual.get_individual().get_configuration())

    monkeypatch.setattr("gen_algo.mutation.random.randint", lambda a, b: 1)

    mutated = mutate_from_point(individual, mutation_rate=0.1)

    mutated_config = mutated.get_individual().get_configuration()
    expected = list(original_config)
    for i in range(1, len(expected)):
        expected[i] *= complex(0, 1)
    assert mutated_config == expected


def test_mutate_from_to_point_flips_range(monkeypatch):
    individual = Individual([0, 1, 1, 0, 1, 0])
    original_config = list(individual.get_individual().get_configuration())

    calls = iter([1, 3])
    monkeypatch.setattr("gen_algo.mutation.random.randint", lambda a, b: next(calls))

    mutated = mutate_from_to_point(individual, mutation_rate=0.1)

    mutated_config = mutated.get_individual().get_configuration()
    expected = list(original_config)
    for i in range(1, 3):
        expected[i] *= complex(-1, 0)
    assert mutated_config == expected


def test_pick_mutation_method_without_iteration_info(monkeypatch):
    monkeypatch.setattr("gen_algo.mutation.random.random", lambda: 0.4)
    assert pick_mutation_method(None, None) is mutate_one_point

    monkeypatch.setattr("gen_algo.mutation.random.random", lambda: 0.6)
    assert pick_mutation_method(None, None) is mutate_from_point


def test_pick_mutation_method_early_iteration(monkeypatch):
    monkeypatch.setattr("gen_algo.mutation.random.random", lambda: 0.5)
    assert pick_mutation_method(1, 10) is mutate_from_point

    monkeypatch.setattr("gen_algo.mutation.random.random", lambda: 0.95)
    assert pick_mutation_method(1, 10) is mutate_from_to_point


def test_pick_mutation_method_late_iteration(monkeypatch):
    monkeypatch.setattr("gen_algo.mutation.random.random", lambda: 0.5)
    assert pick_mutation_method(9, 10) is mutate_one_point

    monkeypatch.setattr("gen_algo.mutation.random.random", lambda: 0.95)
    assert pick_mutation_method(9, 10) is mutate_from_to_point


def test_do_mutation_verbose_prints(monkeypatch, capsys):
    monkeypatch.setattr("gen_algo.mutation.verbose", True)
    individual = Individual([0, 1, 1, 0])
    monkeypatch.setattr(
        "gen_algo.mutation.pick_mutation_method",
        lambda iteration, max_iteration: (lambda ind, rate: deepcopy(ind)),
    )

    do_mutation(individual, mutation_rate=0.1, iteration=1, max_iteration=10)

    assert "GeneticsAlgorithm -> Mutation" in capsys.readouterr().out


def test_do_mutation_accepts_when_valid_and_improved(monkeypatch):
    original = Individual([0, 1, 1, 0])
    original.free_energy = 100.0

    better = FakeMutatedIndividual(free_energy=5.0, valid=True)
    monkeypatch.setattr(
        "gen_algo.mutation.pick_mutation_method",
        lambda iteration, max_iteration: (lambda ind, rate: better),
    )

    result = do_mutation(original, mutation_rate=0.1, iteration=1, max_iteration=10)

    assert result is better


def test_do_mutation_rejects_when_invalid(monkeypatch):
    original = Individual([0, 1, 1, 0])
    original.free_energy = 100.0

    worse_but_invalid = FakeMutatedIndividual(free_energy=5.0, valid=False)
    monkeypatch.setattr(
        "gen_algo.mutation.pick_mutation_method",
        lambda iteration, max_iteration: (lambda ind, rate: worse_but_invalid),
    )

    result = do_mutation(original, mutation_rate=0.1, iteration=1, max_iteration=10)

    assert result is original
