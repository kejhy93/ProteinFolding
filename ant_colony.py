#! /usr/bin/python3

import random

from ant import Ant

class AntColony:
	def __init__ ( self, count_of_ants, sequance ):
		self.verbose = True

		if self.verbose:
			print ( "Ant Colony -> Init")

		self.COUNT_OF_ANTS = count_of_ants
		self.ants = []
		self.sequance = sequance
		for ant_index in range ( self.COUNT_OF_ANTS ):
			self.ants . append ( Ant(ant_index, sequance ))

		self.pheronome = []

		self.pheronome = self.init_pheronome_trails ()

	def init_pheronome_trails ( self ):
		"""
		Init pheronome trails
		"""
		pheronome = []
		for index in range(len(self.sequance)-1):
			pheronome.append ( [self.init_pheronome(), self.init_pheronome(), self.init_pheronome()] )

		return pheronome

	def init_pheronome ( self ):
		"""
		Init pheronome
		"""
		return random.random()

	def search ( self ):
		"""
		Create new solution by ant 
		"""
		new_individuals = []
		for ant in self.ants:
			new_individuals.append(ant.search( self.pheronome ))

		print("Individuals from ant: ",new_individuals)
		return new_individuals