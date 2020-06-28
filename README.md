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

To install claraprint

1. Create a python3 virtual environment `virtualenv ~/.env/claraprint -p /usr/bin/python3` and activate it `source ~/.env/claraprint/bin/activate`
2. Clone this repository `git clone https://github.com/miqwit/claraprint`
3. Install the dependency with `pip install -r requirements.txt`

> **Warning**: During the installation of requirements, you may see the following error: `ERROR: crema 0.1.0 has requirement librosa==0.5, but you'll have librosa 0.7.2 which is incompatible.` This version of `crema` references `librosa==0.5` but actually works unders `librosa==0.7.2`. Id does not work under `librosa==0.5`. See [raised issue on GitHub](https://github.com/bmcfee/crema/issues/31). 

## Reproducibility

This section explains how to rerun the experiments in the scientific paper CLARAPRINT: A CHORD AND MELODY BASED FINGERPRINT FOR WESTERN CLASSICAL MUSIC COVER DETECTION.

### Used versions

* Python 3.6.9
* Elasticsearch 7.6.2
* Dependencies: see [requirements.txt](requirements.txt)

### Installation for reproducibility

Additionally to the previous installation section, you must run an Elasticsearch instance that will be used to store 
and expose the fingerprints for research. We used Docker to run an Elasticsearch (version 7.6.2) sever locally.

```
docker run \
-e "indices.query.bool.max_clause_count=10000" \
-e "http.max_initial_line_length=1mb" \
-e "http.max_header_size=1mb" \
-e "discovery.type=single-node" \
-e "http.cors.enabled=true" \
-e "http.cors.allow-origin=moz-extension://45f04639-6ef3-476e-b943-9a9e856b309e" \
-d \
--name claraes_7.6.2 \
-p 9200:9200 \
docker.elastic.co/elasticsearch/elasticsearch:7.6.2
```

### Run an experiment

The main experiment file script is [es_multiple_fp_generated](experiments/es_multiple_fp_generated/es_multiple_fp_generated.py).
 It allows to run different experiments, and not only multiple fingerprint ones, as the name of the file suggests.
 
#### Preparation

Before running an experiment, open the file, and edit the `configs_to_run` variable. Here is an example of its value:

```python
configs_to_run = [
    Config(algo="chords_chordino", duration=120, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1]),
    Config(algo="chords_crema", duration=120, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1]),
    Config(algo="melody_melodia", duration=120, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1]),
    Config(algo="melody_piptrack", duration=120, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1])
]
``` 

This example will run 4 configurations, for 4 different algorithms (property `algo`). The details of the parameters
can be found in the source file, and is repeated here:

- **algo**: which algo to run. Can be chords_chordino, chords_crema, melody_melodia, melody_piptrack
- **duration**: which samples to use. In these experiment, only 30s and 120s are precomputed. Use int 30 or 120.
- **letters_to_use**: set of letters to use for a claraprint. Is defined in fingerprints.py. Traditionally, 1 is for 
  chords and 3 is for melody. 2 is unused. It is useful to use different sets for combinatory fingerprints 
  (chords + melody)
- **range_words**: for the given configuration, the different sizes of words to use. Contains a list of range objects.
- **num_sources**: how many audio files to use to generate one claraprint
- **num_bests**: will display in the results how many times a fingerprint was found in the N top values of a search result.
  Contains a list. For example [10, 5, 1] will display the presence of a given claraprint in the top 10, top 5 and top 1
  (= is it the first result) of a search.
- **fingerprint_from_one_source**: reference to a function to mix fingerprints from different sources. Such function, like
  fingerprint_from_n_sources, can be found in the utils_experiments.py file. You can write your own.
- **search_func**: reference to a function to run a search query against the elasticsearch. Such functions are to be found
  in the file experiments.es_helper.py.
- **ingest_func**: reference to a function to ingest a document (claraprint) inside the Elasticsearch index. Such functions
  are to be found in the file experiments.es_helper.py.
- **createindex_func**: reference to a function to create the Elasticsearch index.
- **rounds**: number of times the configuration is run. Because the works are taken randomly in the dataset, it's worth
  running the config several times to consolidate the result.
- **combination_mode**: when several fingerprints are used (num_sources > 1), how do we combine the fingerprint, can be
  'union' or 'intersection'. This is implemented in the fingerprint_from_n_sources function.

#### Run experiment

Run the experiment with the command:

```shell script

```

### Generate figures in the paper