# Claraprint

Claraprint is a cover song (or musical work) fingerprint based on rough chord and melody extraction. It has been thought to be used
for classical music where these non-accurate features are proved to be enough in certain circumstances to capture the 
musical work unicity.

This code is used in the research paper CLARAPRINT: A CHORD AND MELODY BASED FINGERPRINT FOR WESTERN CLASSICAL MUSIC COVER DETECTION.
All experiments and figures are reproducible by following the present instructions and using this code.

This code is under [MIT Licence](LICENCE.txt).

## Usage

After referencing this code in your project, run the following commands.

### Build a claraprint

```python
from claraprint import claraprint

algo = "chords_chordino"
# can also be "chords_crema", "melody_piptrack", "melody_melodia"

audio_file_path = "/data/audio/myfile.mp3"
cp = claraprint(audio_file_path, algo)

# cp is a string
print(cp)
```

## Installation

## Reproducibility

This section explains how to rerun the experiments in the scientific paper CLARAPRINT: A CHORD AND MELODY BASED FINGERPRINT FOR WESTERN CLASSICAL MUSIC COVER DETECTION.

### Run an experiment

### Generate figures in the paper