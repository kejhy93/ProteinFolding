from multiprocessing.dummy import Pool as ThreadPool

from data.individual import Individual
from gen_algo.ant_colony import AntColony, EVAPORATE_CONSTANT, LEFT, RIGHT, STRAIGHT


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
    monkeypatch.setattr(colony, "update_tabu_list", lambda individual: "updated")

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


def test_init_ants_resets_list():
    colony = make_ant_colony()
    colony.ants = ["stub"]

    colony.init_ants()

    assert colony.ants == []


def test_update_heuristic_pheronome_value_covers_all_bands():
    colony = make_ant_colony()

    assert colony.update_heuristic_pheronome_value(0, 10) == (10, 1)
    assert colony.update_heuristic_pheronome_value(3, 10) == (6, 3)
    assert colony.update_heuristic_pheronome_value(5, 10) == (5, 4)
    assert colony.update_heuristic_pheronome_value(9, 10) == (4, 4)


def test_check_valid_of_new_individual_branches():
    colony = make_ant_colony()

    assert colony.check_valid_of_new_individual(None) is False
    assert colony.check_valid_of_new_individual("something") is True


def test_check_valid_of_new_individuals_branches():
    colony = make_ant_colony()

    assert colony.check_valid_of_new_individuals([None, None]) is False
    assert colony.check_valid_of_new_individuals([None, "x"]) is True


def test_search_orchestrates_ants_local_search_and_pheronome_update(monkeypatch):
    colony = make_ant_colony()
    colony.verbose = True

    class FakeAnt:
        def __init__(self, ant_index, sequance, pheronome, heuristic_val, pheronome_val):
            self.ant_index = ant_index

        def start(self):
            pass

        def join(self):
            pass

        def get_individual(self):
            return "individual-%d" % self.ant_index

        def get_tabu_list(self):
            return [self.ant_index]

    monkeypatch.setattr("gen_algo.ant_colony.Ant", FakeAnt)
    monkeypatch.setattr(colony, "local_search", lambda individuals, tabu_lists: (individuals, tabu_lists))

    recorded = {}

    def fake_update(new_individuals, tabu_lists):
        recorded["individuals"] = new_individuals
        recorded["tabu_lists"] = tabu_lists

    monkeypatch.setattr(colony, "update_pheronome_trails", fake_update)

    results = colony.search()

    assert results == ["individual-0", "individual-1"]
    assert len(colony.ants) == 2
    assert recorded["individuals"] == ["individual-0", "individual-1"]
    assert recorded["tabu_lists"] == [[0], [1]]


def test_update_pheronome_trails_applies_evaporation_and_delta(monkeypatch):
    colony = make_ant_colony()
    colony.verbose = True
    colony.pheronome = [[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0]]

    monkeypatch.setattr(
        colony,
        "compute_delta_pheronome",
        lambda individuals, tabu_lists: [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
    )

    colony.update_pheronome_trails([], [])

    assert colony.pheronome[0] == [1.0, 1.0, 1.0]
    assert colony.pheronome[1] == [
        2.0 * EVAPORATE_CONSTANT + 0.1,
        2.0 * EVAPORATE_CONSTANT + 0.2,
        2.0 * EVAPORATE_CONSTANT + 0.3,
    ]
    assert colony.pheronome[2] == [
        3.0 * EVAPORATE_CONSTANT + 0.4,
        3.0 * EVAPORATE_CONSTANT + 0.5,
        3.0 * EVAPORATE_CONSTANT + 0.6,
    ]


def test_compute_delta_pheronome_accumulates_by_direction():
    colony = make_ant_colony()
    colony.verbose = True
    colony.pheronome = [[0, 0, 0], [0, 0, 0]]

    class FakeIndividual:
        def __init__(self, free_energy):
            self._free_energy = free_energy

        def get_free_energy(self):
            return self._free_energy

    individuals = [FakeIndividual(10), FakeIndividual(20)]
    tabu_lists = [[9, STRAIGHT], [9, LEFT]]

    delta = colony.compute_delta_pheronome(individuals, tabu_lists)

    assert delta == [[100.0, 50.0, 0.0]]


def test_update_tabu_list_detects_turns_from_configuration():
    colony = make_ant_colony()
    individual = Individual([0, 1, 1, 0, 1])
    individual.vector.set_configuration([complex(1, 0), complex(1, 0), complex(0, 1), complex(1, 0)])

    tabu_list = colony.update_tabu_list(individual)

    assert tabu_list == [STRAIGHT, STRAIGHT, LEFT, RIGHT]
