from AlgorithmsSensors.cam.Vision_RGB_Depth import  *
from AlgorithmsSensors.cam.VisionSVMTracker import *
from AlgorithmsSensors.cam.Vision_RGB import *
import time

from abc import ABC, abstractmethod

class IDetect(Thread):
    #Interface de detecção
    def __init__(self,vehicleComunication,sensorsAlgorithm,avoidThread):
        Thread.__init__(self)
        self.avoidThread = avoidThread
        self.vehicle = vehicleComunication
        self.sensorsThreads = []
        self.sensorsAlgorithm = sensorsAlgorithm


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
        #Iniciando os algoritmos
        for sensorThread in self.sensorsThreads:
            sensorThread.start()

        #Rodando loop infinito de ler os dados
        while not self.stop:
            dict_sensor_data = {}
            for sensorThread in self.sensorsThreads:
                dict_sensor_data[sensorThread.name] = sensorThread.getStatus()
            #colocar um eval para funsão do algoritmos
            detect_data = self.fusion_data(dict_sensor_data[sensorThread.name])
            if self.checkDetect(detect_data):
                self.avoidThread.detectionData = detect_data
            '''
            if self.vehicle.name == "AirSim":
                 colision = self.vehicle.client.simGetCollisionInfo()
                 if colision.has_collided:
                     print("Colidiu! com ",colision.object_name)
                    # Reset AirSim
                    self.vehicle.reset()
            '''
            time.sleep(0.1)

    def fusion_data(self,list_sensor_data):
        if type(list_sensor_data) == list:
            dict_data = vars(list_sensor_data[0])
            for sensor_data in list_sensor_data[1:]:
                dict_sensor = vars(sensor_data)
                for data in  dict_sensor:
                    if dict_sensor[data] and (dict_data[data] is None):
                        dict_data[data] = dict_sensor[data]
            return dict_data
        else:
            return list_sensor_data

    def checkDetect(self,fusion_data):
        #aprimorar para pegar apenas os dados relevantes
        if fusion_data:
            return True
        return False

    #Terminar essa função que vai receber os dados dos sensores
    def receiveData(self,detectData,name='vision'):
        self.sendData(detectData)

    def sendData(self,detectData):
        self.avoidThread.detectionData = detectData


