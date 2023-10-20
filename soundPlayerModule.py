import os
import threading
import time

import numpy as np

from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio

class SoundPlayer:
    notez = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    instrumentz = ["bass", "sine_wavez"]

    curNote = -1
    samplesDir = ""
    curInstrument = ""
    shouldRepeat = True
    playBack = None
    comboNotesRequired = 10
    curCombo = 0
    sample = None
    congratsTimer = 0.
    shouldEncourage = True
    isRandomisingInstrument = False
    currentPath = ""

    def __init__(self, sampleDir:str=None, instrument:str="bass", comboNotesRequired:int=10,
                 congratsTimer=0., shouldEncourage=True, shouldRandomise=False,
                 currentPath:str=""):
        if sampleDir is None:
            sampleDir = os.path.join("assetz", "notez")
        self.curNote = None
        self.samplesDir = sampleDir
        self.curInstrument = instrument
        self.comboNotesRequired = comboNotesRequired
        self.sample = None
        self.congratsTimer = congratsTimer
        self.shouldEncourage = shouldEncourage
        self.isRandomisingInstrument = shouldRandomise
        self.crawlAvailableInstrumentz()
        self.currentPath = currentPath

    def crawlAvailableInstrumentz(self):
        self.instrumentz = [x for x in os.listdir(self.samplesDir) if
                            len(os.listdir(os.path.join(self.samplesDir, x))) == 12]

    def setInstrument(self, instrument:str):
        self.curInstrument = instrument
        return

    def selectSample(self, note):
        tempInstrument = self.curInstrument
        if self.isRandomisingInstrument:
            tempInstrument = self.getRandInstrument()
        numSamples = len(os.listdir(os.path.join(self.samplesDir, tempInstrument, str(note))))
        sample = np.random.randint(0, numSamples)
        return os.path.join(self.samplesDir, tempInstrument, str(note), str(note) + "_" + str(sample) + ".wav")

    def getRandNote(self, forceNote:str=None):
        if forceNote is None:
            return self.notez[np.random.randint(0, len(self.notez))]
        return forceNote
    
    def getRandInstrument(self):
        return self.instrumentz[np.random.randint(0, len(self.instrumentz))]
    
    def setIsRandomisingInstrument(self, shouldRandomise:bool):
        self.isRandomisingInstrument = shouldRandomise

    def noteToId(self, note:str):
        if '♯' in note:
            note = note.replace('♯', '#')
        if note[-1].isnumeric():
            note = note[:-1]
        return self.notez.index(note)

    def play(self, note:str, sampleRate=44100):
        if self.curNote != -1:
            return
        self.curNote = self.noteToId(note)
        threading.Thread(target=self.playLoop, args=(self.selectSample(self.noteToId(note)), sampleRate), daemon=True).start()

    def validateNote(self, hearingNote:str):
        isMatching = self.noteToId(hearingNote) == self.curNote
        if isMatching:
            self.curCombo += 1
        else:
            self.curCombo = 0
        if self.curCombo >= self.comboNotesRequired:
            self.curCombo = 0
            self.ceaseRepetitions()
        return isMatching
    
    def ceaseRepetitions(self):
        self.shouldRepeat = False
        self.curNote = -1

    def killPlayBack(self, shouldCongratulate=True):
        self.shouldRepeat = False
        if shouldCongratulate:
            threading.Thread(target=self.congratulator, daemon=True).start()
        self.curNote = -1
        if self.playBack is not None:
            print("Stopping playback")
            self.playBack.stop()
            self.playBack = None

    def playLoop(self, samplePath, sampleRate=44100, coolDownInS=0.1):
        if self.playBack is not None:
            return
        self.shouldRepeat = True
        # audioSeries, sr = librosa.load(samplePath, sr=sampleRate)
        # duration = librosa.get_duration(y=audioSeries, sr=sr) + coolDownInS
        self.sample = AudioSegment.from_wav(samplePath)
        duration = len(self.sample) // 1000 + coolDownInS
        
        durReset = 0
        while self.shouldRepeat:
            if durReset == 0:
                self.playBack = _play_with_simpleaudio(self.sample)
            durReset += coolDownInS
            if durReset >= duration:
                durReset = 0
            time.sleep(coolDownInS)
        return
    
    def congratulator(self):
        tempiePlayback = _play_with_simpleaudio(self.sample)

        if self.shouldEncourage:
            encouragementz = os.listdir(os.path.join("assetz", "encouragementz"))
            encouragingSample = encouragementz[np.random.randint(0, len(encouragementz))]
            _play_with_simpleaudio(AudioSegment.from_wav(os.path.join("assetz", "encouragementz", encouragingSample)))
        time.sleep(self.congratsTimer)
        tempiePlayback.stop()
        # anotherPlayBack.stop()
        return
