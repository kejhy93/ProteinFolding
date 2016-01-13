__author__ = 'hejnaluk'


class ProteinFolding:
	def __init__(self):
		"""
		Init protein folding solver
		:return:
		"""
		self.debug_verbose = True

		if self.debug_info():
			print("ProteinFolding Solver -> INIT")

	def parse(self, file_to_parse):
		"""
		Parse amino sequances from given file
		:param file_to_parse: Path to file with amino sequances
		:return:
		"""
		if self.debug_info():
			print("ProteinFolding Solver -> PARSE")

	def solve(self):
		"""
		Solve all amino sequances
		:return:
		"""
		if self.debug_info():
			print("ProteinFolding Solver -> SOLVE")

	def debug_info(self):
		"""
		Check if print debug info
		:return:
		"""
		if self.debug_verbose:
			return True
		else:
			return False
