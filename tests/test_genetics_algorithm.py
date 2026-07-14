import pytest

from data.individual import Individual
from data.population import Population
from gen_algo.genetics_algorithm import GeneticsAlgorithm


def make_solver(max_generation, population_size, monkeypatch, **kwargs):
    """
    Build a GeneticsAlgorithm with the expensive/non-deterministic
    optimisation steps stubbed out, so solve() only exercises the
    population bookkeeping (including list_individuals tracking).
    """
    solver = GeneticsAlgorithm(
        sequance=[0, 1, 1, 0, 1, 0],
        max_generation=max_generation,
        population_size=population_size,
        count_of_mutation_per_generation=0,
        count_of_crossover_per_generation=0,
        mutate_rate=0.0,
        crossover_rate=0.0,
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
        max_generation=1,
        population_size=2,
        count_of_mutation_per_generation=0,
        count_of_crossover_per_generation=0,
        mutate_rate=0.0,
        crossover_rate=0.0,
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
        store_individuals_per_generation=False,
    )

    solver.solve()

    assert solver.list_individuals == []


def test_solve_stores_individuals_when_explicitly_enabled(monkeypatch):
    solver = make_solver(
        3, population_size=4, monkeypatch=monkeypatch,
        store_individuals_per_generation=True,
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


def test_run_hill_climbing_step_replaces_individual_on_matching_iteration(monkeypatch):
    solver = make_solver(20, population_size=4, monkeypatch=monkeypatch)
    replacement = Individual([0, 1, 1, 0, 1, 0])
    monkeypatch.setattr(
        "gen_algo.genetics_algorithm.do_hill_climbing",
        lambda parent, iterations, neighbours: replacement,
    )

    population = Population(4)
    population.init_population(solver.result_vector)

    result = solver.run_hill_climbing_step(population, solver.FREQUANCY_OF_HILL_CLIMBING)

    replaced_sequances = [ind.get_individual().get_amino_sequance() for ind in result.individuals]
    assert replacement.get_individual().get_amino_sequance() in replaced_sequances


def test_run_hill_climbing_step_leaves_population_unchanged_off_cycle(monkeypatch):
    solver = make_solver(20, population_size=4, monkeypatch=monkeypatch)
    monkeypatch.setattr(
        "gen_algo.genetics_algorithm.do_hill_climbing",
        lambda parent, iterations, neighbours: (_ for _ in ()).throw(AssertionError("should not run")),
    )

    population = Population(4)
    population.init_population(solver.result_vector)
    original_individuals = list(population.individuals)

    result = solver.run_hill_climbing_step(population, solver.FREQUANCY_OF_HILL_CLIMBING + 1)

    assert result.individuals == original_individuals


def test_run_generation_triggers_crossover_when_probability_favors_it(monkeypatch):
    solver = make_solver(1, population_size=4, monkeypatch=monkeypatch)
    solver.CROSSOVER_RATE = 1.0
    crossover_calls = []
    monkeypatch.setattr(
        solver, "do_crossover",
        lambda population, count: crossover_calls.append(count) or population,
    )

    solver.solve()

    assert crossover_calls == [solver.COUNT_OF_CROSSOVER_PER_GENERATION]


def test_run_generation_runs_hill_climbing_when_enabled(monkeypatch):
    solver = make_solver(20, population_size=4, monkeypatch=monkeypatch)
    solver.is_hill_climbing_enabled = True
    hill_climbing_calls = []
    monkeypatch.setattr(
        "gen_algo.genetics_algorithm.do_hill_climbing",
        lambda parent, iterations, neighbours: (hill_climbing_calls.append(1), parent)[1],
    )

    solver.solve()

    assert hill_climbing_calls


def test_solve_verbose_prints_iteration_summary(monkeypatch, capsys):
    solver = make_solver(1, population_size=4, monkeypatch=monkeypatch)
    solver.verboseGeneticsSolver = True

    solver.solve()

    assert "Energy of best individual" in capsys.readouterr().out
