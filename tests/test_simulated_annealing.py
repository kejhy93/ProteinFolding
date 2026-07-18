from math import exp

from gen_algo.simulated_annealing import (
    COOLING_RATE_OK,
    COOLING_RATE_TOO_HIGH,
    COOLING_RATE_TOO_LOW,
    TEMPERATURE_INVALID,
    TEMPERATURE_VALID,
    acceptance_probability,
    check_temperatures,
    check_valid_of_cooling_rate,
    do_simulated_annealing,
    update_temperature,
)


class FakeIndividual:
    def __init__(self, free_energy, valid=True, label=""):
        self.free_energy = free_energy
        self.valid = valid
        self.label = label

    def get_free_energy(self):
        return self.free_energy

    def check_valid_configuration(self):
        return self.valid

    def __eq__(self, other):
        return isinstance(other, FakeIndividual) and self.label == other.label

    def __repr__(self):
        return "FakeIndividual(%s)" % self.label


class FakeMutation:
    def __init__(self):
        self.call_count = 0

    def __call__(self, current_solution, rate, temperature, initial_temperature):
        self.call_count += 1
        if self.call_count == 1:
            # Same free energy as the starting individual, but a different
            # object -> exercises the "Energy are wrong" diagnostic branch.
            return FakeIndividual(free_energy=10.0, valid=True, label="mutated-1")
        return FakeIndividual(free_energy=3.0, valid=True, label="mutated-%d" % self.call_count)


def test_check_valid_of_cooling_rate_branches():
    assert check_valid_of_cooling_rate(1.0) == COOLING_RATE_TOO_HIGH
    assert check_valid_of_cooling_rate(1.5) == COOLING_RATE_TOO_HIGH
    assert check_valid_of_cooling_rate(0.0) == COOLING_RATE_TOO_LOW
    assert check_valid_of_cooling_rate(-0.5) == COOLING_RATE_TOO_LOW
    assert check_valid_of_cooling_rate(0.5) == COOLING_RATE_OK


def test_check_temperatures_branches():
    assert check_temperatures(1, 10) == TEMPERATURE_INVALID
    assert check_temperatures(10, 1) == TEMPERATURE_VALID
    assert check_temperatures(10, 10) == TEMPERATURE_VALID


def test_acceptance_probability_returns_one_when_new_energy_is_better():
    assert acceptance_probability(energy=10, new_energy=5, temperature=100) == 1


def test_acceptance_probability_uses_boltzmann_formula_when_new_energy_is_worse():
    result = acceptance_probability(energy=5, new_energy=10, temperature=100)

    assert result == exp((5 - 10) / 100)
    assert 0 < result < 1


def test_update_temperature_multiplies_by_cooling_rate():
    assert update_temperature(100, 0.9) == 90.0


def test_do_simulated_annealing_returns_none_when_cooling_rate_too_high(capsys):
    result = do_simulated_annealing(FakeIndividual(1.0), cooling_rate=1.0)

    assert result is None
    assert "Cooling rate is equal or higher then 1" in capsys.readouterr().out


def test_do_simulated_annealing_returns_none_when_cooling_rate_too_low(capsys):
    result = do_simulated_annealing(FakeIndividual(1.0), cooling_rate=0.0)

    assert result is None
    assert "Cooling rate is equal or lower then 0" in capsys.readouterr().out


def test_do_simulated_annealing_returns_none_when_temperature_invalid(capsys):
    result = do_simulated_annealing(FakeIndividual(1.0), cooling_rate=0.5, initial_temperature=1, min_temperature=10)

    assert result is None
    assert "Temperature invalid" in capsys.readouterr().out


def test_do_simulated_annealing_runs_cooling_loop_and_accepts_moves(monkeypatch, capsys):
    individual = FakeIndividual(free_energy=10.0, label="start")
    fake_mutation = FakeMutation()

    monkeypatch.setattr("gen_algo.simulated_annealing.do_mutation", fake_mutation)
    monkeypatch.setattr("gen_algo.simulated_annealing.random.random", lambda: 0.0)
    monkeypatch.setattr("gen_algo.simulated_annealing.verbose", True)

    result = do_simulated_annealing(individual, cooling_rate=0.5, initial_temperature=10, min_temperature=1)

    out = capsys.readouterr().out
    assert "Simulated Annealing" in out
    assert "Energy are wrong" in out
    assert fake_mutation.call_count == 4
    assert result.label == "mutated-4"
