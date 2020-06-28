"""
In this experiment, the fingerprint is generated from two or more audio sources. The most recurring words from one
fingerprint to the other are used to generate the final fingerprint.

For example, if
       FP1="tif ift umn cfc"
   and FP2="tij ift umn ffc",

the final FP will be "ift umn" in case of intersection or "tif ift ift umn umn cfc tij ffc" in case of union (it's a
parameter to the experiment: combination_mode)
"""

from utils_experiments import get_all_fingerprints_by_rdb_id, get_all_fingerprints, fingerprint_from_n_sources, fingerprint_from_one_random
from experiments.es_helper import es_search, create_index, store_one_fingerprint, generic_score_by_es_search, es_refresh
from collections import namedtuple
import numpy as np
import time

"""
Description of a config:
- algo: which algo to run. Can be chords_chordino, chords_crema, melody_melodia, melody_piptrack
- duration: which samples to use. In these experiment, only 30s and 120s are precomputed. Use int 30 or 120.
- letters_to_use: set of letters to use for a claraprint. Is defined in fingerprints.py. Traditionally, 1 is for 
  chords and 3 is for melody. 2 is unused. It is useful to use different sets for combinatory fingerprints 
  (chords + melody)
- range_words: for the given configuration, the different sizes of words to use. Contains a list of range objects.
- num_sources: how many audio files to use to generate one claraprint
- num_bests: will display in the results how many times a fingerprint was found in the N top values of a search result.
  Contains a list. For example [10, 5, 1] will display the presence of a given claraprint in the top 10, top 5 and top 1
  (= is it the first result) of a search.
- fingerprint_from_one_source: reference to a function to mix fingerprints from different sources. Such function, like
  fingerprint_from_n_sources, can be found in the utils_experiments.py file. You can write your own.
- search_func: reference to a function to run a search query against the elasticsearch. Such functions are to be found
  in the file experiments.es_helper.py.
- ingest_func: reference to a function to ingest a document (claraprint) inside the Elasticsearch index. Such functions
  are to be found in the file experiments.es_helper.py.
- createindex_func: reference to a function to create the Elasticsearch index.
- rounds: number of times the configuration is run. Because the works are taken randomly in the dataset, it's worth
  running the config several times to consolidate the result.
- combination_mode: when several fingerprints are used (num_sources > 1), how do we combine the fingerprint, can be
  'union' or 'intersection'. This is implemented in the fingerprint_from_n_sources function.
"""
fields   = ['algo', 'duration', 'letters_to_use', 'range_words', 'num_sources', 'num_bests', 'fingerprint_from_one_source',
            'search_func', 'ingest_func',         'createindex_func', 'rounds', 'combination_mode']
defaults = (None,   120,        None,             [range(3, 4)], [1],            [10, 5, 1], fingerprint_from_n_sources,
            es_search,     store_one_fingerprint, create_index,       10,        'union')
Config = namedtuple('Config', fields)
Config.__new__.__defaults__ = defaults

# Algo comparison
configs_to_run = [
    Config(algo="chords_chordino", duration=120, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1]),
    Config(algo="chords_crema", duration=120, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1]),
    Config(algo="melody_melodia", duration=120, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1]),
    Config(algo="melody_piptrack", duration=120, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1])
]

# Duration comparison
# configs_to_run = [
#     Config(algo="chords_chordino", duration=30, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1]),
#     Config(algo="chords_crema", duration=30, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1]),
#     Config(algo="melody_melodia", duration=30, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1]),
#     Config(algo="melody_piptrack", duration=30, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1]),
#     Config(algo="chords_chordino", duration=120, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1]),
#     Config(algo="chords_crema", duration=120, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1]),
#     Config(algo="melody_melodia", duration=120, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1]),
#     Config(algo="melody_piptrack", duration=120, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1]),
# ]

# Range (1 source)
# all_ranges = [range(2, 9), range(2, 10), range(2, 11), range(2, 12)]
# configs_to_run = [
#     Config(algo="chords_chordino", letters_to_use=1, range_words=all_ranges),
#     Config(algo="chords_crema", letters_to_use=1, range_words=all_ranges),
#     Config(algo="melody_melodia", letters_to_use=3, range_words=all_ranges),
#     Config(algo="melody_piptrack", letters_to_use=3, range_words=all_ranges)
# ]

# Elasticsearch shingling + min_hash
# configs_to_run = [
#     Config(algo="chords_chordino", duration=120, letters_to_use=1, range_words=[range(3, 4), range(3, 5), range(3, 6), range(3, 7), range(2, 6)], num_sources=[1],
#            search_func=es_search_shingle, ingest_func=store_one_fingerprint_shingle, createindex_func=create_index_shingle,
#            fingerprint_from_one_source=fingerprint_from_one_random),
#     Config(algo="chords_chordino", duration=120, letters_to_use=1, range_words=[range(3, 4), range(2, 7)],
#            num_sources=[1]),
# ]

# Num sources
# configs_to_run = [
#     Config(algo="chords_chordino", duration=120, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1, 2, 3, 4]),
#     Config(algo="chords_crema", duration=120, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1, 2, 3, 4]),
#     Config(algo="melody_melodia", duration=120, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1, 2, 3, 4]),
#     Config(algo="melody_piptrack", duration=120, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1, 2, 3, 4])
# ]


# Run experiment
if __name__ == "__main__":

    for config in configs_to_run:
        all_fingerprint = get_all_fingerprints(config.duration, config.algo)
        all_fingerprints_by_rdb = get_all_fingerprints_by_rdb_id(config.duration, config.letters_to_use, config.algo, all_fingerprint)
        for num_sources in config.num_sources:
            for range_words in config.range_words:
                all_avg_scores = []  # average score from all rounds
                avg_time_insertion = 0
                avg_time_query = 0

                for round in range(1, config.rounds + 1):
                    config.createindex_func(list(range_words)[0], list(range_words)[-1])
                    ytbs_used = []
                    for rdb_id, fgpts in all_fingerprints_by_rdb.items():
                        if num_sources == 1:
                            final_fgpt, used_ytb_ids = config.fingerprint_from_one_source(fgpts, num_sources, range_words, config.combination_mode)
                        else:
                            final_fgpt, used_ytb_ids = fingerprint_from_n_sources(fgpts, num_sources, range_words, config.combination_mode)
                            ytbs_used.extend(used_ytb_ids)

                        # Store final_fgpt with this rdb_id
                        t1 = time.time()
                        config.ingest_func(rdb_id, used_ytb_ids, final_fgpt)
                        avg_time_insertion += (time.time() - t1)
                    avg_time_insertion /= len(all_fingerprints_by_rdb.items())

                    es_refresh()
                    avg_scores, avg_query_time = generic_score_by_es_search(config.search_func,
                                                           algo=config.algo,
                                                           used_ytb_ids=ytbs_used,
                                                           num_bests=config.num_bests,
                                                           duration=config.duration,
                                                           letters_to_use=config.letters_to_use,
                                                           range_=range_words,
                                                           all_fingerprints=all_fingerprint)

                    all_avg_scores.append(avg_scores)
                    avg_time_query += avg_query_time

                # update average scores
                scores_array = np.array(all_avg_scores)
                final_avg = scores_array.mean(axis=0).tolist()
                avg_time_query /= config.rounds

                # Average
                print("algo={},#sources={},dur={},search_func={},num_bests={},ranges={},time_insert={},time_query={},scores={}".format(
                    config.algo,
                    num_sources,
                    config.duration,
                    config.search_func,
                    config.num_bests,
                    str(list(range_words)[0]) + "_" + str(list(range_words)[-1]),
                    avg_time_insertion,
                    avg_query_time,
                    " ".join(["{:.2f}".format(r) for r in final_avg])
                ))

    # print("Best score is {:.2f}".format(best_score_exp))
