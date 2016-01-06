#! /usr/bin/python3


import time
import calendar

import os

import threading

import math

import utils
from vector import Vector
from data import Data
from sequance_optimization import optimize_sequance

from genetics_algorithm import GeneticsAlgorithm

PATH_TO_TEST_FILE = "testsuite.txt"

INCREASE = 1
DECREASE = 0


if __name__ == "__main__":

	TEST_FILE = utils.parse ( PATH_TO_TEST_FILE )

	TEST_FILE = utils.sort ( TEST_FILE, INCREASE )

	start_millis = int(round(time.time() * 1000))
	total_score = 0

	# for i in TEST_FILE:
	# 	print(i)

	# TEST_FILE = utils.sort_by_test_size ( TEST_FILE )
	# TEST_FILE = [TEST_FILE[100],TEST_FILE[3]]
	counter = 0
	for protein in TEST_FILE:
		print ( " ======================================================= ")
		modify_sequance = protein.get_sequance()

		print ( "Test: ", protein.get_counter())
		print ( "Counter: ", counter, "/",str(len(TEST_FILE)))
		print ( "Protein sequance: ", protein.get_sequance() )

		if not modify_sequance or protein.get_count_of_hydro() <= 5:
			minimal_configuration = protein.get_vector()
		else:
			TOTAL_COUNT_OF_GENERATION = 100
			SIZE_OF_POPULATION = 30

			COUNF_OF_MUTATION = 4
			COUNT_OF_CROSSOVER = 4

			MUTATION_RATE = 0.1
			CROSSOVER_RATE = 0.7

			solver = GeneticsAlgorithm ( modify_sequance, TOTAL_COUNT_OF_GENERATION,
			SIZE_OF_POPULATION, COUNF_OF_MUTATION, COUNT_OF_CROSSOVER,
			MUTATION_RATE, CROSSOVER_RATE )

			minimal_configuration = solver.solve()

			free_energy = minimal_configuration.compute_free_energy()
			total_score += free_energy

			free_energy_from_file = utils.read_minimal_energy_from_file(protein.get_counter())

			if free_energy_from_file == None:
				free_energy_from_file = -1

			format_string_free_energy = "Free energy: {:10.3f}, \tCurrent optimum: {:10.3f}"
			print ( format_string_free_energy.format(free_energy, free_energy_from_file) )

			utils.append_to_file ( minimal_configuration, free_energy, protein.get_counter() )
			print ( "Test: ", protein.get_counter())

			title_of_notification = "Test " + str(protein.get_counter())
			body_of_notification = "Free energy: {:10.3f}\nBest score from file: {:10.3f}".format(free_energy, free_energy_from_file)

			utils.send_notification ( title_of_notification, body_of_notification )

			minimal_configuration.plot_config()

		counter += 1


	end_millis = int(round(time.time() * 1000))

	print ("Total score: ", total_score/len(TEST_FILE))
	print ("Total time: ", ((end_millis-start_millis)/1000)/60)

	print ("Final Result: ", total_score+math.exp(((end_millis-start_millis)/1000)/60))
