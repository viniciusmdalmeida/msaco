from AlgorithmsSensors.cam.Vision_RGB_Depth import  *
from AlgorithmsSensors.cam.VisionSVMTracker import *
from AlgorithmsSensors.cam.Vision_RGB import *
import time
import airsim

class Detect(Thread):
    stop = False

    def __init__(self,semaphore,avoidThread,sensorsAlgorithm={"vision":'SVMTracker'}):
        Thread.__init__(self)
        self.semaphore = semaphore
        self.avoidThread = avoidThread
        self.airsimConection = airsim.MultirotorClient()
        self.sensorsThreads = []

        if type(sensorsAlgorithm) is list:
            for sensor in sensorsAlgorithm:
                if sensor.lower() == "visão" or sensor.lower() == "vision":
                    visionThread = VisionRDSVMTracker(self,self.semaphore)
                    self.sensorsThreads.append(visionThread)

        if type(sensorsAlgorithm) is dict:
            for sensor in sensorsAlgorithm:
                if type(sensorsAlgorithm[sensor]) is list:
                    for algorithm in sensorsAlgorithm[sensor]:
                        newAlgorithm = algorithm(self,self.semaphore)
                        self.sensorsThreads.append(newAlgorithm)
                else:
                    newAlgorithm = sensorsAlgorithm[sensor](self, self.semaphore)
                    self.sensorsThreads.append(newAlgorithm)
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
    def receiveData(self,detectData,name='vision'):
        self.sendData(detectData)

    def sendData(self,detectData):
        self.avoidThread.detectionData = detectData


