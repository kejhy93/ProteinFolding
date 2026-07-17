from data.data import Data
from data.vector import Vector


def test_str_includes_sequance_and_hydro_count():
    data = Data([1, 0, 1, 1], 3)

    result = str(data)

    assert "length: 3" in result


def test_get_length_of_vector_returns_sequance_length():
    data = Data([1, 0, 1, 1], 0)

    assert data.get_length_of_vector() == 4


def test_optimize_sequance_delegates_to_vector():
    data = Data([0, 1, 1, 0], 0)

    result = data.optimize_sequance()

    assert result == [1, 1]
    assert data.get_sequance() == [1, 1]


def test_get_vector_returns_underlying_vector():
    data = Data([1, 0, 1], 0)

    assert isinstance(data.get_vector(), Vector)
    assert data.get_vector() is data.vector
