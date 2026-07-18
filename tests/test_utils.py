from data.data import Data
from data.vector import Vector

import utils


class FakeConfig:
    def __init__(self, configuration):
        self._configuration = configuration

    def get_configuration(self):
        return self._configuration


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


def test_zero_or_one_branches():
    assert utils.zero_or_one("1") == 1
    assert utils.zero_or_one("0") == 0
    assert utils.zero_or_one("x") == 0


def test_append_to_file_creates_folder_and_writes_new_file(tmp_path, monkeypatch):
    result_folder = tmp_path / "result"
    monkeypatch.setattr(utils, "RESULT_FOLDER", str(result_folder))

    utils.append_to_file(FakeConfig([1, 2, 3]), 5.0, 7)

    written_file = result_folder / utils.create_filename(7)
    assert written_file.read_text() == "5.0 [1, 2, 3]\n"


def test_append_to_file_appends_to_existing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(utils, "RESULT_FOLDER", str(tmp_path))
    written_file = tmp_path / utils.create_filename(3)
    written_file.write_text("1.0 [0]\n")

    utils.append_to_file(FakeConfig([9]), 2.0, 3)

    assert written_file.read_text() == "1.0 [0]\n2.0 [9]\n"


def test_create_filesize_set_zero_when_result_folder_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(utils, "RESULT_FOLDER", str(tmp_path / "does-not-exist"))

    assert utils.create_filesize_set([Data([1, 0], 0)]) == [0]


def test_create_filesize_set_zero_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(utils, "RESULT_FOLDER", str(tmp_path))

    assert utils.create_filesize_set([Data([1, 0], 5)]) == [0]


def test_read_configuration_history_returns_empty_when_file_missing(tmp_path):
    result = utils.read_configuration_history(str(tmp_path / "missing.txt"), [1, 0, 1])

    assert result == []


def test_read_configuration_history_reads_and_parses_file(tmp_path):
    amino_sequance = [1, 0, 1]
    original_vector = Vector(amino_sequance)
    original_vector.set_configuration([complex(1, 0), complex(0, 1)])

    history_file = tmp_path / "history.txt"
    history_file.write_text("5.0 " + str(original_vector.get_configuration()))

    history = utils.read_configuration_history(str(history_file), amino_sequance)

    assert len(history) == 1
    assert history[0].get_configuration() == [complex(1, 0), complex(0, 1)]


def test_parse_configuration_history_handles_multiple_lines():
    amino_sequance = [1, 0, 1]
    vector_a = Vector(amino_sequance)
    vector_a.set_configuration([complex(1, 0), complex(0, 1)])
    vector_b = Vector(amino_sequance)
    vector_b.set_configuration([complex(-1, 0), complex(0, -1)])

    content = "5.0 " + str(vector_a.get_configuration()) + "\n" + "3.0 " + str(vector_b.get_configuration())

    history = utils.parse_configuration_history(content, amino_sequance)

    assert len(history) == 2
    assert history[0].get_configuration() == [complex(1, 0), complex(0, 1)]
    assert history[1].get_configuration() == [complex(-1, 0), complex(0, -1)]
