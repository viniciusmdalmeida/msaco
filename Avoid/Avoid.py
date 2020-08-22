from threading import Thread
from Control.DetectionData import *


class Avoid(Thread):
    detectionData = None
    def __init__(self,control):
        Thread.__init__(self)
        self.control = control

    def run(self):
        print("Avoid Start!")
        cont = 0
        while self.detectionData is None or \
                self.detectionData.distance is None or \
                self.detectionData.distance > 500:
            cont += 1
            if cont % 100 ==0  and self.detectionData is not None:
                 print("Distancia:",self.detectionData.distance)
            # print("Desvio::Muito Longe")
            pass
        print("---Desvio---")
        print("Distancia:", self.detectionData.distance)
        route = [[60, -20, -9],[100, -40, -9],[30, -60, -9]]
        self.control.updatePath(route)
        self.detectionData = None