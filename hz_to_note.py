import math

# Ripped from https://stackoverflow.com/a/70963520 on account of laziness. THanks, @lisrael1!

def hz_to_note(freq):
    notez = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    note_number = 12 * math.log2(freq / 440) + 49  
    note_number = round(note_number)
    note = (note_number - 1 ) % len(notez)
    note = notez[note]
    octave = (note_number + 8 ) // len(notez) + 1
    return note + str(octave)