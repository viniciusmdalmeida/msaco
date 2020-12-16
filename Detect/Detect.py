from AlgorithmsSensors.cam_others.VisionSVMTracker import *
from AlgorithmsSensors.Collision_sensor import *
from AlgorithmsSensors.IMU.InertialSensors import *
from Detect.FusionData import *
import time

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

    def __init__(self,startObj,vehicleComunication,sensorsAlgorithm,avoidThread,config_path='config.yml'):
        Thread.__init__(self)
        with open(config_path, 'r') as file_config:
            self.config = yaml.full_load(file_config)
        self.avoidThread = avoidThread
        self.vehicle = vehicleComunication
        self.sensorsAlgorithm = sensorsAlgorithm
        self.collisionSensor = Collision_sensor(self)
        self.inertialSensor = InertialSensor(self)
        self.sensorsThreads = [self.inertialSensor]
        self.startObj = startObj
        self.fusionData = FusionData()

    def startAlgorithms(self):
        for sensor in self.sensorsAlgorithm:
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
            detect_data = DetectionData(None)
            self.fusionData.clearList()
            for sensorThread in self.sensorsThreads:
                dict_sensor_data[sensorThread.name] = sensorThread.getDetectData()
                detect_data.updateData(**dict_sensor_data[sensorThread.name].getDictData())
            #colocar um eval para funsão do algoritmos
            detect_data.print_data()
            self.sendData(detect_data)
            #Colisão
            if self.collisionSensor.check_collision():
                self.startObj.set_status('collision')
                break
            time.sleep(0.1)
            #Observando tempo de execução
            time_exec = time.time()
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




