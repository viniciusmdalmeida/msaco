from threading import Thread
from Control.DetectionData import *

class StopAvoid(Thread):
    detectionData = None
    def __init__(self,control):
        Thread.__init__(self)
        self.control = control

    def run(self):
        while self.detectionData is None or self.detectionData.distance > 100:
            #print("Muito Longe")
            pass
            # if self.detectionData is not None:
            #     print("Distancia:",self.detectionData.distance)
        print("---Desvio---")
        print("Distancia:", self.detectionData.distance)
        route = [[30, 1, -10],[30, 1, -10]]
        self.control.updateRota(route)
        self.detectionData = None