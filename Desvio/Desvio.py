from threading import Thread
from Controle.DetectionData import *


class Desvio(Thread):
    detectionData = None
    def __init__(self,control):
        Thread.__init__(self)
        self.control = control

    def run(self):
        while self.detectionData is None or self.detectionData.distance > 30:
            print("Muito Longe")
            pass
            # if self.detectionData is not None:
            #     print("Distancia:",self.detectionData.distance)
        print("---Desvio---")
        print("Distancia:", self.detectionData.distance)
        route = [[1, -10, -9]]
        self.control.updateRota(route)
        self.detectionData = None