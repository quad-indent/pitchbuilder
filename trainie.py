import sys
import os

import threading

from PyQt5.QtWidgets import QApplication, QWidget, QCheckBox, QLabel, QMainWindow, QGridLayout, QSlider, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from hz_to_note import hz_to_note

from soundProcessorModule import SoundProcessor
from soundPlayerModule import SoundPlayer
from configParser import ConfigParser as CParser
import time

SAMPLINGINTERVAL = 0.1
NEXTNOTECOOLDOWN = 2.
CURRENTPATH = ""

if getattr(sys, 'frozen', False):
    CURRENTPATH = sys._MEIPASS
else:
    CURRENTPATH = os.path.dirname(os.path.abspath(__file__))

print(f"Current path: {CURRENTPATH}")

class Winda(QMainWindow):
    soundProcessorRef = None
    soundPlayerRef = None
    configRef = None
    curPitch = -1
    lightsOn = [False, False]
    suppressingInput = False

    def __init__(self, soundProcessorRef:SoundProcessor, soundPlayerRef:SoundPlayer, configRef:CParser):
        super(Winda, self).__init__()
        self.w = QWidget()
        self.setCentralWidget(self.w)
        self.grid = QGridLayout(self.w)
        self.setLayout(self.grid)

        self.soundProcessorRef = soundProcessorRef
        self.soundPlayerRef = soundPlayerRef
        self.configRef = configRef

        self.encouragingCheckBox = QCheckBox()
        self.encouragingCheckBox.setChecked(self.configRef.getEncouragement())
        self.encouragingCheckBox.setText("Congratulatory remarks")

        self.randomInstrCheckBox = QCheckBox()
        self.randomInstrCheckBox.setChecked(self.configRef.getRandomInstrument())
        self.randomInstrCheckBox.setText("Randomise instrument")

        self.lightz = [os.path.join("assetz", "greenLight.png"), os.path.join("assetz", "redLight.png")]
        self.signalInLabel = QLabel()
        self.signalInLabelLabel = QLabel()
        self.signalInLabelLabel.setText("Receiving signal: ")

        self.signalPitchLabel = QLabel()
        self.signalPitchLabelLabel = QLabel()
        self.signalPitchLabelLabel.setText("Matching pitch: ")

        self.noiseGateSlider = QSlider(Qt.Orientation.Horizontal)
        self.noiseGateLabel = QLabel()
        self.noiseGateLabel.setText("Noise gate:")

        self.currentNoteLabel = QLabel()
        self.currentNoteLabel.setText("Currently hearing: ")

        self.pixMap = QPixmap(self.lightz[1]).scaled(32, 32)
        self.pitchMap = QPixmap(self.lightz[1]).scaled(32, 32)

        self.setWindowTitle("My window")
        self.inputDevices = self.soundProcessorRef.getInputDevices()
        self.outputDevices = None
        self.label = QLabel()

        self.inputComboBox = QComboBox()
        self.instrumentComboBox = QComboBox()
        self.instrumentComboBoxLabel = QLabel()
        self.instrumentComboBoxLabel.setText("Instrument:")

        self.initUI()
        self.initComboBox()
        self.initThreadzor()

        prefRecording = self.configRef.getPreferredAudioDevice()
        if prefRecording == "None" or not self.soundProcessorRef.isInputDeviceValid(prefRecording):
            prefRecording = self.inputDevices[0].get('name')
            self.configRef.setPreferredAudioDevice(prefRecording)

        self.inputComboBox.setCurrentText(prefRecording)
        self.soundProcessorRef.setRecordingDevice(prefRecording)

    def initUI(self):
        self.signalInLabel.setPixmap(self.pixMap)
        self.signalInLabel.resize(8, 8)

        self.signalPitchLabel.setPixmap(self.pitchMap)
        self.signalPitchLabel.resize(8, 8)

        self.noiseGateSlider.setRange(0, 12000)
        self.noiseGateSlider.setValue(self.configRef.getDetectionThreshold())
        self.noiseGateSlider.setTickInterval(600)
        self.noiseGateSlider.setTickPosition(QSlider.TicksBothSides)
        self.noiseGateSlider.valueChanged.connect(self.delegateUpdateThreshold)

        self.encouragingCheckBox.stateChanged.connect(self.onEncouragementChanged)
        self.randomInstrCheckBox.stateChanged.connect(self.onRandomiseChanged)

        self.grid.addWidget(self.encouragingCheckBox, 0, 0, 1, 1, Qt.AlignLeft | Qt.AlignBottom)
        self.grid.addWidget(self.randomInstrCheckBox, 5, 5, 1, 1, Qt.AlignLeft | Qt.AlignBottom)

        self.grid.addWidget(self.signalInLabel, 2, 4, 1, 1, Qt.AlignCenter)
        self.grid.addWidget(self.signalInLabelLabel, 1, 4, 1, 1, Qt.AlignLeft | Qt.AlignBottom)

        self.grid.addWidget(self.signalPitchLabel, 2, 5, 1, 1, Qt.AlignCenter)
        self.grid.addWidget(self.signalPitchLabelLabel, 1, 5, 1, 1, Qt.AlignLeft | Qt.AlignBottom)

        self.grid.addWidget(self.instrumentComboBoxLabel, 5, 0, 1, 1, Qt.AlignLeft | Qt.AlignBottom)

        self.grid.addWidget(self.noiseGateSlider, 2, 0, 1, 4, Qt.AlignLeft | Qt.AlignCenter)
        self.grid.addWidget(self.noiseGateLabel, 1, 0, 1, 1, Qt.AlignLeft | Qt.AlignBottom)
        self.grid.addWidget(self.currentNoteLabel, 3, 0, 1, 4, Qt.AlignLeft | Qt.AlignBottom)
        self.noiseGateSlider.setMinimumWidth(200)

    def initComboBox(self):
        inputNamez = [x.get('name') for x in self.inputDevices]
        self.inputComboBox.addItems(inputNamez)
        self.inputComboBox.activated[str].connect(self.onChanged)
        self.grid.addWidget(self.inputComboBox, 4, 0, 1, 8, Qt.AlignLeft | Qt.AlignBottom)
        self.inputComboBox.setFixedWidth(400)

        instrumentNamez = self.soundPlayerRef.instrumentz
        self.instrumentComboBox.addItems(instrumentNamez)
        self.instrumentComboBox.activated[str].connect(self.onInstrumentChanged)
        self.grid.addWidget(self.instrumentComboBox, 5, 1, 1, 8, Qt.AlignLeft | Qt.AlignBottom)

    def onChanged(self):
        current_text = self.inputComboBox.currentText()
        self.soundProcessorRef.setRecordingDevice(current_text)
        self.configRef.setPreferredAudioDevice(current_text)

    def onInstrumentChanged(self):
        current_text = self.instrumentComboBox.currentText()
        self.soundPlayerRef.setInstrument(current_text)

    def onEncouragementChanged(self):
        self.configRef.setEncouragement(self.encouragingCheckBox.isChecked())
        self.soundPlayerRef.shouldEncourage = self.encouragingCheckBox.isChecked()
    
    def onRandomiseChanged(self):
        self.configRef.setRandomInstrument(self.randomInstrCheckBox.isChecked())
        self.soundPlayerRef.setIsRandomisingInstrument(self.randomInstrCheckBox.isChecked())

    def initThreadzor(self):
        threading.Thread(target=self.soundProcessorRef.alwaysListening, daemon=True).start()
        threading.Thread(target=self.pitchWatcher, daemon=True).start()

    def toggleLight(self, whichMapName:QPixmap, whichLabelName:QLabel, lightId=0, toggleOn=True):
        if toggleOn == self.lightsOn[lightId]:
            return
        whichMap = getattr(self, whichMapName)
        whichLabel = getattr(self, whichLabelName)
        whichMap.load(self.lightz[0 if toggleOn else 1])
        whichMap = whichMap.scaled(32, 32)
        whichLabel.setPixmap(whichMap)
        self.lightsOn[lightId] = toggleOn

    def delegateUpdateThreshold(self, value):
        self.soundProcessorRef.updateThreshold(value)
        self.configRef.setDetectionThreshold(value)

    def genNewNote(self, waitPeriodInS=0.5):
        self.curPitch = -1
        time.sleep(waitPeriodInS)
        self.soundPlayerRef.killPlayBack(False)
        self.soundPlayerRef.play(self.soundPlayerRef.getRandNote())

    def suppressor(self, durationInS=1, generateNoteAfter=True):
        self.toggleLight('pitchMap', 'signalPitchLabel', 1, True)
        self.soundPlayerRef.killPlayBack(True)
        self.suppressingInput = True
        time.sleep(durationInS)
        self.toggleLight('pitchMap', 'signalPitchLabel', 1, False)
        self.suppressingInput = False
        if generateNoteAfter:
            threading.Thread(target=self.genNewNote, daemon=True).start()

    def pitchWatcher(self):
        while True:
            if self.suppressingInput:
                time.sleep(SAMPLINGINTERVAL)
                continue
            self.curPitch = self.soundProcessorRef.curPitch
            self.toggleLight('pixMap', 'signalInLabel', 0, self.curPitch != -1)
            if self.curPitch <= 0:
                try:
                    self.currentNoteLabel.setText("Currently hearing: nothing")
                    time.sleep(SAMPLINGINTERVAL)
                except RuntimeError:
                    exit(0) # Tends to crash when clicking X to exit program
                continue
            pitchie = hz_to_note(self.curPitch)
            self.currentNoteLabel.setText(f"Currently hearing: {pitchie}")
            hitRightNote = self.soundPlayerRef.validateNote(pitchie)
            if hitRightNote:
                threading.Thread(target=self.suppressor, kwargs={'durationInS': NEXTNOTECOOLDOWN, 'generateNoteAfter': True},
                                 daemon=True).start()
            time.sleep(SAMPLINGINTERVAL)

def window(soundProcRef, soundPlayerRef, configRef):
    app = QApplication(sys.argv)
    winda = Winda(soundProcRef, soundPlayerRef, configRef)
    winda.show()
    winda.genNewNote()
    app.exec()

def main():
    configRef = CParser()

    sound = SoundProcessor(recDurationInSec=SAMPLINGINTERVAL, detectionThreshold=configRef.getDetectionThreshold())
    soundPlayer = SoundPlayer(congratsTimer=NEXTNOTECOOLDOWN, shouldEncourage=configRef.getEncouragement(),
                              shouldRandomise=configRef.getRandomInstrument())

    window(sound, soundPlayer, configRef)

if __name__ == '__main__':
    main()
