from sequance_optimization import check_valid_index, optimize_sequance


def test_check_valid_index_in_range_returns_true():
    assert check_valid_index(0, [1, 0, 1]) is True
    assert check_valid_index(2, [1, 0, 1]) is True


def test_check_valid_index_out_of_range_returns_false():
    assert check_valid_index(-1, [1, 0, 1]) is False
    assert check_valid_index(3, [1, 0, 1]) is False


def test_optimize_sequance_returns_empty_when_entirely_hydrophilic():
    assert optimize_sequance([0, 0, 0]) == []
