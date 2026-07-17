from data.population import Population
from data.vector import Vector


class FakeIndividual:
    def __init__(self, free_energy):
        self._free_energy = free_energy

    def get_free_energy(self):
        return self._free_energy


def test_init_population_verbose_prints(capsys):
    population = Population(2)
    population.verbose = True
    vector = Vector([0, 1, 1, 0])

    population.init_population(vector)

    assert "Init of population" in capsys.readouterr().out
    assert population.count_of_individuals() == 2


def test_exist_lower_value_in_finds_first_lower_value():
    population = Population(1)

    assert population.exist_lower_value_in(5, [10, 3, 8]) == (True, 1)


def test_exist_lower_value_in_returns_false_when_none_lower():
    population = Population(1)

    assert population.exist_lower_value_in(5, [10, 8, 6]) == (False, -1)


def test_move_shifts_and_inserts():
    population = Population(1)

    new_index, new_values = population.move([0, 1, 2], [10, 20, 30], 1, 99, 15)

    assert new_values == [10, 15, 20]
    assert new_index == [0, 99, 1]


def test_find_worst_individuals_tracks_highest_energy_individuals():
    population = Population(5)
    population.individuals = [FakeIndividual(e) for e in [5, 100, 50, 200, 10]]

    worst = population.find_worst_individuals(2)

    assert worst == [3, 1]


def test_str_prints_verbose_message_and_lists_individuals(capsys):
    population = Population(1)
    population.verbose = True
    population.individuals = [FakeIndividual(5)]

    result = str(population)

    out = capsys.readouterr().out
    assert "Print population" in out
    assert "Individual 1:" in result
