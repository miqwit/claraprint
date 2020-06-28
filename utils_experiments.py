import os
from os import listdir
from os.path import isfile, join, exists
import json
from fingerprint import fgpt, clean_chords, clean_melody
import config
import random
from utils import fingerprints_to_words


def get_full_piece_id(piece):
    """
    Returns rdb piece id and append movement id if exists.

    :param piece: A piece as stored in dataset
    :return: A string containing either the piece ID (no movement information) like "123", or the piece ID followed
      by dash, followed by the movement ID like "123-46123"
    """
    piece_id_only = piece["rdb_id_piece"]
    movement_id = str(piece.get("rdb_id_movement", ""))

    piece_id = str(piece_id_only)
    if movement_id:
        piece_id += "-" + movement_id

    return piece_id


def get_all_fingerprints(duration, algo):
    """
    Get fingerprints as stored in the dataset. Will not recompute them contrary to compute_all_fingerprints

    :param duration:
    :param algo:
    :return:
    """

    dataset = json.load(open(os.path.dirname(os.path.realpath(__file__)) + "/dataset/dataset_rdb_100.jams.json", "r"))
    fingerprints = {}  # Indexed by duration + "s" + "_" + full piece id

    for piece in dataset:
        for recording in piece["sandbox"]["recordings"]:
            ytb_id = recording["url"].split("?v=")[-1]
            key = str(duration) + "s_" + get_full_piece_id(piece["sandbox"]) + "_" + ytb_id
            fingerprints[key] = recording["claraprints"][f"{duration}s_{algo}"]

    return fingerprints

def compute_all_fingerprints(duration, letters_to_use, algo):
    """

    :param algo: chords_chordino or melody_melodia for instance, will be appended to folder name
    :param duration:
    :param letters_to_use:
    :return:
    """
    chords_path_dir = join(config.AUDIO_FOLDER_LOCATION, f"dataset/audio/{duration}s/{algo}/")

    if not exists(chords_path_dir):
        raise IOError(f"Folder with precomputed chords does not exists: {chords_path_dir}")

    files = [f for f in listdir(chords_path_dir) if isfile(join(chords_path_dir, f))]
    files.sort()

    all_fingerprints = {}

    for i, file in enumerate(files):
        file_path = join(chords_path_dir, file)
        ytb_id = file_path.split('/')[-1].split('_', 2)[2].split('.')[0]
        rdb_id = file_path.split('/')[-1].split('_')[1]

        claraprint = compute_fingerprint(duration=duration, letters_set=letters_to_use, algo=algo, rdb_id=rdb_id, ytb_id=ytb_id)

        all_fingerprints[file_path] = claraprint

    return all_fingerprints


def compute_fingerprint(duration, letters_set, algo, rdb_id, ytb_id, min_count=5):
    chords_path_file = join(config.AUDIO_FOLDER_LOCATION, f"dataset/audio/{duration}s/{algo}/{duration}s_{rdb_id}_{ytb_id}.json")

    if not exists(chords_path_file):
        raise IOError(f"Folder with precomputed chords does not exists: {chords_path_file}")

    data = json.load(open(chords_path_file, "r"))

    # Depending if algo is chords or melody, do not call the same cleaning method
    algo_type = algo.split("_")[0]
    if algo_type == "chords":
        chords_clean = clean_chords(data["annotations"][0]["data"], right_slash=False, resolve_enharmonics=True)
    elif algo_type == "melody":
        chords_clean = clean_melody(data["data"][0]["value"], min_count=min_count)

    claraprint = fgpt(chords_clean, letters_set)

    return claraprint


def get_all_fingerprints_by_rdb_id(duration, letters_set, algo, all_fingerprints=None):
    """
    Returns all fingerprint grouped by rdb id in this format:
    {
        "1001": [
            {"path": <path>, "fgpt": <fingerprint>},
            {"path": <path>, "fgpt": <fingerprint>},
            {"path": <path>, "fgpt": <fingerprint>},
            {"path": <path>, "fgpt": <fingerprint>},
            {"path": <path>, "fgpt": <fingerprint>}
        ]
    }
    :param duration:
    :param letters_set:
    :return:
    """
    if not all_fingerprints:
        all_fingerprints = get_all_fingerprints(duration, letters_set, algo=algo)

    # group fingerprints by rdb id
    fingerprints_by_rdb_id = {}
    for path, fgpt in all_fingerprints.items():
        name = path.split("/")[-1]
        rdb_id = name.split("_", 2)[1]

        entry = {"path": path, "fgpt": fgpt}
        if rdb_id in fingerprints_by_rdb_id:
            fingerprints_by_rdb_id[rdb_id].append(entry)
        else:
            fingerprints_by_rdb_id[rdb_id] = [entry]

    return fingerprints_by_rdb_id


def get_all_fingerprints_by_rdb_id_multiple(duration, algos, all_fingerprints=None):
    """
    Returns all fingerprint grouped by rdb id in this format:
    Can have multiple fingerprint given the algos.
    {
        "1001": [
            {"chords_chordino": "fqsdlfmj", "chords_crema": "qfqlskdjf", ...},
            {"chords_chordino": "fqsdlfmj", "chords_crema": "qfqlskdjf", ...},
            {"chords_chordino": "fqsdlfmj", "chords_crema": "qfqlskdjf", ...},
            {"chords_chordino": "fqsdlfmj", "chords_crema": "qfqlskdjf", ...},
            {"chords_chordino": "fqsdlfmj", "chords_crema": "qfqlskdjf", ...},
        ]
    }
    :param duration:
    :param letters_set:
    :return:
    """

    dataset = json.load(open(os.path.dirname(os.path.realpath(__file__)) + "/dataset/dataset_rdb_100.json", "r"))

    all_fgpt = {}
    for piece in dataset:
        rdb_id = piece["rdb_id_piece"]
        for recording in piece["recordings"]:
           if rdb_id not in all_fgpt:
               all_fgpt[rdb_id] = []

           entry = recording["claraprints"]
           entry.update({"url": recording["url"]})
           all_fgpt[rdb_id].append(entry)

    return all_fgpt


def fingerprint_from_n_sources(fgpts, num_sources, range_words, combination_mode):
    # pick random num sources
    samples = random.sample(range(0, len(fgpts)), num_sources)
    final_fgpt = []
    used_ytb_ids = []
    for sample in samples:
        words = fingerprints_to_words(fgpts[sample]["fgpt"], range_words)
        ytb_id = fgpts[sample]["path"].split("/")[-1].split("_", 2)[-1].split(".")[0]
        used_ytb_ids.append(ytb_id)
        final_fgpt.extend(words)

    if combination_mode == "intersection":
        final_fgpt = list(set(final_fgpt))

    return final_fgpt, used_ytb_ids


def fingerprint_from_n_sources_multiple_algos(fgpts, num_sources, range_words, combination_mode, claraprints):
    # pick random num sources
    samples = random.sample(range(0, len(fgpts)), num_sources)
    final_fgpt = []
    used_ytb_ids = []
    for sample in samples:
        words = []
        for claraprint in claraprints:
            words.extend(fingerprints_to_words(fgpts[sample][claraprint], range_words))
        ytb_id = fgpts[sample]["url"].split("?v=")[1]
        used_ytb_ids.append(ytb_id)
        final_fgpt.extend(words)

    if combination_mode == "intersection":
        final_fgpt = list(set(final_fgpt))

    return final_fgpt, used_ytb_ids


def fingerprint_from_one_random(fgpts, num_sources, range_words):
    sample = random.randint(0, len(fgpts) - 1)
    fgpt = fgpts[sample]["fgpt"]
    ytb_id = fgpts[sample]["path"].split("/")[-1].split("_", 2)[-1].split(".")[0]

    return fgpt, [ytb_id]