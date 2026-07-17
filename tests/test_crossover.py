from gen_algo.crossover import (
    check_every_odd_index_swap_crossover,
    check_one_crossover_point,
    check_two_crossover_points,
    crossover,
    crossover_every_odd_index,
    crossover_one_point,
    crossover_two_points,
    do_crossover,
)


class ConfigIndividual:
    def __init__(self, configuration):
        self.configuration = list(configuration)

    def get_configuration(self):
        return self.configuration

    def set_configuration(self, new_configuration):
        self.configuration = new_configuration


class FakeIndividual:
    def __init__(self, free_energy, valid=True, label="", configuration=None):
        self.free_energy = free_energy
        self.valid = valid
        self.label = label
        self.configuration = configuration if configuration is not None else [0, 1, 2, 3]

    def compute_free_energy(self):
        return self.free_energy

    def check_valid_configuration(self):
        return self.valid

    def get_configuration(self):
        return self.configuration


def test_check_every_odd_index_swap_crossover_branches():
    assert check_every_odd_index_swap_crossover(-1, -1) is True
    assert check_every_odd_index_swap_crossover(2, -1) is False
    assert check_every_odd_index_swap_crossover(2, 4) is False


def test_crossover_every_odd_index_swaps_pairs():
    first = ConfigIndividual([1, 2, 3, 4])
    second = ConfigIndividual([5, 6, 7, 8])

    result_first, result_second = crossover_every_odd_index(first, second)

    assert result_first.get_configuration() == [5, 2, 7, 4]
    assert result_second.get_configuration() == [1, 6, 3, 8]


def test_check_one_crossover_point_branches():
    assert check_one_crossover_point(2, -1) is True
    assert check_one_crossover_point(-1, -1) is False
    assert check_one_crossover_point(2, 4) is False


def test_crossover_one_point_swaps_from_index_to_end():
    first = ConfigIndividual([1, 2, 3, 4])
    second = ConfigIndividual([5, 6, 7, 8])

    result_first, result_second = crossover_one_point(first, second, 2)

    assert result_first.get_configuration() == [1, 2, 7, 8]
    assert result_second.get_configuration() == [5, 6, 3, 4]


def test_check_two_crossover_points_branches():
    assert check_two_crossover_points(2, 4) is True
    assert check_two_crossover_points(-1, -1) is False
    assert check_two_crossover_points(2, -1) is False


def test_crossover_two_points_swaps_range():
    first = ConfigIndividual([1, 2, 3, 4])
    second = ConfigIndividual([5, 6, 7, 8])

    result_first, result_second = crossover_two_points(first, second, 1, 3)

    assert result_first.get_configuration() == [1, 6, 7, 4]
    assert result_second.get_configuration() == [5, 2, 3, 8]


def test_crossover_dispatches_to_odd_index_mode():
    first = ConfigIndividual([1, 2, 3, 4])
    second = ConfigIndividual([5, 6, 7, 8])

    result_first, result_second = crossover(first, second, -1, -1)

    assert result_first.get_configuration() == [5, 2, 7, 4]
    assert result_second.get_configuration() == [1, 6, 3, 8]
    assert first.get_configuration() == [1, 2, 3, 4]


def test_crossover_dispatches_to_one_point_mode():
    first = ConfigIndividual([1, 2, 3, 4])
    second = ConfigIndividual([5, 6, 7, 8])

    result_first, result_second = crossover(first, second, 2, -1)

    assert result_first.get_configuration() == [1, 2, 7, 8]
    assert result_second.get_configuration() == [5, 6, 3, 4]


def test_crossover_dispatches_to_two_point_mode():
    first = ConfigIndividual([1, 2, 3, 4])
    second = ConfigIndividual([5, 6, 7, 8])

    result_first, result_second = crossover(first, second, 1, 3)

    assert result_first.get_configuration() == [1, 6, 7, 4]
    assert result_second.get_configuration() == [5, 2, 3, 8]


def test_crossover_returns_unmodified_copies_when_no_mode_matches():
    first = ConfigIndividual([1, 2, 3, 4])
    second = ConfigIndividual([5, 6, 7, 8])

    result_first, result_second = crossover(first, second, 2, 2)

    assert result_first.get_configuration() == [1, 2, 3, 4]
    assert result_second.get_configuration() == [5, 6, 7, 8]


def test_do_crossover_selects_one_point_mode_for_low_probability(monkeypatch):
    original_first = FakeIndividual(10, label="orig-first")
    original_second = FakeIndividual(10, label="orig-second")
    crossed = FakeIndividual(20, label="crossed")
    captured = {}

    def fake_crossover(first, second, first_point, second_point):
        captured["first_point"] = first_point
        captured["second_point"] = second_point
        return crossed, crossed

    monkeypatch.setattr("gen_algo.crossover.random.random", lambda: 0.1)
    monkeypatch.setattr("gen_algo.crossover.crossover", fake_crossover)

    do_crossover(original_first, original_second)

    assert captured["second_point"] == -1
    assert 0 <= captured["first_point"] <= len(original_first.get_configuration())


def test_do_crossover_selects_two_point_mode_for_mid_probability(monkeypatch):
    original_first = FakeIndividual(10, label="orig-first")
    original_second = FakeIndividual(10, label="orig-second")
    crossed = FakeIndividual(20, label="crossed")
    captured = {}

    def fake_crossover(first, second, first_point, second_point):
        captured["first_point"] = first_point
        captured["second_point"] = second_point
        return crossed, crossed

    monkeypatch.setattr("gen_algo.crossover.random.random", lambda: 0.5)
    monkeypatch.setattr("gen_algo.crossover.crossover", fake_crossover)

    do_crossover(original_first, original_second)

    assert captured["second_point"] != -1
    assert captured["second_point"] >= captured["first_point"]


def test_do_crossover_selects_uniform_mode_for_high_probability(monkeypatch):
    original_first = FakeIndividual(10, label="orig-first")
    original_second = FakeIndividual(10, label="orig-second")
    crossed = FakeIndividual(20, label="crossed")
    captured = {}

    def fake_crossover(first, second, first_point, second_point):
        captured["first_point"] = first_point
        captured["second_point"] = second_point
        return crossed, crossed

    monkeypatch.setattr("gen_algo.crossover.random.random", lambda: 0.9)
    monkeypatch.setattr("gen_algo.crossover.crossover", fake_crossover)

    do_crossover(original_first, original_second)

    assert captured["first_point"] == -1
    assert captured["second_point"] == -1


def test_do_crossover_replaces_first_when_valid_and_improved(monkeypatch):
    original_first = FakeIndividual(10, label="orig-first")
    original_second = FakeIndividual(10, label="orig-second")
    crossed_first = FakeIndividual(5, valid=True, label="crossed-first")
    crossed_second = FakeIndividual(20, valid=True, label="crossed-second")

    monkeypatch.setattr("gen_algo.crossover.random.random", lambda: 0.9)
    monkeypatch.setattr("gen_algo.crossover.crossover", lambda a, b, fp, sp: (crossed_first, crossed_second))

    result_first, result_second = do_crossover(original_first, original_second)

    assert result_first.label == "crossed-first"
    assert result_second.label == "orig-second"


def test_do_crossover_keeps_first_when_crossover_invalid(monkeypatch):
    original_first = FakeIndividual(10, label="orig-first")
    original_second = FakeIndividual(10, label="orig-second")
    crossed_first = FakeIndividual(5, valid=False, label="crossed-first")
    crossed_second = FakeIndividual(20, valid=True, label="crossed-second")

    monkeypatch.setattr("gen_algo.crossover.random.random", lambda: 0.9)
    monkeypatch.setattr("gen_algo.crossover.crossover", lambda a, b, fp, sp: (crossed_first, crossed_second))

    result_first, result_second = do_crossover(original_first, original_second)

    assert result_first.label == "orig-first"


def test_do_crossover_replaces_second_when_valid_and_improved(monkeypatch):
    original_first = FakeIndividual(10, label="orig-first")
    original_second = FakeIndividual(10, label="orig-second")
    crossed_first = FakeIndividual(20, valid=True, label="crossed-first")
    crossed_second = FakeIndividual(5, valid=True, label="crossed-second")

    monkeypatch.setattr("gen_algo.crossover.random.random", lambda: 0.9)
    monkeypatch.setattr("gen_algo.crossover.crossover", lambda a, b, fp, sp: (crossed_first, crossed_second))

    result_first, result_second = do_crossover(original_first, original_second)

    assert result_first.label == "orig-first"
    assert result_second.label == "crossed-second"


def test_do_crossover_keeps_second_when_crossover_invalid(monkeypatch):
    original_first = FakeIndividual(10, label="orig-first")
    original_second = FakeIndividual(10, label="orig-second")
    crossed_first = FakeIndividual(20, valid=True, label="crossed-first")
    crossed_second = FakeIndividual(5, valid=False, label="crossed-second")

    monkeypatch.setattr("gen_algo.crossover.random.random", lambda: 0.9)
    monkeypatch.setattr("gen_algo.crossover.crossover", lambda a, b, fp, sp: (crossed_first, crossed_second))

    result_first, result_second = do_crossover(original_first, original_second)

    assert result_second.label == "orig-second"
