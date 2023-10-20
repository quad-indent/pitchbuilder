# pitch-trainer

The aim of this project is to help the user improve their pitch recognition by having them replicate the pitch of the note they hear being played, which then is recorded and compared against the played note's pitch

# Usage

The bulk of the functionality lies within trainie.py, with the other modules handling recognition, producing the pitch, etc.

The /assetz directory contains some buttons, recordings of encouraging words, and most importantly: **the samples**. It is trivial enough to add your own samples in either a new sub-directory or by changing one of the existing sub-directories, so long as the specific schema is maintained:
- There need to be 12 sub-directories, named 0-11, where 0 corresponds to C, 1-C#, ..., 11-B
- within each of them, there can be as many samples as one wishes (ideally at least 1). I decided against caring about octaves, so have as many as you like for every note
- Each sample can be of any length one desires, but it is expected to be in .wav format with the sampling of 44.1kHz


## Contributing

Contributions are always welcome, **ESPECIALLY** if you have an instrument and would like to sample it for this project!


## Acknowledgements
 - [Zulfadhli M's fantastic music information retrieval implementation](https://github.com/ZulfadhliM/python-mir)


## Installation

1. Navigate to the latest executable at https://github.com/Jan-bog/pitch-trainer/releases
2. Unzip the files and launch trainie.exe! Make sure the assetz folder is next to the executable