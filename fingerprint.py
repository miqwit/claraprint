import math
import re
import os

# The scale of all possible pitches returned from chords or melody.
# Pitches are simplified to sharps (#) only, and no flats (b)
scale = ["A", "A#", "B", "B#", "C", "C#", "D", "D#", "E", "E#", "F", "F#", "G", "G#"]

# This is one letter set, arbitrarily used for chords
letters = {
    'D1': 'a',
    'D2': 'b',
    'D3': 'c',
    'D4': 'd',
    'D5': 'e',
    'D6': 'f',
    'D7': 'g',
    'U1': 'h',
    'U2': 'i',
    'U3': 'j',
    'U4': 'k',
    'U5': 'l',
    'U6': 'm',
    'U7': 'n'
}

# In this set of letters, each interval is a set of three letters
# Two of them are in common with the closest intervals, so will result
# in more similarities. Sometimes the chord detection is confused by closed chords_chordino
letters_set_2 = {
    'D1': 'abc',
    'D2': 'bcd',
    'D3': 'cde',
    'D4': 'def',
    'D5': 'efg',
    'D6': 'fgh',
    'D7': 'ghi',
    'U1': 'yza',
    'U2': 'xyz',
    'U3': 'wxy',
    'U4': 'vwx',
    'U5': 'uvw',
    'U6': 'buv',
    'U7': 'abu'
}


# This is another letters set, arbitrarily used for melody.
letters_set_3 = {
    'D1': 'o',
    'D2': 'p',
    'D3': 'q',
    'D4': 'r',
    'D5': 's',
    'D6': 't',
    'D7': 'y',
    'U1': 'b',
    'U2': 'w',
    'U3': 'x',
    'U4': 'y',
    'U5': 'z',
    'U6': '$',
    'U7': '%'
}


def get_letters_set_from_algo(algo):
    """
    Returns 1 if it's a chord algo, 3 if it's a melody algo. This is an arbitraty choice.

    :param algo:
    :return:
    """
    prefix = algo.split("_")[0]
    if prefix == "chords":
        return 1
    elif prefix == "melody":
        return 3
    else:
        raise IOError("Unexpected algo type")


def clean_chords(data, right_slash=False, resolve_enharmonics=True, time_threshold=100):
    """
    From chords_chordino computed by chordino, clean them. Will only use
    letters and # and b by default. Adim becomes A, Ebmaj7 becomes Eb, ...
    G7/B becomes G, unless right_slash is True.

    :param data: (dict) JAMS, a list of chords such as:
         [
        {
          "time": 0.185759637,
          "confidence": null,
          "duration": null,
          "value": "N"
        },... ]
    :param right_slash: (bool) For a chord like 'G7/B', use B.
    :param resolve_enharmonics: (bool) For instance Db becomes C#. Use only #.
    :param time_threshold: (int) Ignore chord if it last less than this value (in ms)

    :returns: An array or clean chords, like ["G#", "A#", "B"]. Same repeated chords are reduced to one occurence.
    """

    enharm_from = ["Ab", "Bb", "Cb", "Db", "Eb", "Fb", "Gb"]
    enharm_to = ["G#", "A#", "B", "C#", "D#", "E", "F#"]

    chord_simples = []  # cleaner chord succession

    # Remove duplicated
    chord_num = -1
    for chord_raw in data:
        chord = chord_raw["value"]
        chord_num += 1

        # Skip unknown chord (like N for chordino or X for crema)
        if chord in ["N", "X"]:
            continue

        # Skip chord that does not last long enough
        if chord_num + 1 <= len(data) - 1:
            cur_ts = chord_raw['time']
            next_ts = data[chord_num + 1]['time']
            if ((next_ts * 1000) - (cur_ts * 1000)) < time_threshold:
                continue

        # Use right of slash
        if "/" in chord and right_slash:
            chord = chord.split("/")[-1]

        # Take first char of chord for now
        chord_simple = chord[0]

        # Take first char + second char if # or b
        # Ignore following chars that contain more accurate information like
        # 'm', 'm6', 'maj', 'dim', ...
        if len(chord) > 1 and chord[1] in ["b", "#"]:
            chord_simple += chord[1]

        # Resolve enharmonics
        if resolve_enharmonics:
            if chord_simple in enharm_from:
                chord_simple = enharm_to[enharm_from.index(chord_simple)]

        # First element of chord_simples
        if len(chord_simples) > 0:
            previous_chord = chord_simples[-1]
        else:
            chord_simples.append(chord_simple)
            continue

        # Skip similar chord to previous one
        if chord_simple == previous_chord:
            continue

        chord_simples.append(chord_simple)

    return chord_simples


def chords_to_prog(chord_simples, letters_to_use):
    # Convert progressions in up or down
    chord_prog = []
    # Compute fgpt
    previous_chord = ""
    switch_dir = math.floor((len(scale) / 2) + 1)
    for chord_simple in chord_simples:
        # Get position of chord in scale
        idx = scale.index(chord_simple)
        idx_previous = scale.index(previous_chord) if previous_chord != "" else ""

        # Check if we go up or down
        if idx_previous:
            # Direction is up or down. Cannot be equal as we eliminated this option before
            # If the distance is more than the half + 1, goes the other direction (modulo)
            if idx == idx_previous:
                raise Exception("Should not happen")

            diff = abs(idx - idx_previous)

            if idx > idx_previous:
                prog = "U" + str(diff)
            else:
                prog = "D" + str(diff)

            # Reverse
            if (diff >= switch_dir):
                new_value = str(len(scale) - diff)
                prog = "U" + new_value if prog[0] == "D" else "D" + new_value

            letter = letters_to_use[prog]
            chord_prog.append(letter)

        # Update previous chord
        previous_chord = chord_simple

    # print("-".join(map(lambda x:x.ljust(2), chord_simples)))
    claraprint_ = "".join(chord_prog)
    return claraprint_


def fgpt(chords_clean, letters_set=1):
    if letters_set == 1:
        letters_to_use = letters
    elif letters_set == 2:
        letters_to_use = letters_set_2
    elif letters_set == 3:
        letters_to_use = letters_set_3

    claraprint_ = chords_to_prog(chords_clean, letters_to_use)
    return claraprint_


# Table taken from https://pages.mtu.edu/~suits/notefreqs.html
# Note	Frequency (Hz)
# As we don't discriminate # from b here, only tag notes as # (D# and not Eb)
scale_freq = {
    "C0": 16.35,
    "C#0": 17.32,
    "D0": 18.35,
    "D#0": 19.45,
    "E0": 20.60,
    "F0": 21.83,
    "F#0": 23.12,
    "G0": 24.50,
    "G#0": 25.96,
    "A0": 27.50,
    "A#0": 29.14,
    "B0": 30.87,
    "C1": 32.70,
    "C#1": 34.65,
    "D1": 36.71,
    "D#1": 38.89,
    "E1": 41.20,
    "F1": 43.65,
    "F#1": 46.25,
    "G1": 49.00,
    "G#1": 51.91,
    "A1": 55.00,
    "A#1": 58.27,
    "B1": 61.74,
    "C2": 65.41,
    "C#2": 69.30,
    "D2": 73.42,
    "D#2": 77.78,
    "E2": 82.41,
    "F2": 87.31,
    "F#2": 92.50,
    "G2": 98.00,
    "G#2": 103.83,
    "A2": 110.00,
    "A#2": 116.54,
    "B2": 123.47,
    "C3": 130.81,
    "C#3": 138.59,
    "D3": 146.83,
    "D#3": 155.56,
    "E3": 164.81,
    "F3": 174.61,
    "F#3": 185.00,
    "G3": 196.00,
    "G#3": 207.65,
    "A3": 220.00,
    "A#3": 233.08,
    "B3": 246.94,
    "C4": 261.63,
    "C#4": 277.18,
    "D4": 293.66,
    "D#4": 311.13,
    "E4": 329.63,
    "F4": 349.23,
    "F#4": 369.99,
    "G4": 392.00,
    "G#4": 415.30,
    "A4": 440.00,
    "A#4": 466.16,
    "B4": 493.88,
    "C5": 523.25,
    "C#5": 554.37,
    "D5": 587.33,
    "D#5": 622.25,
    "E5": 659.25,
    "F5": 698.46,
    "F#5": 739.99,
    "G5": 783.99,
    "G#5": 830.61,
    "A5": 880.00,
    "A#5": 932.33,
    "B5": 987.77,
    "C6": 1046.50,
    "C#6": 1108.73,
    "D6": 1174.66,
    "D#6": 1244.51,
    "E6": 1318.51,
    "F6": 1396.91,
    "F#6": 1479.98,
    "G6": 1567.98,
    "G#6": 1661.22,
    "A6": 1760.00,
    "A#6": 1864.66,
    "B6": 1975.53,
    "C7": 2093.00,
    "C#7": 2217.46,
    "D7": 2349.32,
    "D#7": 2489.02,
    "E7": 2637.02,
    "F7": 2793.83,
    "F#7": 2959.96,
    "G7": 3135.96,
    "G#7": 3322.44,
    "A7": 3520.00,
    "A#7": 3729.31,
    "B7": 3951.07,
    "C8": 4186.01,
    "C#8": 4434.92,
    "D8": 4698.63,
    "D#8": 4978.03,
    "E8": 5274.04,
    "F8": 5587.65,
    "F#8": 5919.91,
    "G8": 6271.93,
    "G#8": 6644.88,
    "A8": 7040.00,
    "A#8": 7458.62,
    "B8": 7902.13
}


def get_note_from_freq(f):
    """
    From the given frequency f, return the closest note in the scale_freq (defined in this file) array. The closest
    note can be a bit higher, or a bit lower.

    :param f: Frequency (float)
    :return: A note information, with octave such as 'C3'
    """
    prev_freq = None
    prev_note = None

    for note, freq in scale_freq.items():
        # lower than lowest
        if prev_freq is None and f < freq:
            return note

        # Go higher
        if f > freq:
            prev_freq = freq
            prev_note = note
            continue

        # exact same freq
        if f == freq:
            return note

        # check if closest than previous or not
        if f < freq:
            if abs(freq - f) < abs(prev_freq - f):
                # closest to this one
                return note

            # closest to previous one
            return prev_note

    # Higer than higest
    return freq


def note_to_pitch_class(note):
    """
    Remove octave information. Input D#3 will return D#

    :param note: Original note, such as 'D#3'
    :return: Note without the octave, such as 'D#'
    """
    return re.sub("\d", "", note)


def clean_melody(freqs, min_count):
    """
    Get pitch from each frequence given by melodia. For each frequence, the note will be returned by the function
    get_note_from_freq, and the pitch (no octave information) by note_to_pitch_class.
    Do not repeat twice the same note. If the found melody is ['C', 'C', 'B', 'B'], then ['C', 'B'] will be returned.

    :param freqs: The array of frequences to be used
    :param min_count: Do not store pitch if it's not repeated that much time. Some pitched might be artefacts, or
      to fast in the audio to be considered as an interesting melody in our case. Depends on algorithm, for piptrack,
      the value 5 was found optimal, but for melodia, the value 10 was found optimal. Empirical values.
    :return: An array of clean pitches such as ['C', 'D', 'E', 'C']
    """

    # remove negative values
    freqs_positive = list(filter(lambda x: x > 0, freqs))

    # Keep only values present more than 10 times (included)
    counter = 0
    last_val = None
    notes = []

    for f in freqs_positive:
        # Add it only if was not the last one already
        note = note_to_pitch_class(get_note_from_freq(f))

        if last_val is None or last_val == note:
            counter += 1
        elif last_val != note:
            counter = 1

        if counter >= min_count:
            if len(notes) == 0 or notes[-1] != note:
                notes.append(note)

        last_val = note

    return notes


def claraprint(audio_path, algo):
    """
    Compute the claraprint for the given audio path.
    This function is not very generic, and will do slightly different processes from one algo to the other.
    The functions used to compute chords or melody are in extract_information.py

    :param audio_path: The full audio path. Will raise an error if not found
    :param algo: The algo to be used to compute the claraprint. A value like "chords_chordino", "chords_crema",
      "melody_piptrack", "melody_melodia", ...
    :return: A string representing a fingerprint based on the given algo, like "yzyszszryoszszsxqxqs..."
    """
    if not os.path.exists(audio_path):
        raise OSError(f"Audio file {audio_path} not found")

    # Compute chord or melody based on algo
    if algo == "chords_chordino":
        from extract_information import extract_chords_chordino
        pitches = extract_chords_chordino(audio_path)
    elif algo == "chords_crema":
        from extract_information import extract_chords_crema
        pitches = extract_chords_crema(audio_path)
    elif algo == "melody_melodia":
        from extract_information import extract_melody_melodia
        pitches = extract_melody_melodia(audio_path)
        min_count = 10
    elif algo == "melody_piptrack":
        from extract_information import extract_melody_piptrack
        pitches = extract_melody_piptrack(audio_path)
        min_count = 5
    else:
        raise IOError(f"Algo {algo} not supported")

    # Depending if algo is chords or melody, do not call the same cleaning method
    algo_type = algo.split("_")[0]
    if algo_type == "chords":
        letters_ = 1
        # in JAMS chords are in ["annotations"][0]["data"]
        chords_clean = clean_chords(pitches["annotations"][0]["data"], right_slash=False, resolve_enharmonics=True)
    elif algo_type == "melody":
        letters_ = 3
        # in JAMS melody pitches are in ["data"][0]["value"]
        chords_clean = clean_melody(pitches["data"][0]["value"], min_count=min_count)

    claraprint_ = fgpt(chords_clean, letters_)

    return claraprint_
