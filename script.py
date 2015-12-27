#! /usr/bin/python3


import time
import calendar

import os

import threading

import math

from vector import Vector
from data import Data
from sequance_optimization import optimize_sequance

from genetics_algorithm import GeneticsAlgorithm

FIRST_AMINO_SEQUANCE = [ 0, 1, 1, 1, 1, 0 ]
SECOND_AMINO_SEQUANCE = [ 1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1 ] 
THIRD_AMINO_SEQUANCE = [ 0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,0,0 ]
FOURTH_AMINO_SEQUANCE = [ 0,0,0,0,0,0,1,1,1,0,0 ]
FIFTH_AMINO_SEQUANCE = [ 0,1,0,0,1,1,0,0,0,0,0,1,0,1,0,1,1,1,1,1,1,1,1,0,1,1,1,0,1,0,1,1,1,1,0,0,0,0,1,1,0,0,0,0,0,1,0,0,0,1,0,0,0,1,1,0,1,1,0,0,1,0,0,0,0,0,1,0,1,1 ]
SIXTH_AMINO_SEQUANCE = [ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0 ]
SEVENTH_AMINO_SEQUANCE = [ 0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0 ]
EIGTH_AMINO_SEQUANCE = [ 0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1 ]
NINETH_AMINO_SEQUANCE = [ 0,1,0,0,0,0 ]
TENTH_AMINO_SEQUANCE = [ 0,0,0,0,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 ]
ELEVENTH_AMINO_SEQUANCE = [ 0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0 ]
TWELETH_AMINO_SEQUANCE = [ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1 ]
THIRTEEN_AMINO_SEQUANCE = [ 1,0,1,0,0,0,1,0,0,1,0,1,0,1,1,1,0,0,1,1,1,0,1,1,1,1,0,0,0,0,1,0,1,1,1,1,0,0,1,0,0,1,1,0,0,1,1,1,1,1,1,0,1,0,0,0,1,0,0,0,0,1,0,0,0,1,0,1,0,1,1,0,0,0,0,1 ]
FOURTEEN_AMINO_SEQUANCE = [ 0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1 ]
FIFTEEN_AMINO_SEQUANCE = [ 1,0,1,1,0 ]

TEST = [ 	FIRST_AMINO_SEQUANCE, SECOND_AMINO_SEQUANCE, THIRD_AMINO_SEQUANCE, FOURTH_AMINO_SEQUANCE, 
			FIFTH_AMINO_SEQUANCE, SIXTH_AMINO_SEQUANCE, SEVENTH_AMINO_SEQUANCE, EIGTH_AMINO_SEQUANCE,
			NINETH_AMINO_SEQUANCE, TENTH_AMINO_SEQUANCE, ELEVENTH_AMINO_SEQUANCE, TWELETH_AMINO_SEQUANCE,
			THIRTEEN_AMINO_SEQUANCE, FOURTEEN_AMINO_SEQUANCE, FIFTEEN_AMINO_SEQUANCE  ]

PATH_TO_TEST_FILE = "testsuite.txt"

INCREASE = 1
DECREASE = 0

def parse ( PATH ):
	content_of_test_file = ""

	with open ( PATH, 'r', encoding="utf-8") as f:
		content_of_test_file = f.read()

	parsed_content = content_of_test_file.split()

	test_set = []
	counter = 0
	for line in parsed_content:
		parsed_line = []
		for number in line:
			parsed_line . append ( int(number ) )

		data = Data ( parsed_line, counter )
		test_set.append ( data )
		counter += 1

	return test_set

def zero_or_one ( number ):
	if number is "1":
		return 1
	else:
		return 0

def sort ( test_set, STYLE ):
	count_of_sorted = 0

	for index in range ( count_of_sorted, len(test_set)) :
		lowest_index = count_of_sorted
		for find_index in range ( count_of_sorted, len(test_set ) ):
			if STYLE == DECREASE:
				if test_set[find_index].get_length_of_vector() > test_set[lowest_index].get_length_of_vector():
					lowest_index = find_index
			else:
				if test_set[find_index].get_length_of_vector() < test_set[lowest_index].get_length_of_vector():
					lowest_index = find_index


		tmp = test_set[index]
		test_set[index] = test_set[lowest_index]
		test_set[lowest_index] = tmp

		count_of_sorted += 1

	return test_set

def append_to_file ( configuration, free_energy, index ):
	if index < 10:
		indexStr = "00"+str(index)
	elif index < 100:
		indexStr = "0"+str(index)
	else:
		indexStr = str(index)

	name_of_file = "result/file_" + indexStr

	if not os.path.exists("result"):
		os.makedirs("result")

	if not os.path.exists(name_of_file):
		with open ( name_of_file, 'w', encoding='utf-8') as f:
			f.write ( str(free_energy) + " " + str(configuration.get_configuration()) + "\n" )
	else:
		with open ( name_of_file, 'a', encoding='utf-8') as f:
			f.write ( str(free_energy) + " " + str(configuration.get_configuration()) + "\n" )

if __name__ == "__main__":

	TEST_FILE = parse ( PATH_TO_TEST_FILE )
	# TEST_FILE_LITTLE = [ TEST_FILE[104] ]

	TEST_FILE = sort ( TEST_FILE, INCREASE )

	start_millis = int(round(time.time() * 1000))
	total_score = 0

	print(TEST_FILE)

	counter = 0
	for protein in TEST_FILE:
		print ( " ======================================================= ")
		modify_sequance = protein.optimize_sequance()

		print ( "Test: ", counter)
		print ( "Protein sequance: ", protein.get_sequance() )

		if not modify_sequance or len(modify_sequance) <= 2:
			minimal_configuration = protein.get_vector()
		else:
			TOTAL_COUNT_OF_GENERATION = 100
			SIZE_OF_POPULATION = 30

			COUNF_OF_MUTATION = 10
			COUNT_OF_CROSSOVER = 5

			MUTATION_RATE = 0.1
			CROSSOVER_RATE = 0.3

			solver = GeneticsAlgorithm ( modify_sequance, TOTAL_COUNT_OF_GENERATION, 
			SIZE_OF_POPULATION, COUNF_OF_MUTATION, COUNT_OF_CROSSOVER, 
			MUTATION_RATE, CROSSOVER_RATE )

			minimal_configuration = solver.solve()

		free_energy = minimal_configuration.compute_free_energy()
		total_score += free_energy

		print ( "Free energy: ", free_energy)

		append_to_file ( minimal_configuration, free_energy, protein.get_counter() )
		minimal_configuration.plot_config()

		counter += 1


	end_millis = int(round(time.time() * 1000))

	print ("Total score: ", total_score/len(TEST_FILE))
	print ("Total time: ", ((end_millis-start_millis)/1000)/60)

	print("Final Result: ", total_score+math.exp(((end_millis-start_millis)/1000)/60))