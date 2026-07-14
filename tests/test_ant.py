from data.ant import Ant


def make_ant():
    sequance = [0, 1, 1, 0]
    pheronome = [[0.5, 0.5, 0.5] for _ in range(len(sequance) - 1)]
    return Ant(0, sequance, pheronome, 5, 1)


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
