from gen_algo.hill_climbing import do_hill_climbing, hill_climbing


class FakeIndividual:
    def __init__(self, free_energy):
        self.free_energy = free_energy

    def get_free_energy(self):
        return self.free_energy

    def compute_free_energy(self):
        return self.free_energy


def test_do_hill_climbing_delegates_to_hill_climbing(monkeypatch):
    individual = FakeIndividual(10)
    monkeypatch.setattr(
        "gen_algo.hill_climbing.do_mutation",
        lambda ind: FakeIndividual(10),
    )

    result = do_hill_climbing(individual, count_of_iteration=3, count_of_neighbor=2)

    assert result is individual


def test_hill_climbing_terminates_immediately_when_no_improvement(monkeypatch):
    call_count = {"n": 0}

    def fake_do_mutation(individual):
        call_count["n"] += 1
        return FakeIndividual(individual.get_free_energy())

    monkeypatch.setattr("gen_algo.hill_climbing.do_mutation", fake_do_mutation)

    individual = FakeIndividual(10)
    result = hill_climbing(individual, iteration=5, count_of_neighour=3)

    assert result is individual
    assert call_count["n"] == 3


def test_hill_climbing_recurses_until_iteration_exhausted(monkeypatch):
    call_count = {"n": 0}

    def fake_do_mutation(individual):
        call_count["n"] += 1
        return FakeIndividual(individual.get_free_energy() - 1)

    monkeypatch.setattr("gen_algo.hill_climbing.do_mutation", fake_do_mutation)

    individual = FakeIndividual(10)
    result = hill_climbing(individual, iteration=2, count_of_neighour=1)

    assert call_count["n"] == 3
    assert result.get_free_energy() == 9
