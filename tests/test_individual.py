from data.individual import Individual


def test_get_configuration_returns_vector_configuration():
    individual = Individual([0, 1, 1, 0])

    assert individual.get_configuration() == individual.vector.get_configuration()


def test_set_configuration_updates_vector_configuration():
    individual = Individual([0, 1, 1, 0])
    new_config = [complex(1, 0), complex(0, 1), complex(1, 0)]

    individual.set_configuration(new_config)

    assert individual.get_configuration() == new_config


def test_str_verbose_prints_message(capsys):
    individual = Individual([0, 1, 1, 0])
    individual.verbose = True

    str(individual)

    assert "Individual -> print" in capsys.readouterr().out


def test_eq_returns_false_when_other_is_none():
    individual = Individual([0, 1, 1, 0])

    assert (individual == None) is False


def test_eq_true_for_individuals_with_same_sequance():
    first = Individual([0, 1, 1, 0])
    second = Individual([0, 1, 1, 0])

    assert first == second


def test_eq_false_for_individuals_with_different_sequance():
    first = Individual([0, 1, 1, 0])
    second = Individual([1, 1, 1, 0])

    assert not (first == second)
