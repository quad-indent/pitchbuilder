import json
import os

class ConfigParser:
    jsonRef = None
    currentPath = ""

    def __init__(self, currentPath: str = ""):
        self.currentPath = currentPath
        if not os.path.exists("config.json"):
            self.jsonRef = {
                "preferredAudioDevice": "None",
                "detectionThreshold": 3000,
                "comboNotesRequired": 10,
                "wantsEncouragement": True,
                "randomInstrument": False
            }
            json.dump(self.jsonRef, open(
                "config.json", "w+", encoding='utf-8'))
        self.jsonRef = json.load(open("config.json", "r", encoding='utf-8'))

    def getPreferredAudioDevice(self):
        return self.jsonRef["preferredAudioDevice"]

    def getDetectionThreshold(self):
        return self.jsonRef["detectionThreshold"]

    def getComboNotesRequired(self):
        return self.jsonRef["comboNotesRequired"]

    def getEncouragement(self):
        return self.jsonRef["wantsEncouragement"]

    def getRandomInstrument(self):
        return self.jsonRef["randomInstrument"]

    def setPreferredAudioDevice(self, deviceName: str):
        self.jsonRef["preferredAudioDevice"] = deviceName
        json.dump(self.jsonRef, open("config.json", "w+", encoding='utf-8'))

    def setDetectionThreshold(self, threshold: int):
        self.jsonRef["detectionThreshold"] = threshold
        json.dump(self.jsonRef, open("config.json", "w+", encoding='utf-8'))

    def setComboNotesRequired(self, comboNotesRequired: int):
        self.jsonRef["comboNotesRequired"] = comboNotesRequired
        json.dump(self.jsonRef, open("config.json", "w+", encoding='utf-8'))

    def setEncouragement(self, wantsEncouragement: bool):
        self.jsonRef["wantsEncouragement"] = wantsEncouragement
        json.dump(self.jsonRef, open("config.json", "w+", encoding='utf-8'))

    def setRandomInstrument(self, randomInstrument: bool):
        self.jsonRef["randomInstrument"] = randomInstrument
        json.dump(self.jsonRef, open("config.json", "w+", encoding='utf-8'))
