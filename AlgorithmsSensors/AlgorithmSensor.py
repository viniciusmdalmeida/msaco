from threading import Thread
import airsim
from abc import ABC, abstractmethod
from Control.DetectionData import DetectionData
from Utils.Semaphore import *
import yaml

class AlgorithmSensor(Thread, ABC):
    name = "Sensor"

    def __init__(self,detectRoot,config_path='config.yml'):
        Thread.__init__(self)
        ABC.__init__(self)
        print("Start Algorithm ",self.name)
        with open(config_path, 'r') as file_config:
            self.config = yaml.full_load(file_config)
        self.client = airsim.MultirotorClient()
        self.detectRoot = detectRoot
        self.detectData = None


    @abstractmethod
    def run(self):
        pass

    def getData(self):
        pass

    def sendresult(self,name=None):
        #Calculando resultado
        if self.detectData is None:
            self.detectData = DetectionData()
        if name == None:
            name = self.name
        self.detectRoot.receiveData(self.detectData,name)
            # Desvio(self.controle).start()

    def getStatus(self):
        return self.detectData

    def terminate(self):
        self._stop = False


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

