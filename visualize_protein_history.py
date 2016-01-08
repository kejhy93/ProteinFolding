#! /usr/bin/python3

import os

from vector import Vector
from data import Data

import utils

RESULT_FOLDER = "result"
TEST_SET = "testsuite.txt"

CONFIGURATION_FOLDER = "configuration_diagram"

def visualize ( history, counter ):
	count_of_records = len(history)
	counter_of_diagrams = 1

	path = os.path.join ( CONFIGURATION_FOLDER, utils.create_filename( counter ) )

	if not os.path.exists ( CONFIGURATION_FOLDER):
		os.makedirs(CONFIGURATION_FOLDER)

	for configuration_history in history:
		# configuration_history.plot_config()
		filename = path + "-" + utils.create_index ( counter_of_diagrams )
		print(filename)
		configuration_history.save_config_to_file ( filename )

		counter_of_diagrams += 1

def read_history_of_configuration_of ( path_to_file ):
	all_configuration_history_of_protein = []
	all_configuration_history_of_protein = utils.read_configuration_history ( full_name_to_file, protein.get_sequance() )

	return all_configuration_history_of_protein

if __name__ == "__main__":
	set_of_all_proteins = utils.parse(TEST_SET)
	history = []

	for protein in set_of_all_proteins:

		number_of_file = protein.get_counter()

		full_name_to_file = utils.create_filename( number_of_file )
		full_name_to_file = os.path.join ( RESULT_FOLDER, full_name_to_file )

		history_of_configuration = read_history_of_configuration_of ( full_name_to_file )
		history . append ( history_of_configuration )

	counter = 2

	visualize(history[counter],counter)

	# counter = 0
	# for protein_history in history:
	# 	visualize(protein_history, counter)
	# 	print(" ======== ")
	# 	counter += 1