from threading import Thread
from Detecção.Sensores.Vision import  *
import time

class Deteccao(Thread):
    sensorsThreads = []
    stop = False

    def __init__(self,semaphore,desvioThread,sensors=["visão","radar"]):
        Thread.__init__(self)
        self.semaphore = semaphore
        self.desvioThread = desvioThread
        for sensor in sensors:
            if sensor.lower() == "visão" or sensor.lower() == "vision":
                visionThread = Visao(self.semaphore)
                self.sensorsThreads.append(visionThread)
            # elif sensor.lower() == "radar":
            #     radarThread = Radar()
            #     self.sensorsThreads.append(radarThread)


    def run(self):
        for sensorThread in self.sensorsThreads:
            sensorThread.start()
        while not self.stop:
            self.detecções = {}
            for sensorThread in self.sensorsThreads:
                self.detecções[sensorThread.name] = sensorThread.getStatus()
            if self.checkDetect():
                self.desvioThread.detectionData = self.detecções['Vision']
            ##Reconhecendo Detect
            time.sleep(0.1)

    def checkDetect(self):
        for detectName in self.detecções:
            if self.detecções[detectName] is None:
                return False
        return True


