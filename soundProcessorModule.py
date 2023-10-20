import time

import numpy as np

import pyaudio
from pitchEstimator import pePitch


class SoundProcessor:
    pAudio = None
    audioInfo = None
    numDevices = -1
    preferredAudioDevice = None
    chunkz = 2048
    sampleFormat = pyaudio.paInt16
    channelz = 1
    recFs = 44100
    recDurationInSec = 0.2
    curPitch = -1
    detectionThreshold = 3000

    def __init__(self, chunkz=2048, sampleFormat=pyaudio.paInt16, channelz=1, recFs=44100, recDurationInSec=.2,
                 detectionThreshold=3000):
        self.pAudio = pyaudio.PyAudio()
        self.info = self.pAudio.get_host_api_info_by_index(0)
        self.numDevices = self.info.get('deviceCount')
        self.preferredAudioDevice = self.getInputDevices()[0]
        self.chunkz = chunkz
        self.sampleFormat = sampleFormat
        self.channelz = channelz
        self.recFs = recFs
        self.recDurationInSec = recDurationInSec
        self.detectionThreshold = detectionThreshold

    def isInputDeviceValid(self, deviceName):
        for i in self.getInputDevices():
            if i.get('name') == deviceName:
                return True
        return False

    def getInputDevices(self):
        devicez = []
        for i in range(0, self.numDevices):
            if (self.pAudio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                devicez.append(self.pAudio.get_device_info_by_host_api_device_index(0, i))
        return devicez

    def setRecordingDevice(self, deviceName):
        for i in self.getInputDevices():
            if i.get('name') == deviceName:
                self.preferredAudioDevice = i
                return True
        return False

    def updateThreshold(self, newThreshold):
        self.detectionThreshold = newThreshold

    def listenIn(self, saveChunks=False):
        stream = self.pAudio.open(format=self.sampleFormat,
                        channels=self.channelz,
                        rate=self.recFs,
                        input=True,
                        frames_per_buffer=self.chunkz,
                        input_device_index=self.preferredAudioDevice.get('index'))
        framez = []
        passes = int(self.recFs / self.chunkz * self.recDurationInSec)
        if passes < 1:
            passes = 1
        for _ in range(passes):
            data = stream.read(self.chunkz)
            framez.append(np.fromstring(data, dtype=np.int16))
        npData = np.hstack(framez)
        stream.stop_stream()
        stream.close()

        volume = np.log2(np.linalg.norm(npData)) ** 3

        if volume < self.detectionThreshold:
            print(f"Volume of {volume}. Too quiet, skipping")
            return -1

        if not saveChunks:
            newCunty = pePitch(npData, self.recFs)[0]
            if newCunty < 1:
                newCunty = -1
                print("Pitch not determined, skipping")
            else:
                print(f'newCunty: {newCunty}')
            print(f'Volume of {volume}. Pitchie: {newCunty}')
            return newCunty

        # wf = pydub.open("output.wav", 'wb')
        # wf.setnchannels(self.channelz)
        # wf.setsampwidth(self.pAudio.get_sample_size(self.sampleFormat))
        # wf.setframerate(self.recFs)
        # wf.writeframes(b''.join(framez))
        # wf.close()

        return -1
    
    def alwaysListening(self):
        while True:
            self.curPitch = self.listenIn()
            time.sleep(self.recDurationInSec)