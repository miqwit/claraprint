"""
In this experiment, the fingerprint is generated from the same audio source, but from two (or more?) claraprints.
Ideally, one is from the chords, and the other from the melody, in order to find some complementarity

For example, if
       FP_ch="abc cbf aba hfg"
   and FP_me="opq rsv wzq qqp",

the final FP will be "abc cbf aba hfg opq rsv wzq qqp".
"""

from utils_experiments import get_all_fingerprints_by_rdb_id_multiple, get_all_fingerprints, fingerprint_from_n_sources_multiple_algos, fingerprint_from_one_random
from experiments.es_helper import es_search, create_index, store_one_fingerprint, generic_score_by_es_search_multiple_algo, es_refresh
from experiments.es_helper import es_search_shingle, create_index_shingle, store_one_fingerprint_shingle
from collections import namedtuple
import numpy as np
from fingerprint import get_letters_set_from_algo

# All parameters are not useful here. It's copied from es_multiple_fp_generated experiment
# algos: It's now a list of algos to combine, for instance ["chord_chordino", "melody_melodia"]
fields   = ['algos', 'duration', 'range_words', 'num_sources', 'num_bests',
            'search_func', 'ingest_func',         'createindex_func', 'rounds', 'combination_mode']
defaults = (None,    120,         [range(3, 4)], [1],            [10, 5, 1],
            es_search,     store_one_fingerprint, create_index,       10,        'union')
Config = namedtuple('Config', fields)
Config.__new__.__defaults__ = defaults

# Num sources
configs_to_run = [
    Config(algos=["chords_chordino", "melody_melodia"], range_words=[range(2, 8)], search_func=es_search_shingle),
    Config(algos=["chords_chordino", "melody_piptrack"], range_words=[range(2, 8)], search_func=es_search_shingle),
    Config(algos=["chords_crema", "melody_melodia"], range_words=[range(2, 8)], search_func=es_search_shingle),
    Config(algos=["chords_crema", "melody_piptrack"], range_words=[range(2, 8)], search_func=es_search_shingle),
    Config(algos=["chords_chordino", "chords_crema"], range_words=[range(2, 8)], search_func=es_search_shingle),
    Config(algos=["melody_melodia", "melody_piptrack"], range_words=[range(2, 8)], search_func=es_search_shingle),
]


# Run experiment
if __name__ == "__main__":

    for config in configs_to_run:
        all_fingerprints_by_rdb_by_algo = get_all_fingerprints_by_rdb_id_multiple(config.duration, config.algos)

        for num_sources in config.num_sources:
            for range_words in config.range_words:
                all_avg_scores = []  # average score from all rounds
                claraprints = [f"{config.duration}s_{a}" for a in config.algos]

                for round in range(1, config.rounds + 1):
                    config.createindex_func(list(range_words)[0], list(range_words)[-1])
                    ytbs_used = []
                    for rdb_id, fgpts in all_fingerprints_by_rdb_by_algo.items():
                        final_fgpt, used_ytb_ids = fingerprint_from_n_sources_multiple_algos(fgpts, num_sources, range_words,
                                                                                             config.combination_mode,
                                                                                             claraprints)
                        ytbs_used.extend(used_ytb_ids)

                        # Store final_fgpt with this rdb_id
                        config.ingest_func(rdb_id, used_ytb_ids, final_fgpt)

                    es_refresh()

                    # Search by each algo used to compute this FP
                    avg_scores = generic_score_by_es_search_multiple_algo(config.search_func,
                                                                          used_ytb_ids=ytbs_used,
                                                                          num_bests=config.num_bests,
                                                                          range_=range_words,
                                                                          all_fingerprints=all_fingerprints_by_rdb_by_algo,
                                                                          claraprints=claraprints,
                                                                          combination_mode=config.combination_mode)

                    all_avg_scores.append(avg_scores)

                # update average scores
                scores_array = np.array(all_avg_scores)
                final_avg = scores_array.mean(axis=0).tolist()

                # Average

                print("algos={},#sources={},dur={},comb_mode={},search_func={},#bests={},ranges={},scores={}".format(
                    config.algos,
                    num_sources,
                    config.duration,
                    config.combination_mode,
                    config.search_func,
                    config.num_bests,
                    str(list(range_words)[0]) + "_" + str(list(range_words)[-1]),
                    " ".join(["{:.2f}".format(r) for r in final_avg])
                ))

    # print("Best score is {:.2f}".format(best_score_exp))
