from multiprocessing.dummy import Pool as ThreadPool

from data.individual import Individual
from gen_algo.ant_colony import AntColony


def make_ant_colony():
    return AntColony(count_of_ants=2, sequance=[0, 1, 1, 0], iteration=0, max_iteration=10)


def test_remove_invalid_individuals_drops_none_entries():
    colony = make_ant_colony()
    individual_a = Individual([0, 1, 1, 0])
    individual_b = Individual([0, 1, 1, 0])
    individuals = [individual_a, None, individual_b, None]
    tabu_lists = [[0], [1], [2], [3]]

    colony.remove_invalid_individuals(individuals, tabu_lists)

    assert individuals == [individual_a, individual_b]
    assert tabu_lists == [[0], [2]]


def test_sync_tabu_lists_only_updates_mutated_individuals(monkeypatch):
    colony = make_ant_colony()
    monkeypatch.setattr(colony, "update_tabu_list", lambda individual, tabu_list: "updated")

    unchanged = Individual([0, 1, 1, 0])
    mutated = Individual([0, 1, 1, 0])
    results = [mutated, unchanged, None]
    individuals = [unchanged, unchanged, unchanged]
    tabu_lists = [["a"], ["b"], ["c"]]

    colony.sync_tabu_lists(results, individuals, tabu_lists)

    assert tabu_lists == ["updated", ["b"], ["c"]]


def test_run_local_search_pool_dispatches_based_on_random_choice(monkeypatch):
    colony = make_ant_colony()
    individual = Individual([0, 1, 1, 0])

    monkeypatch.setattr("gen_algo.ant_colony.do_simulated_annealing", lambda individual, cooling_rate: "sa-result")
    monkeypatch.setattr("gen_algo.ant_colony.do_hill_climbing", lambda individual, neighbour, iteration: "hc-result")
    monkeypatch.setattr("gen_algo.ant_colony.random.random", lambda: 0.0)

    pool = ThreadPool(1)
    try:
        results = colony.run_local_search_pool(pool, [individual])
    finally:
        pool.close()

    assert results == ["sa-result"]

    monkeypatch.setattr("gen_algo.ant_colony.random.random", lambda: 0.9)

    pool = ThreadPool(1)
    try:
        results = colony.run_local_search_pool(pool, [individual])
    finally:
        pool.close()

    assert results == ["hc-result"]


def test_local_search_removes_invalid_and_returns_results(monkeypatch):
    colony = make_ant_colony()
    colony.verbose = True

    monkeypatch.setattr("gen_algo.ant_colony.do_simulated_annealing", lambda individual, cooling_rate: individual)
    monkeypatch.setattr("gen_algo.ant_colony.do_hill_climbing", lambda individual, neighbour, iteration: individual)
    monkeypatch.setattr("gen_algo.ant_colony.random.random", lambda: 0.0)

    individual = Individual([0, 1, 1, 0])
    individuals = [individual, None]
    tabu_lists = [[0], [1]]

    results, updated_tabu_lists = colony.local_search(individuals, tabu_lists)

    assert results == [individual]
    assert updated_tabu_lists == [[0]]


def test_remove_individuals_local_search_could_not_improve_keeps_alignment():
    colony = make_ant_colony()
    individual_a = Individual([0, 1, 1, 0])
    individual_b = Individual([0, 1, 1, 0])
    individual_c = Individual([0, 1, 1, 0])

    # A None in a leading position must not shift which tabu_list/individual
    # a later, kept result is matched up with.
    results = [None, individual_b, individual_c]
    individuals = [individual_a, individual_b, individual_c]
    tabu_lists = [["a"], ["b"], ["c"]]

    colony.remove_individuals_local_search_could_not_improve(results, individuals, tabu_lists)

    assert results == [individual_b, individual_c]
    assert individuals == [individual_b, individual_c]
    assert tabu_lists == [["b"], ["c"]]


def test_local_search_drops_individuals_local_search_could_not_improve(monkeypatch):
    colony = make_ant_colony()
    colony.verbose = True

    monkeypatch.setattr("gen_algo.ant_colony.do_simulated_annealing", lambda individual, cooling_rate: None)
    monkeypatch.setattr("gen_algo.ant_colony.do_hill_climbing", lambda individual, neighbour, iteration: None)
    monkeypatch.setattr("gen_algo.ant_colony.random.random", lambda: 0.9)

    individual = Individual([0, 1, 1, 0])
    individuals = [individual]
    tabu_lists = [[0]]

    results, updated_tabu_lists = colony.local_search(individuals, tabu_lists)

    assert results == []
    assert individuals == []
    assert updated_tabu_lists == []
