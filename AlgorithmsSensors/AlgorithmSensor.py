from threading import Thread
import airsim
from abc import ABC, abstractmethod
from Control.DetectionData import DetectionData
from MyUtils.Semaphore import *

class AlgorithmSensor(Thread, ABC):
    name = "Sensor"

    def __init__(self,semaphore):
        Thread.__init__(self)
        ABC.__init__(self)
        print("Iniciando Visão",self.name)
        self.client = airsim.MultirotorClient()
        self.semaphore = semaphore
        self.detectData = None

    @abstractmethod
    def run(self):
        pass

    def sendresult(self):
        #Calculando resultado
        self.detectData = DetectionData()
        self.avoidThread.detectionData = self.detectData
            # Desvio(self.controle).start()

    def getStatus(self):
        return self.detectData


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

