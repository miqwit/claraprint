"""
This file provides function to extract chords or melody from the given file.
This is basically a wrapper to other libraries.
Return data in JAMs format, which is different for chords and melody.
"""

import librosa
import vamp
import numpy as np
from crema import analyze as crema_analyze


def extract_chords_chordino(audio_path):
    audio_1, sr_1 = librosa.load(audio_path, sr=44100, mono=True)
    duration = librosa.get_duration(audio_1, sr_1)
    chords = vamp.collect(audio_1, sr_1, "nnls-chroma:chordino")

    # Timestamp is of type RealTime. Convert to float first
    chords_casted = {
        'list': [{'timestamp': float(c['timestamp']), 'label': c['label']} for c in chords['list']]
    }

    # use jams format
    jams_format = {
        "annotations": [
            {
                "annotation_metadata": {
                    "annotator": {},
                    "annotation_tools": "nnls-chroma:chordino",
                    "version": "",
                    "annotation_rules": "",
                    "data_source": "program",
                    "corpus": "",
                    "validation": "",
                    "curator": {
                        "name": "",
                        "email": ""
                    }
                },
                "file_metadata": {
                    "release": "",
                    "artist": "",
                    "jams_version": "0.3.4",
                    "title": "",
                    "duration": duration,
                    "identifiers": {}
                },
                "sandbox": {},
                "data": [{"time": c["timestamp"],
                          "confidence": None,  # not provided by chordino
                          "duration": None,  # not provided by chordino
                          "value": c["label"]
                          } for c in chords_casted["list"]]
            }
        ]
    }

    return jams_format


def extract_chords_crema(audio_path):
    return crema_analyze.analyze(audio_path)


def extract_melody_melodia(audio_path):
    voicing = .6

    # Comments in this function are given by the creator of melodia
    # This is how we load audio using Librosa
    audio_1, sr_1 = librosa.load(audio_path, sr=44100, mono=True)

    # data_1 = vamp.collect(audio_1, sr_1, "mtg-melodia:melodia")

    # vector is a tuple of two values: the hop size used for analysis and the array of pitch values
    # Note that the hop size is *always* equal to 128/44100.0 = 2.9 ms
    # hop_1, melody_1 = data_1['vector']

    # parameter values are specified by providing a dicionary to the optional "parameters" parameter:
    params = {"minfqr": 100.0, "maxfqr": 1760.0, "voicing": voicing, "minpeaksalience": 0.0}

    data_1 = vamp.collect(audio_1, sr_1, "mtg-melodia:melodia", parameters=params)
    hop_1, melody_1 = data_1['vector']

    # <h3>\*\*\* SUPER IMPORTANT SUPER IMPORTANT \*\*\*</h3>
    # For reasons internal to the vamp architecture, THE TIMESTAMP OF THE FIRST VALUE IN THE MELODY ARRAY IS ALWAYS:
    #
    # ```
    # first_timestamp = 8 * hop = 8 * 128/44100.0 = 0.023219954648526078
    # ```
    #
    # This means that the timestamp of the pitch value at index i (starting with i=0) is given by:
    #
    # ```
    # timestamp[i] = 8 * 128/44100.0 + i * (128/44100.0)
    # ```
    #
    # So, if you want to generate a timestamp array to match the pitch values, you do it like this:

    timestamps_1 = 8 * 128 / 44100.0 + np.arange(len(melody_1)) * (128 / 44100.0)

    # Melodia has 4 parameters:
    # * **minfqr**: minimum frequency in Hertz (default 55.0)
    # * **maxfqr**: maximum frequency in Hertz (default 1760.0)
    # * **voicing**: voicing tolerance. Greater values will result in more pitch contours included in the final melody.
    # Smaller values will result in less pitch contours included in the final melody (default 0.2).
    # * **minpeaksalience**: (in Sonic Visualiser "Monophonic Noise Filter") is a hack to avoid silence turning into
    # junk contours when analyzing monophonic recordings (e.g. solo voice with no accompaniment).
    # Generally you want to leave this untouched (default 0.0).

    melody = melody_1.tolist()

    output = {
        'data': [
            {
                'value': melody,
                'time': timestamps_1.tolist()
            }
        ]
    }

    return output


def extract_melody_piptrack(audio_path):
    y, sr = librosa.load(audio_path, sr=44100, mono=True)
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)

    strongest_pitches = []
    for t in range(1, magnitudes.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        strongest_pitches.append(float(pitch))

    timestamps_1 = 8 * 128 / 44100.0 + np.arange(len(strongest_pitches)) * (128 / 44100.0)

    output = {
        'data': [
            {
                'value': strongest_pitches,
                'time': timestamps_1.tolist()
            }
        ]
    }

    return output
