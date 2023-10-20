import os
import numpy as np
from scipy.io import wavfile

# Define the frequencies for each note (C2 to B2)
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
base_octave = 0
sample_rate = 44100  # Adjust as needed

# Create a directory to store the generated .wav files
output_dir = "sine_waves"
os.makedirs(output_dir, exist_ok=True)

# Generate and save sine waves for each note and octave
for octave in range(base_octave, 4):  # Generate for octaves 2, 3, and 4
    for note_index, note_name in enumerate(note_names):
        frequency = 55.0 * (2 ** (octave - base_octave)) * (2 ** (note_index / 12))
        file_name = f"{note_index}_{octave - base_octave}.wav"
        folder_name = str(note_index)

        # Create separate folders for each note (not octave)
        note_folder = os.path.join(output_dir, folder_name)
        os.makedirs(note_folder, exist_ok=True)

        # Generate a sine wave
        t = np.linspace(0, 3, sample_rate * 3, endpoint=False)
        sine_wave = np.sin(2 * np.pi * frequency * t) * 0.4

        # Scale the sine wave to fit in a 16-bit .wav file
        scaled_wave = np.int16(sine_wave * 32767)

        # Save the wave to a .wav file
        wavfile.write(os.path.join(note_folder, file_name), sample_rate, scaled_wave)

print("Sine waves generated and saved.")