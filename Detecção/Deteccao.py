from threading import Thread
from Detecção.Sensores.Vision import  *
import time
import airsim

class Deteccao(Thread):
    sensorsThreads = []
    stop = False

    def __init__(self,semaphore,desvioThread,sensors=["visão","radar","inertial"]):
        Thread.__init__(self)
        self.semaphore = semaphore
        self.desvioThread = desvioThread
        self.airsimConection = airsim.MultirotorClient()
        for sensor in sensors:
            if sensor.lower() == "visão" or sensor.lower() == "vision":
                visionThread = Visao(self.semaphore)
                self.sensorsThreads.append(visionThread)
            #if sensor.lower() == "radar":
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
                self.desvioThread.detectionData = self.detecções['vision']
            colision = self.airsimConection.simGetCollisionInfo()
            if colision.has_collided:
                print("Colidiu! com ",colision.object_name)
                ## Reset AirSim
                #self.airsimConection.reset()
            time.sleep(0.1)

    def checkDetect(self):
        selfPosition = self.airsimConection.simGetVehiclePose().position
        #Print posição
        # print("Position = x:{}, y:{}, z:{}"
        #       .format(selfPosition.x_val,selfPosition.y_val,selfPosition.z_val))
        for detectName in self.detecções:
            if self.detecções[detectName] is None:
                return False
        return True


