from threading import Thread
import airsim
from abc import ABC, abstractmethod
from MyUtils.Semaphore import *

class Sensor(Thread,ABC):
    name = "Sensor"

    def __init__(self,semaphore):
        Thread.__init__(self)
        ABC.__init__(self)
        print("Iniciando Visão",self.name)
        self.client = airsim.MultirotorClient()
        self.semaphore = semaphore
        self.detectData = None

    def getStatus(self):
        return self.detectData

    @abstractmethod
    def run(self):
        pass

    def sendData(self):
        pass
        # detect.recevieData(self.name,self.detectData)
        # Desvio(self.controle).start()

