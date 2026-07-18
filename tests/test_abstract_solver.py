from abstract_solver import AbstractSolver


def test_init_stores_sequance_and_builds_result_vector():
    solver = AbstractSolver([0, 1, 1, 0])

    assert solver.sequance == [0, 1, 1, 0]
    assert solver.result_vector.get_amino_sequance() == [0, 1, 1, 0]


def test_solve_verbose_prints_message(capsys):
    solver = AbstractSolver([0, 1, 1, 0])
    solver.verbose = True

    solver.solve()

    assert "AbstractSolver -> solve" in capsys.readouterr().out


def test_solve_silent_by_default(capsys):
    solver = AbstractSolver([0, 1, 1, 0])

    solver.solve()

    assert capsys.readouterr().out == ""
