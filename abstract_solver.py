#! /usr/bin/python3

from data.vector import Vector


class AbstractSolver:
    def __init__(self, sequance):
        self.verbose = False

        if self.verbose:
            print("AbstractSolver -> init")

        self.sequance = sequance
        self.result_vector = Vector(self.sequance)

    def solve(self):
        if self.verbose:
            print("AbstractSolver -> solve ")
