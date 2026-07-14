import pytest

from data.individual import Individual
from gen_algo.genetics_algorithm import GeneticsAlgorithm


def make_solver(max_generation, population_size, monkeypatch, **kwargs):
    """
    Build a GeneticsAlgorithm with the expensive/non-deterministic
    optimisation steps stubbed out, so solve() only exercises the
    population bookkeeping (including list_individuals tracking).
    """
    solver = GeneticsAlgorithm(
        sequance=[0, 1, 1, 0, 1, 0],
        MAX_GENERATION=max_generation,
        POPULATION_SIZE=population_size,
        COUNT_OF_MUTATION_PER_GENERATION=0,
        COUNT_OF_CROSSOVER_PER_GENERATION=0,
        MUTATE_RATE=0.0,
        CROSSOVER_RATE=0.0,
        **kwargs,
    )
    solver.verboseGeneticsSolver = False

    monkeypatch.setattr(solver, "mutate", lambda population, iteration: None)
    monkeypatch.setattr(solver, "do_crossover", lambda population, count: population)
    monkeypatch.setattr(solver, "do_ant_colony", lambda population, iteration: population)
    monkeypatch.setattr(
        "gen_algo.genetics_algorithm.do_simulated_annealing",
        lambda individual: individual,
    )

    return solver


def test_list_individuals_is_empty_after_init():
    solver = GeneticsAlgorithm(
        sequance=[0, 1, 1, 0],
        MAX_GENERATION=1,
        POPULATION_SIZE=2,
        COUNT_OF_MUTATION_PER_GENERATION=0,
        COUNT_OF_CROSSOVER_PER_GENERATION=0,
        MUTATE_RATE=0.0,
        CROSSOVER_RATE=0.0,
    )

    assert solver.list_individuals == []


def test_solve_appends_one_individual_per_generation(monkeypatch):
    max_generation = 3
    solver = make_solver(max_generation, population_size=4, monkeypatch=monkeypatch)

    solver.solve()

    assert len(solver.list_individuals) == max_generation


def test_solve_stores_individuals_by_default(monkeypatch):
    solver = make_solver(3, population_size=4, monkeypatch=monkeypatch)

    assert solver.STORE_INDIVIDUALS_PER_GENERATION is True

    solver.solve()

    assert len(solver.list_individuals) == 3


def test_solve_does_not_store_individuals_when_disabled(monkeypatch):
    solver = make_solver(
        3, population_size=4, monkeypatch=monkeypatch,
        STORE_INDIVIDUALS_PER_GENERATION=False,
    )

    solver.solve()

    assert solver.list_individuals == []


def test_solve_stores_individuals_when_explicitly_enabled(monkeypatch):
    solver = make_solver(
        3, population_size=4, monkeypatch=monkeypatch,
        STORE_INDIVIDUALS_PER_GENERATION=True,
    )

    solver.solve()

    assert len(solver.list_individuals) == 3


def test_solve_stores_best_individual_of_each_iteration(monkeypatch):
    solver = make_solver(2, population_size=4, monkeypatch=monkeypatch)

    solver.solve()

    for stored_individual in solver.list_individuals:
        assert isinstance(stored_individual, Individual)
        assert stored_individual.get_free_energy() is not None


def test_solve_records_consistent_energy_when_population_is_unchanged(monkeypatch):
    # With mutation/crossover/simulated-annealing/ant-colony all stubbed to
    # no-ops, the population never changes between generations, so every
    # recorded "best individual of iteration" should report the same energy.
    solver = make_solver(4, population_size=4, monkeypatch=monkeypatch)

    solver.solve()

    energies = [individual.get_free_energy() for individual in solver.list_individuals]
    assert energies == [energies[0]] * len(energies)
