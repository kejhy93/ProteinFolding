import os
import runpy

SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "script.py")


class FakeVector:
    def __init__(self, free_energy):
        self._free_energy = free_energy
        self.plotted = False

    def compute_free_energy(self):
        return self._free_energy

    def plot_config(self):
        self.plotted = True


class FakeGeneticsAlgorithm:
    instances = []

    def __init__(self, *args, **kwargs):
        FakeGeneticsAlgorithm.instances.append(args)
        self._result = FakeVector(42.0)

    def solve(self):
        return self._result


def write_testsuite(tmp_path):
    # First line: 0 hydrophobic residues -> takes the "skip GA" branch.
    # Second line: 15 hydrophobic residues -> takes the "run GA" branch.
    testsuite = tmp_path / "testsuite.txt"
    testsuite.write_text("00000\n" + "1" * 15 + "\n")
    return testsuite


def test_script_runs_pipeline_skips_short_sequences_and_solves_long_ones(monkeypatch, tmp_path, capsys):
    write_testsuite(tmp_path)
    monkeypatch.chdir(tmp_path)

    FakeGeneticsAlgorithm.instances = []
    monkeypatch.setattr("gen_algo.genetics_algorithm.GeneticsAlgorithm", FakeGeneticsAlgorithm)

    appended = []
    monkeypatch.setattr(
        "utils.append_to_file",
        lambda configuration, free_energy, index: appended.append((free_energy, index)),
    )
    monkeypatch.setattr("utils.read_minimal_energy_from_file", lambda protein_id: None)

    runpy.run_path(SCRIPT_PATH, run_name="__main__")

    out = capsys.readouterr().out

    # Only the 15-hydrophobic-residue sequence should have gone through the GA solver.
    assert len(FakeGeneticsAlgorithm.instances) == 1
    assert FakeGeneticsAlgorithm.instances[0][0] == [1] * 15

    # append_to_file is only called for the GA-solved sequence, with its free energy.
    assert appended == [(42.0, 1)]

    assert "Current optimum:     -1.000" in out
    assert "Total score:  21.0" in out
    assert "Final Result:" in out


def test_script_reports_existing_optimum_from_history_file(monkeypatch, tmp_path, capsys):
    write_testsuite(tmp_path)
    monkeypatch.chdir(tmp_path)

    FakeGeneticsAlgorithm.instances = []
    monkeypatch.setattr("gen_algo.genetics_algorithm.GeneticsAlgorithm", FakeGeneticsAlgorithm)
    monkeypatch.setattr("utils.append_to_file", lambda configuration, free_energy, index: None)
    monkeypatch.setattr("utils.read_minimal_energy_from_file", lambda protein_id: 7.5)

    runpy.run_path(SCRIPT_PATH, run_name="__main__")

    out = capsys.readouterr().out

    assert "Current optimum:      7.500" in out
