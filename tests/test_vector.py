from collections import Counter

from data.vector import Vector


def make_vector(sequance=None, configuration=None):
    if sequance is None:
        sequance = [1, 0, 1, 1]

    vector = Vector(sequance)

    if configuration is not None:
        vector.set_configuration(configuration)

    return vector


def test_clean_configuration_empties_list():
    vector = make_vector()
    assert vector.configuration != []

    vector.clean_configuration()

    assert vector.configuration == []


def test_update_space_configuration_counter_matches_compute():
    vector = make_vector(configuration=[complex(1, 0), complex(0, 1), complex(1, 0)])

    vector.update_space_configuration_counter()

    assert vector.space_configuration_counter == Counter(vector.space_configuration)


def test_check_space_configuration_counter_true_when_no_collision():
    vector = make_vector(sequance=[1, 0, 1], configuration=[complex(1, 0), complex(0, 1)])

    assert vector.check_space_configuration_counter(complex(0, 1), 0) is True


def test_check_space_configuration_counter_false_when_collision():
    vector = make_vector(sequance=[1, 0, 1], configuration=[complex(1, 0), complex(0, 1)])

    assert vector.check_space_configuration_counter(complex(-1, 0), 0) is False


def test_print_config_handles_all_directions_and_default():
    vector = make_vector()

    assert vector.print_config(complex(1, 0)) == "1"
    assert vector.print_config(complex(-1, 0)) == "-1"
    assert vector.print_config(complex(0, 1)) == "i"
    assert vector.print_config(complex(0, -1)) == "-i"
    assert vector.print_config(complex(2, 2)) == ""


def test_check_valid_of_configuration_true_when_no_overlap():
    vector = make_vector()
    vector.space_configuration = [complex(0, 0), complex(1, 0), complex(1, 1)]

    assert vector.check_valid_of_configuration() is True


def test_check_valid_of_configuration_false_when_overlap():
    vector = make_vector()
    vector.space_configuration = [complex(0, 0), complex(1, 0), complex(0, 0)]

    assert vector.check_valid_of_configuration() is False


def test_check_valid_configuration_returns_false_on_overlap():
    vector = make_vector(sequance=[1, 0, 1], configuration=[complex(1, 0), complex(-1, 0)])

    assert vector.check_valid_configuration() is False


def test_set_configuration_at_index_appends_when_out_of_range():
    vector = make_vector(sequance=[1, 0], configuration=[])

    vector.set_configuration_at_index(0, complex(1, 0))

    assert vector.configuration == [complex(1, 0)]


def test_set_configuration_at_index_overwrites_when_in_range():
    vector = make_vector(sequance=[1, 0, 1], configuration=[complex(1, 0), complex(0, 1)])

    vector.set_configuration_at_index(1, complex(-1, 0))

    assert vector.configuration == [complex(1, 0), complex(-1, 0)]


def test_get_configuration_at_index_returns_value():
    vector = make_vector(configuration=[complex(1, 0), complex(0, 1)])

    assert vector.get_configuration_at_index(1) == complex(0, 1)


def test_multiply_configuration_scales_from_index():
    vector = make_vector(configuration=[complex(1, 0), complex(0, 1), complex(1, 0)])

    vector.multiply_configuration(complex(-1, 0), index=1)

    assert vector.configuration == [complex(1, 0), complex(0, -1), complex(-1, 0)]


def test_multiply_configuration_verbose_prints(capsys):
    vector = make_vector(configuration=[complex(1, 0)])
    vector.verbose = True

    vector.multiply_configuration(complex(-1, 0))

    out = capsys.readouterr().out
    assert "Original configration" in out
    assert "Updated configration" in out


def test_optimize_sequance_trims_and_extends_configuration():
    vector = make_vector(sequance=[0, 1, 1, 0])
    original_len = len(vector.configuration)

    result = vector.optimize_sequance()

    assert result == [1, 1]
    assert vector.sequance == [1, 1]
    assert len(vector.configuration) == original_len + (len(result) - 1)


def test_get_space_configuration_set_returns_counter():
    vector = make_vector(configuration=[complex(1, 0)])
    vector.update_space_configuration_counter()

    assert vector.get_space_configuration_set() == vector.space_configuration_counter


def test_get_space_configuration_computes_when_empty():
    vector = make_vector(sequance=[1, 0, 1], configuration=[complex(1, 0), complex(0, 1)])
    vector.space_configuration = []

    result = vector.get_space_configuration(index=1)

    assert result == [complex(0, 0), complex(1, 0)]


def test_get_space_configuration_returns_full_when_index_none():
    vector = make_vector(configuration=[complex(1, 0), complex(0, 1)])
    vector.compute_space_configuration()

    result = vector.get_space_configuration()

    assert result == vector.space_configuration


def test_get_axis_covers_min_and_max_expansion_in_all_directions():
    vector = make_vector()
    vector.space_configuration = [complex(-2, 0), complex(3, 0), complex(0, -3), complex(0, 4)]

    axis = vector.get_axis()

    assert axis == (-3, 4, -4, 5)


def test_compute_space_configuration_stops_at_index():
    vector = make_vector(sequance=[1, 0, 1, 1], configuration=[complex(1, 0), complex(0, 1), complex(1, 0)])

    result = vector.compute_space_configuration(1)

    assert result == [complex(0, 0), complex(1, 0), complex(1, 1)]


def test_compute_space_configuration_verbose_prints(capsys):
    vector = make_vector(configuration=[complex(1, 0)])
    vector.verbose = True

    vector.compute_space_configuration()

    assert "Space configuration" in capsys.readouterr().out


def test_compute_free_energy_uses_given_space_config():
    vector = make_vector(sequance=[1, 1], configuration=[complex(1, 0)])
    space_conf = [complex(0, 0), complex(1, 0)]

    energy = vector.compute_free_energy(index=0, space_config=space_conf)

    assert energy == 1.0


def test_compute_free_energy_defaults_to_full_sequance():
    vector = make_vector(sequance=[1, 1], configuration=[complex(1, 0)])

    energy = vector.compute_free_energy()

    assert energy == 1.0


def test_compute_free_energy_verbose_prints(capsys):
    vector = make_vector(sequance=[1, 1], configuration=[complex(1, 0)])
    vector.verbose = True

    vector.compute_free_energy()

    assert "Free energy" in capsys.readouterr().out


def test_update_free_energy_adds_distance_to_new_point():
    vector = make_vector(sequance=[1, 1, 1, 1], configuration=[complex(1, 0), complex(1, 0), complex(1, 0)])
    space_conf = [complex(0, 0), complex(1, 0), complex(2, 0), complex(3, 0)]

    result = vector.update_free_energy(old_free_energy=5.0, index=3, space_conf=space_conf)

    assert result == 7.0


def test_eq_compares_sequance_elementwise():
    vector_a = make_vector(sequance=[1, 0, 1])
    vector_b = make_vector(sequance=[1, 0, 1])
    vector_c = make_vector(sequance=[1, 1, 1])

    assert vector_a == vector_b
    assert not (vector_a == vector_c)


def test_save_config_to_file_writes_png(tmp_path):
    vector = make_vector(sequance=[1, 0, 1, 1], configuration=[complex(1, 0), complex(0, 1), complex(1, 0)])
    output_path = tmp_path / "plot"

    vector.save_config_to_file(str(output_path))

    assert (tmp_path / "plot.png").exists()


def test_plot_config_runs_with_and_without_index(monkeypatch):
    vector = make_vector(sequance=[1, 0, 1, 1], configuration=[complex(1, 0), complex(0, 1), complex(1, 0)])
    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None)

    vector.plot_config(index=1)
    vector.plot_config()
