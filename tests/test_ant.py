from collections import Counter

import utils
from data.ant import Ant, NO_ROUTE


def make_ant(sequance=None, pheronome=None, heuristic_val=5, pheronome_val=1, ant_id=0):
    if sequance is None:
        sequance = [0, 1, 1, 0]
    if pheronome is None:
        pheronome = [[0.5, 0.5, 0.5] for _ in range(len(sequance) - 1)]
    return Ant(ant_id, sequance, pheronome, heuristic_val, pheronome_val)


def test_selection_sort_orders_descending_by_value():
    ant = make_ant()
    indexes = [0, 1, 2, 3]
    values = [3, 1, 4, 2]

    sorted_indexes, sorted_values = ant.selection_sort(indexes, values)

    assert sorted_values == [4, 3, 2, 1]
    assert sorted_indexes == [2, 0, 3, 1]


def test_randomize_equal_solutions_no_swap_when_probability_high(monkeypatch):
    ant = make_ant()
    monkeypatch.setattr("data.ant.random.random", lambda: 0.9)

    indexes = [0, 1, 2]
    values = [1.0, 1.0, 1.0]

    result_indexes, result_values = ant.randomize_equal_solutions(indexes, values)

    assert result_indexes == [0, 1, 2]
    assert result_values == [1.0, 1.0, 1.0]


def test_randomize_equal_solutions_swaps_when_change_rate_allows(monkeypatch, capsys):
    ant = make_ant()
    monkeypatch.setattr("data.ant.CHANGE_RATE", 1)
    monkeypatch.setattr("data.ant.SWITCH_PROBABILITY", 1.0)
    monkeypatch.setattr("data.ant.random.random", lambda: 0.0)

    indexes = [0, 1, 2]
    values = [1.0, 1.0001, 5.0]

    result_indexes, result_values = ant.randomize_equal_solutions(indexes, values)

    assert result_indexes == [1, 0, 2]
    assert result_values == [1.0001, 1.0, 5.0]
    assert "Swap" in capsys.readouterr().out


def test_sort_by_combines_selection_sort_and_randomize(monkeypatch):
    ant = make_ant()
    monkeypatch.setattr("data.ant.random.random", lambda: 0.9)

    indexes = [0, 1, 2]
    values = [3, 1, 2]

    result_indexes, result_values = ant.sort_by(indexes, values)

    assert result_values == [3, 2, 1]


def test_get_id_returns_ant_id():
    ant = make_ant(ant_id=7)

    assert ant.get_id() == 7


def test_run_calls_search_with_pheronome(monkeypatch):
    ant = make_ant()
    called_with = {}

    def fake_search(pheronome):
        called_with["pheronome"] = pheronome

    monkeypatch.setattr(ant, "search", fake_search)

    ant.run()

    assert called_with["pheronome"] is ant.pheronome


def test_search_creates_individual_when_configuration_matches_sequance_length(monkeypatch):
    ant = make_ant(sequance=[0, 1])
    monkeypatch.setattr(ant, "create_configuration", lambda index, pheronome: True)

    individual, tabu_list = ant.search(ant.pheronome)

    assert individual is not None
    assert ant.individual is individual
    assert tabu_list == ant.tabu_list


def test_search_returns_none_when_configuration_incomplete(monkeypatch):
    ant = make_ant(sequance=[0, 1, 1, 0])
    monkeypatch.setattr(ant, "create_configuration", lambda index, pheronome: False)

    result = ant.search(ant.pheronome)

    assert result == (None, None)


def test_create_configuration_returns_true_when_index_reaches_end():
    ant = make_ant(sequance=[0, 1])

    assert ant.create_configuration(1, ant.pheronome) is True


def test_create_configuration_returns_true_when_time_limit_exceeded(monkeypatch):
    ant = make_ant(sequance=[0, 1, 1, 0])
    ant.start_time = 0
    monkeypatch.setattr("data.ant.utils.get_time_in_millis", lambda: 20000)

    assert ant.create_configuration(1, ant.pheronome) is True


def test_create_configuration_returns_false_when_no_valid_moves(monkeypatch):
    ant = make_ant(sequance=[0, 1, 1, 0])
    ant.start_time = utils.get_time_in_millis()
    monkeypatch.setattr(ant, "compute_free_energy_of_possible_moves", lambda index: [None, None, None])

    result = ant.create_configuration(1, ant.pheronome)

    assert result is False


def test_create_configuration_recurses_and_returns_true_on_success(monkeypatch):
    ant = make_ant(sequance=[0, 1, 1])
    ant.start_time = utils.get_time_in_millis()
    monkeypatch.setattr(ant, "compute_free_energy_of_possible_moves", lambda index: [1.0, None, None])

    result = ant.create_configuration(1, ant.pheronome)

    assert result is True
    assert len(ant.tabu_list) == 1


def test_add_to_tabu_list_appends_when_new():
    ant = make_ant()
    ant.tabu_list = [0]

    ant.add_to_tabu_list(1, 2)

    assert ant.tabu_list == [0, 2]


def test_add_to_tabu_list_overwrites_existing_index():
    ant = make_ant()
    ant.tabu_list = [0, 1, 2]

    ant.add_to_tabu_list(1, 9)

    assert ant.tabu_list == [0, 9, 2]


def test_get_direction_multiplies_last_coordinate():
    ant = make_ant(sequance=[0, 1, 1])
    ant.vector.set_configuration_at_index(0, complex(1, 0))

    result = ant.get_direction(1, 1)

    assert result == complex(1, 0) * complex(0, 1)


def test_pick_next_moves_sorts_probabilities_descending(monkeypatch):
    ant = make_ant()
    monkeypatch.setattr("data.ant.random.random", lambda: 0.9)

    indexes, values = ant.pick_next_moves([3, 1, 2])

    assert values == [3, 2, 1]
    assert indexes == [0, 2, 1]


def test_compute_probability_of_next_move_normalises_and_flags_invalid():
    ant = Ant(0, [0, 1], [[1, 1, 1]], 1, 1)

    probability = ant.compute_probability_of_next_move(0, [2, 2], [2, None])

    assert probability[0] == 1.0
    assert probability[1] == NO_ROUTE


def test_compute_probability_of_next_move_all_invalid_returns_no_route():
    ant = Ant(0, [0, 1], [[1, 1, 1]], 1, 1)

    probability = ant.compute_probability_of_next_move(0, [2, 2], [None, None])

    assert probability == [NO_ROUTE, NO_ROUTE]


def test_compute_free_energy_of_possible_moves_detects_collision():
    ant = make_ant(sequance=[0, 1, 0, 1])
    ant.vector.clean_configuration()
    ant.vector.set_configuration_at_index(0, complex(1, 0))
    ant.vector.set_configuration_at_index(1, complex(0, 1))
    ant.vector.set_configuration_at_index(2, complex(-1, 0))
    ant.vector.compute_space_configuration(2)

    free_energy = ant.compute_free_energy_of_possible_moves(3)

    assert free_energy[0] is not None
    assert free_energy[1] is None
    assert free_energy[2] is not None


def test_get_individual_and_get_tabu_list_return_state():
    ant = make_ant()
    ant.individual = "individual-placeholder"
    ant.tabu_list = [0, 1, 2]

    assert ant.get_individual() == "individual-placeholder"
    assert ant.get_tabu_list() == [0, 1, 2]


def test_check_valid_move_true_when_not_in_set():
    ant = make_ant()

    assert ant.check_valid_move(complex(5, 5), Counter()) is True


def test_check_valid_move_false_when_in_set():
    ant = make_ant()
    counter = Counter([complex(1, 0)])

    assert ant.check_valid_move(complex(1, 0), counter) is False


def test_verbose_mode_prints_progress(capsys):
    ant = make_ant(sequance=[0, 1])
    ant.verbose = True

    ant.create_configuration(1, ant.pheronome)
    ant.compute_probability_of_next_move(0, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])
    ant.compute_free_energy_of_possible_moves(1)

    out = capsys.readouterr().out
    assert "Create configuration" in out
    assert "Compute probability" in out
    assert "Compute free energy" in out


def test_verbose_mode_false_produces_no_progress_output(capsys):
    ant = make_ant(sequance=[0, 1])
    ant.verbose = False

    ant.create_configuration(1, ant.pheronome)
    ant.compute_probability_of_next_move(0, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])
    ant.compute_free_energy_of_possible_moves(1)

    out = capsys.readouterr().out
    assert "Create configuration" not in out
    assert "Compute probability" not in out
    assert "Compute free energy" not in out
