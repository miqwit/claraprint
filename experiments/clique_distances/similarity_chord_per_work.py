"""
Return an average distance based on a given algorithm (like levensthein) between all pairs in a given clique.

This is not really an experiment but a measure. This will show that melodies are much more distant within a clique
than chords are. This is not testing the distance of works not in that clique.
"""
import json
from compute_fingerprints import distance_levenshtein, distance_commonwords, distance_commonwords_ponderation
import numpy as np

clique_rdb_id = None
cliques = {}

# Consider the claraprints are already computed in the dataset
# Available at piece["recordings"][n]["claraprints"]
duration = 120
algos = ["chords_chordino", "chords_crema", "melody_melodia", "melody_piptrack"]
dataset = json.load(open("../../dataset/dataset_rdb_100.jams.json", "r"))
# dist_algos = [distance_levenshtein, distance_commonwords, distance_commonwords_ponderation]
dist_algos = [distance_levenshtein, distance_commonwords]

for algo in algos:
    all_scores = np.zeros((4, 1))
    scores = np.zeros((len(dist_algos), 100), dtype=float)

    num_work = -1
    for piece in dataset:
        num_work += 1

        clique = [c[f"{duration}s_{algo}"] for c in [r["claraprints"] for r in piece["sandbox"]["recordings"]]]

        for idx_algo, dist_algo in enumerate(dist_algos):
            distances = [
                dist_algo(clique[0], clique[1]),
                dist_algo(clique[0], clique[2]),
                dist_algo(clique[0], clique[3]),
                dist_algo(clique[0], clique[4]),
                dist_algo(clique[1], clique[2]),
                dist_algo(clique[1], clique[3]),
                dist_algo(clique[1], clique[4]),
                dist_algo(clique[2], clique[3]),
                dist_algo(clique[2], clique[4]),
                dist_algo(clique[3], clique[4])
            ]
            scores[idx_algo, num_work] = sum(distances)/len(distances)

    print(algo)
    print([d.__name__ for d in dist_algos])
    print(scores.mean(axis=1))
    print(scores.min(axis=1))
    print(scores.max(axis=1))
    print(scores.std(axis=1))
