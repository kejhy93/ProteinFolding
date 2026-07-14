from data.data import Data

import utils


def test_create_index_pads_with_zeros():
    assert utils.create_index(5) == "005"
    assert utils.create_index(42) == "042"
    assert utils.create_index(123) == "123"


def test_sort_decrease_orders_by_hydro_count_descending():
    test_set = [Data([1], 0), Data([1, 1], 1), Data([1, 1, 1], 2)]

    sorted_set = utils.sort(test_set, utils.DECREASE)

    assert [d.get_count_of_hydro() for d in sorted_set] == [3, 2, 1]


def test_sort_increase_orders_by_hydro_count_ascending():
    test_set = [Data([1, 1, 1], 0), Data([1, 1], 1), Data([1], 2)]

    sorted_set = utils.sort(test_set, utils.INCREASE)

    assert [d.get_count_of_hydro() for d in sorted_set] == [1, 2, 3]


def test_parse_reads_binary_sequences_from_file(tmp_path):
    test_file = tmp_path / "testsuite.txt"
    test_file.write_text("101\n0110\n")

    result = utils.parse(str(test_file))

    assert [d.get_sequance() for d in result] == [[1, 0, 1], [0, 1, 1, 0]]


def test_read_minimal_energy_from_file_returns_none_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(utils, "RESULT_FOLDER", str(tmp_path / "does-not-exist"))

    assert utils.read_minimal_energy_from_file(999) is None


def test_read_minimal_energy_from_file_returns_minimum(tmp_path, monkeypatch):
    monkeypatch.setattr(utils, "RESULT_FOLDER", str(tmp_path))
    filename = utils.create_filename(7)
    (tmp_path / filename).write_text("5.0 [1, 2]\n2.5 [3, 4]\n7.0 [5, 6]\n")

    assert utils.read_minimal_energy_from_file(7) == 2.5


def test_sort_by_test_size_orders_by_result_file_length(tmp_path, monkeypatch):
    monkeypatch.setattr(utils, "RESULT_FOLDER", str(tmp_path))

    small = Data([1, 0], 0)
    large = Data([1, 1], 1)

    (tmp_path / utils.create_filename(0)).write_text("one line\n")
    (tmp_path / utils.create_filename(1)).write_text("line one\nline two\nline three\n")

    sorted_test_file = utils.sort_by_test_size([small, large])

    assert sorted_test_file[0] is small
    assert sorted_test_file[1] is large
