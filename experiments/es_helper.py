"""
This file contains ES (elasticseach) functions that can be reused in multiple ES based experiments.
Each experiment can override one of these methods for its particular need
"""

from elasticsearch import Elasticsearch
from utils_experiments import get_all_fingerprints
from utils import fingerprints_to_words
from config import es_host, es_port, es_index
import time

es = Elasticsearch([{'host': es_host, 'port': es_port}])


# ES tools for this experiment
def create_index(lower, higher):
    clara_index_mapping = {
        "mappings": {
            "properties": {
                "claraprint": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "rdb_id": {
                    "type": "text",
                    "index": True
                },
                # youtube ids used for this fingerprint. Will be a list of strings in practice
                "ytb_ids": {
                    "type": "text"
                }
            }
        },
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
    }

    es.indices.delete(index=es_index, ignore=404)
    es.indices.create(index=es_index, body=clara_index_mapping)


def store_one_fingerprint(rdb_id, ytb_ids, fingerprint):
    body = {
        "claraprint": " ".join(fingerprint),
        "rdb_id": rdb_id,
        "ytb_ids": ytb_ids
    }

    es.index(index=es_index, body=body)


def es_refresh():
    es.indices.refresh(index=es_index)


def es_search(fingerprint, range_):
    """
    Convert fingerprint to words (shingles) given the range, and query it as a sentence to ES.

    :param fingerprint: The fingerprint that will be shingled.
    :param range_: The min and max word length to use.
    :return: ES results
    """
    words = " ".join(fingerprints_to_words(fingerprint, range_))
    return es.search(index=es_index, q=words)


def generic_score_by_es_search(search_function, algo, used_ytb_ids, num_bests=[10], duration=120, letters_to_use=1,
                               range_=range(2, 7), all_fingerprints=None):
    """
    :param search_function: The function to use for search, as defined in utils_es
    :param num_bests: Check if the expected fingerprint is in this top N results. If two values given, like [10, 5],
      the output of this function will contain two scores, one for the number of times the document was found in the
      10 first results, and one in the 5 first results.
    :param duration: Get precomputed fingerprints for this duration (will look in folder 120s or 30s for instance,
      if duration 120 and 30 is given)
    :param letters_to_use: Set of letters to use from fingerprint
    :param range_: Words to consider during shingling (before ES search)
    :return:
    """
    parameters = locals()
    if not all_fingerprints:
        all_fingerprints = get_all_fingerprints(duration, letters_to_use, algo)

    avgs = [.0]*len(num_bests)
    scores = []
    for n in num_bests:
        scores.append([])

    avg_query_time = 0
    for path, fingerprint in all_fingerprints.items():
        ytb_id = path.split('/')[-1].split('_', 2)[2].split('.')[0]

        # If this fingerprint has been used for the reference fgpt, ignore it
        if ytb_id in used_ytb_ids:
            continue

        t1 = time.time()
        res = search_function(fingerprint, range_)
        avg_query_time += (time.time() - t1)

        rdb_id = path.split('/')[-1].split('_')[1]

        rdb_ids_in_results = [r['_source']['rdb_id'] for r in res['hits']['hits']]

        for idx_best, num_best in enumerate(num_bests):
            found = int(rdb_id in rdb_ids_in_results[:num_best])
            scores[idx_best].append(found)

    avg_query_time /= len(all_fingerprints.items())

    for idx_best, num_best in enumerate(num_bests):
        avgs[idx_best] = sum(scores[idx_best]) / len(scores[idx_best])

    return avgs, avg_query_time


def generic_score_by_es_search_multiple_algo(search_function, used_ytb_ids, combination_mode, claraprints,
                                             num_bests=[10],
                                             range_=range(2, 7), all_fingerprints=None):
    if not all_fingerprints:
        raise IOError("Not supported. Provide all_fingerprints.")

    avgs = [.0]*len(num_bests)
    scores = []
    for n in num_bests:
        scores.append([])

    for rdb_id, gpfgpts in all_fingerprints.items():
        # From this group, remove the recordings that were used for ingestiong
        clean_gpfgpts = []
        for fgpts in gpfgpts:
            ytb_id = fgpts["url"].split('?v=')[-1]

            # If this fingerprint has been used for the reference fgpt, ignore it
            if ytb_id in used_ytb_ids:
                continue

            clean_gpfgpts.append(fgpts)

        # Build combinatory fingerprint from this recording
        from utils_experiments import fingerprint_from_n_sources_multiple_algos
        fingerprint, _ytbid = fingerprint_from_n_sources_multiple_algos(clean_gpfgpts, 1, range_, combination_mode, claraprints)

        res = search_function(fingerprint, range_)

        rdb_ids_in_results = [r['_source']['rdb_id'] for r in res['hits']['hits']]

        for idx_best, num_best in enumerate(num_bests):
            found = int(rdb_id in rdb_ids_in_results[:num_best])
            scores[idx_best].append(found)

    for idx_best, num_best in enumerate(num_bests):
        avgs[idx_best] = sum(scores[idx_best]) / len(scores[idx_best])

    return avgs


def create_index_shingle(lower, upper):
    clara_index_mapping = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "analysis": {
                "filter": {
                    "my_shingle_filter": {
                        "type": "shingle",
                        "min_shingle_size": 3,
                        "max_shingle_size": 3,
                        "output_unigrams": False
                    },
                    "my_minhash_filter": {
                        "type": "min_hash",
                        "hash_count": 1,
                        "bucket_count": 512,
                        "hash_set_size": 12,
                        "with_rotation": True
                    }
                },
                "analyzer": {
                    "my_analyzer": {
                        "tokenizer": "standard",
                        "filter": [
                            "my_shingle_filter",
                            # "my_minhash_filter"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "claraprint": {
                    "type": "text",
                    "analyzer": "my_analyzer"
                },
                "rdb_id": {
                    "type": "text",
                    "index": True
                },
                # youtube ids used for this fingerprint. Will be a list of strings in practice
                "ytb_ids": {
                    "type": "text"
                }
            }
        }
    }

    es.indices.delete(index=es_index, ignore=404)
    clara_index_mapping["settings"]["analysis"]["filter"]["my_shingle_filter"]["min_shingle_size"] = lower
    clara_index_mapping["settings"]["analysis"]["filter"]["my_shingle_filter"]["max_shingle_size"] = upper
    es.indices.create(index=es_index, body=clara_index_mapping)


def store_one_fingerprint_shingle(rdb_id, ytb_ids, fingerprint):
    body = {
        "claraprint": " ".join(fingerprint),
        "rdb_id": rdb_id,
        "ytb_ids": ytb_ids
    }

    es.index(index=es_index, body=body)


def es_search_shingle(fingerprint, range_):
    """
    Convert fingerprint to spaced fingerprint ("fiij" to "f i i j") and query it in the ES
    :param fingerprint: The fingerprint. Will be spaced
    :param range_: Unused, but here for genericity
    :return: ES results
    """
    return es.search(index=es_index, q=" ".join(fingerprint))
