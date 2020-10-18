from AlgorithmsSensors.cam.Vision_RGB_Depth import  *
from AlgorithmsSensors.cam.VisionSVMTracker import *
from AlgorithmsSensors.cam.Vision_RGB import *
from AlgorithmsSensors.Colision_sensor import *
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
        self.colisionSensor = Colision_sensor()

class Detect(Thread):
    stop = False

    def __init__(self,vehicleComunication,sensorsAlgorithm,avoidThread):
        Thread.__init__(self)
        self.avoidThread = avoidThread
        self.vehicle = vehicleComunication
        self.sensorsThreads = []
        self.sensorsAlgorithm = sensorsAlgorithm
        self.colisionSensor = Colision_sensor(self)


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
            detect_data = self.fusion_data(dict_sensor_data)
            if self.checkDetect(detect_data):
                self.avoidThread.check_colision(detect_data)
            #Colisão
            if self.colisionSensor.getStatus():
                print("Colidiu!")
                self.vehicle.client.reset()
                return
            time.sleep(0.1)

    def fusion_data(self,dict_sensor_data):
        sensor_base = 'ADS_B Base'
        if type(dict_sensor_data[sensor_base]) == list:
            dict_data = vars(dict_sensor_data[sensor_base][0])
            for sensor_data in dict_sensor_data[1:]:
                dict_sensor = vars(sensor_data)
                for data in  dict_sensor:
                    if dict_sensor[data] and (dict_data[data] is None):
                        dict_data[data] = dict_sensor[data]
            return dict_data
        else:
            return dict_sensor_data[sensor_base]

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


