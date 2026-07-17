import os

import utils
import visualize_protein_history as vph
from data.data import Data
from data.vector import Vector


class FakeVector:
    def __init__(self, label):
        self.label = label
        self.saved_to = None

    def save_config_to_file(self, filename):
        self.saved_to = filename


def test_visualize_creates_folder_and_saves_each_history_entry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vph, "CONFIGURATION_FOLDER", "configuration_diagram")

    history = [FakeVector("a"), FakeVector("b")]

    vph.visualize(history, 3)

    config_folder = tmp_path / "configuration_diagram"
    base_path = os.path.join("configuration_diagram", utils.create_filename(3))
    assert config_folder.exists()
    assert history[0].saved_to == base_path + "-001"
    assert history[1].saved_to == base_path + "-002"


def test_visualize_skips_makedirs_when_folder_already_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vph, "CONFIGURATION_FOLDER", "configuration_diagram")
    (tmp_path / "configuration_diagram").mkdir()

    vph.visualize([], 1)

    assert (tmp_path / "configuration_diagram").exists()


def test_read_history_of_configuration_of_returns_empty_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(vph, "protein", Data([1, 0, 1], 0), raising=False)

    result = vph.read_history_of_configuration_of(str(tmp_path / "missing.txt"))

    assert result == []


def test_read_history_of_configuration_of_reads_real_history_file(tmp_path, monkeypatch):
    monkeypatch.setattr(vph, "protein", Data([1, 0, 1], 0), raising=False)

    vector = Vector([1, 0, 1])
    vector.set_configuration([complex(1, 0), complex(0, 1)])
    history_file = tmp_path / "history.txt"
    history_file.write_text("5.0 " + str(vector.get_configuration()))

    result = vph.read_history_of_configuration_of(str(history_file))

    assert len(result) == 1
    assert result[0].get_configuration() == [complex(1, 0), complex(0, 1)]
