from threading import Thread
from Detect.FusionData import *
import time
from AlgorithmsSensors.Collision_sensor import *
from AlgorithmsSensors.IMU.InertialSensors import *

"""
class IDetect(Thread):
    #Interface de detecção
    def __init__(self,vehicleComunication,sensorsAlgorithm,avoidThread):
        Thread.__init__(self)
        self.avoidThread = avoidThread
        self.vehicle = vehicleComunication
        self.sensorsThreads = []
        self.sensorsAlgorithm = sensorsAlgorithm
        self.collisionSensor = Collision_sensor()
        self.fusionData = FusionData()
"""

class Detect(Thread):
    stop = False

    def __init__(self,startObj,vehicleComunication,sensorsAlgorithm,avoidThread,configPath='config.yml',fusionAlgorithm=FusionData_Mean):
        Thread.__init__(self)
        print("Start Detect Class")
        with open(configPath, 'r') as file_config:
            self.config = yaml.full_load(file_config)
        self.avoidThread = avoidThread
        self.vehicle = vehicleComunication
        self.sensorsAlgorithm = sensorsAlgorithm
        self.collisionSensor = Collision_sensor(self)
        self.inertialSensor = InertialSensor(self)
        self.sensorsThreads = [self.inertialSensor]
        self.startObj = startObj
        self.fusionData = fusionAlgorithm()

    def startAlgorithms(self):
        for sensor in self.sensorsAlgorithm:
            print("Create Algoritmo Obj:",self.sensorsAlgorithm[sensor])
            newAlgorithm = self.sensorsAlgorithm[sensor](self)
            self.sensorsThreads.append(newAlgorithm)

    def run(self):
        self.startAlgorithms()
        #Iniciando os algoritmos
        for sensorThread in self.sensorsThreads:
            sensorThread.start()

        #Rodando loop infinito de ler os dados
        while not self.stop:
            self.fusionData.clearList()
            for sensorThread in self.sensorsThreads:
                detect_data = DetectionData()
                detect_data.updateData(**sensorThread.getDetectData().getDictData())
                if detect_data.myPosition is None:
                    detect_data.updateData(myPosition=self.fusionData.get_my_position())
                self.fusionData.addDetect(detect_data)
            detect_data_final = self.fusionData.getFusion()
            # TODO: Remover isso!
            algoritmos = '|'.join(detect_data_final.algoritmo)
            detect_data_final.algoritmo = f'detect: "{algoritmos}"@'\
                                          f'avoid: "{self.avoidThread.__class__.__name__}"@'\
                                          f'fusion: "{self.fusionData.__class__.__name__}"'
            # TODO: Remover ate aqui
            detect_data_final.print_data()
            self.sendData(detect_data_final)
            # Colisão
            if self.collisionSensor.check_collision():
                self.startObj.set_status('collision')
                break
            time.sleep(0.1)
        self.end_run()

    def norm_data(self,dict_sensor_data):
        dict_data = {}
        for sensor_key in dict_sensor_data:
            sensor_data = vars(dict_sensor_data[sensor_key])
            for data_key in  sensor_data:
                data = sensor_data[data_key]
                print(sensor_data,data_key,data)
                if data_key in dict_data:
                    dict_data[data_key] = dict_data[data_key].append(data)
                else:
                    dict_data[data_key] = [data]
        for data_key in dict_data:
            print(data_key,":",dict_data[data_key])
            dict_data[data_key] = self.fusion_data(dict_data[data_key])
        return dict_data

    def fusion_data(self,list_data):
        if type(list_data) == list:
            return list_data[0]
        else:
            return list_data

    #Terminar essa função que vai receber os dados dos sensores
    def receiveData(self,detectData,name='vision'):
        pass
        #self.sendData(detectData)

    def sendData(self,detectData):
        self.avoidThread.update_detect_data(detectData)

    def end_run(self):
        print("End Detect")
        for thread in self.sensorsThreads:
            thread.terminate()
            thread.join()
            print("Thread Terminate",thread.name)




