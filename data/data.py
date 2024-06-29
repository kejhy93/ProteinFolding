#! /usr/bin/python3

from data.vector import Vector

class Data:
    def __init__(self, content, index):
        self.vector = Vector(content)

        self.index = index

    def __str__(self):
        s = ""
        s += str(self.vector.get_amino_sequance()) + " length: " + str(self.vector.get_count_of_hydro()) + "\n"

        return s

    def get_length_of_vector(self):
        return len(self.vector.get_amino_sequance())

    def get_count_of_hydro(self):
        return self.vector.get_count_of_hydro()

    def optimize_sequance(self):
        return self.vector.optimize_sequance()

    def get_sequance(self):
        return self.vector.get_amino_sequance()

    def get_vector(self):
        return self.vector

    def get_counter(self):
        return self.index
