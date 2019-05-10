from AlgorithmsSensors.cam.Vision_RGB_Depth import  *
from AlgorithmsSensors.cam.VisionSVMTracker import *
from AlgorithmsSensors.cam.Vision_RGB import *
import time
import airsim

class Detect(Thread):
    sensorsThreads = []
    stop = False

    def __init__(self,semaphore,avoidThread,sensors=["visão","radar","inertial"],algorithm={"vision":'SVMTracker'}):
        Thread.__init__(self)
        self.semaphore = semaphore
        self.avoidThread = avoidThread
        self.airsimConection = airsim.MultirotorClient()
        for sensor in sensors:
            if sensor.lower() == "visão" or sensor.lower() == "vision":
                if 'SVMTracker' in algorithm.values():
                    visionThread = VisionRDSVMTracker(self.semaphore, avoidThread)
                else:
                    visionThread = VisionRGBDefault(self.semaphore,avoidThread)
                self.sensorsThreads.append(visionThread)

    def run(self):
        for sensorThread in self.sensorsThreads:
            sensorThread.start()
        while not self.stop:
            self.detecções = {}
            for sensorThread in self.sensorsThreads:
                self.detecções[sensorThread.name] = sensorThread.getStatus()
            # if self.checkDetect():
            #     self.avoidThread.detectionData = self.detecções['vision']
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

    #Terminar essa função que vai receber os dados dos sensores
    def recevieData(self,name,detectData):
        pass


