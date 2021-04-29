from threading import Thread
import airsim
from abc import ABC, abstractmethod
from Detect.DetectionData import DetectionData
import time
import yaml

class AlgorithmSensor(Thread, ABC):
    name = "Sensor"

    def __init__(self,detectRoot,config_path='config.yml'):
        Thread.__init__(self)
        ABC.__init__(self)
        with open(config_path, 'r') as file_config:
            self.config = yaml.full_load(file_config)
        self.client = airsim.MultirotorClient()
        self.detectRoot = detectRoot
        self.detectData = DetectionData(algoritmo=self.__class__.__name__)
        self.interval = 0.5
        self._stop_detect = False

    def run(self):
        print("Start Algorithm Thread",self.name)
        self.start_tracker()
        while True:
            if self._stop_detect:
                break
            self.detect()
            time.sleep(self.interval)

    def start_tracker(self):
        pass

    @abstractmethod
    def detect(self):
        pass

    def getDetectData(self):
        return self.detectData

    def sendresult(self,name=None):
        #Calculando resultado
        if self.detectData is None:
            self.detectData = DetectionData(algoritmo=self.__class__.__name__)
        if name == None:
            name = self.name
        self.detectRoot.receiveData(self.detectData,name)
            # Desvio(self.controle).start()

    def terminate(self):
        self._stop_detect = True


class SensorProtocol:
    #Esta classe cria o procolo de retorno generico de um sensor
    detect = False
    myPosition = (0, 0, 0)
    relativePosition = (0, 0, 0)
    otherPosition = (0, 0, 0)

    def __init__(self, detect=None, myPosition=None, relativePosition=None, otherPosition=None):
        self.detect = detect
        self.myPosition = myPosition
        self.relativePosition = relativePosition
        if otherPosition is None:
            self.otherPosition = self.calcOtherPosition()
        else:
            self.otherPosition = otherPosition

    def calcOtherPosition(self):
        pass

