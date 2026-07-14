# ProteinFolding
ProteinFolding Problem

Waketime badge

[![wakatime](https://wakatime.com/badge/github/kejhy93/ProteinFolding.svg)](https://wakatime.com/badge/github/kejhy93/ProteinFolding)

Run ./script.py

## Configuration properties

`GeneticsAlgorithm` (`gen_algo/genetics_algorithm.py`) is configured through its constructor. `script.py` shows a typical setup:

```python
solver = GeneticsAlgorithm(
    modify_sequance,          # sequance
    TOTAL_COUNT_OF_GENERATION, # MAX_GENERATION
    SIZE_OF_POPULATION,        # POPULATION_SIZE
    COUNF_OF_MUTATION,         # COUNT_OF_MUTATION_PER_GENERATION
    COUNT_OF_CROSSOVER,        # COUNT_OF_CROSSOVER_PER_GENERATION
    MUTATION_RATE,             # MUTATE_RATE
    CROSSOVER_RATE,            # CROSSOVER_RATE
)
```

| Property | Required | Default | Description |
| --- | --- | --- | --- |
| `sequance` | yes | — | Amino acid sequence to fold, as a list of `0`/`1` values (`1` = hydrophobic). |
| `MAX_GENERATION` | yes | — | Number of generations the algorithm runs for. |
| `POPULATION_SIZE` | yes | — | Number of individuals kept in the population each generation. |
| `COUNT_OF_MUTATION_PER_GENERATION` | yes | — | Number of individuals mutated per generation. |
| `COUNT_OF_CROSSOVER_PER_GENERATION` | yes | — | Number of crossover operations performed per generation. |
| `MUTATE_RATE` | yes | — | Probability used while mutating an individual. |
| `CROSSOVER_RATE` | yes | — | Probability that crossover runs at all in a given generation. |
| `STORE_INDIVIDUALS_PER_GENERATION` | no | `True` | When `True`, the best individual of every generation is appended to `solver.list_individuals`. Set to `False` to skip this bookkeeping (e.g. for long runs where the per-generation history isn't needed) and avoid the associated memory growth. |

Note: `COUNT_OF_HILL_CLIMBING`, `COUNT_OF_SIMULATED_ANNEALING`, `COUNT_OF_ANT_COLONY` and the other tuning constants for the individual optimisation phases (hill climbing, simulated annealing, ant colony) are not constructor arguments — they're module-level constants at the top of `gen_algo/genetics_algorithm.py` and need to be edited there directly. Hill climbing is disabled by default (`IS_HILL_CLIMBING = False` inside `solve()`).
