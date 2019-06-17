from AlgorithmsSensors.cam.Vision_RGB_Depth import  *
from AlgorithmsSensors.cam.VisionSVMTracker import *
from AlgorithmsSensors.cam.Vision_RGB import *
import time
import airsim

class Detect(Thread):
    stop = False

    def __init__(self,vehicleComunication,sensorsAlgorithm,avoidThread):
        Thread.__init__(self)
        self.avoidThread = avoidThread
        self.vehicle = vehicleComunication
        self.sensorsThreads = []
        self.sensorsAlgorithm = sensorsAlgorithm


    def startAlgorithms(self):
        print("Start sensor Algorithms")
        if type(self.sensorsAlgorithm) is list:
            for sensor in self.sensorsAlgorithm:
                if sensor.lower() == "visão" or sensor.lower() == "vision":
                    visionThread = VisionRDSVMTracker(self)
                    self.sensorsThreads.append(visionThread)

        if type(self.sensorsAlgorithm) is dict:
            for sensor in self.sensorsAlgorithm:
                if type(self.sensorsAlgorithm[sensor]) is list:
                    for algorithm in self.sensorsAlgorithm[sensor]:
                        newAlgorithm = algorithm(self)
                        print("-----------",newAlgorithm.name)
                        self.sensorsThreads.append(newAlgorithm)
                else:
                    newAlgorithm = self.sensorsAlgorithm[sensor](self)
                    self.sensorsThreads.append(newAlgorithm)
    def run(self):
        self.startAlgorithms()
        for sensorThread in self.sensorsThreads:
            sensorThread.start()
        while not self.stop:
            self.detecções = {}
            for sensorThread in self.sensorsThreads:
                self.detecções[sensorThread.name] = sensorThread.getStatus()
            # if self.checkDetect():
            #     self.avoidThread.detectionData = self.detecções['vision']
            # if self.vehicle.name == "AirSim":
            #     colision = self.vehicle.client.simGetCollisionInfo()
            #     if colision.has_collided:
            #         print("Colidiu! com ",colision.object_name)
                    ## Reset AirSim
                    #self.vehicle.reset()
            time.sleep(0.1)

    def checkDetect(self):
        if self.vehicle.name == "AirSim":
            selfPosition = self.vehicle.simGetVehiclePose().position
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


