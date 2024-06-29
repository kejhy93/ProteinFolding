#! /usr/bin/python3

from copy import deepcopy

from data.vector import Vector


class Individual:
    def __init__(self, sequance):
        self.verbose = False

        if self.verbose:
            print("Individual -> init")

        self.vector = Vector(sequance)
        self.free_energy = None

    def get_individual(self):
        """
        Get genotype  ( vector )
        """
        return self.vector

    def get_configuration(self):
        """
        Get configuration of individual
        """
        return self.vector.get_configuration()

    def set_individual(self, new_vector):
        """
        Set new genotype
        """
        self.vector = deepcopy(new_vector)

    def set_configuration(self, new_config):
        """
        Set configuration of individual
        """
        self.vector.set_configuration(deepcopy(new_config))

    def compute_free_energy(self):
        free_energy = self.vector.compute_free_energy()

        self.free_energy = free_energy

        return free_energy

    def get_free_energy(self):
        if not self.free_energy:
            self.compute_free_energy()

        return self.free_energy

    def check_valid_configuration(self):
        return self.vector.check_valid_configuration()

    def __str__(self):
        if self.verbose:
            print("Individual -> print")

        res = ""

        res += "Free energy: " + str(self.vector.compute_free_energy()) + " "
        res += str(self.vector)

        return res
    
    def __eq__(self, other_individual): 
        
        self_vector = self.get_individual
        other_vector = other_individual.get_individual
        
        return self_vector.__eq__(other_vector)