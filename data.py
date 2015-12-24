#! /usr/bin/python3

from vector import Vector

class Data:
	def __init__ ( self, content, index ):
		self.vector = Vector ( content )

		self.index = index

	def __str__ ( self ):
		s = ""
		s += str(vector) + "\n"

		return s

	def get_length_of_vector ( self ):
		return len(self.vector.get_amino_sequance())

	def optimize_sequance ( self ):
		return self.vector.optimize_sequance()

	def get_sequance ( self ):
		return self.vector.get_amino_sequance()

	def get_vector ( self ):
		return self.vector

	def get_counter ( self ):
		return self.index
