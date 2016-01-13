__author__ = 'hejnaluk'

from protein_folding import ProteinFolding

if __name__ == "__main__":

	PATH_TO_AMINO_SEQUANCES = "amino_sequances"

	protein_folding_solver = ProteinFolding()

	protein_folding_solver.parse(PATH_TO_AMINO_SEQUANCES)

	results = protein_folding_solver.solve()

	counter = 0
	if results:
		for result in results:
			print("Result of ", counter, ". amino sequance: ", result)
