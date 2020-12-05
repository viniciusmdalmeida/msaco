from AlgorithmsSensors.cam_others.VisionSVMTracker import *
from AlgorithmsSensors.Collision_sensor import *
import time


class IDetect(Thread):
    #Interface de detecção
    def __init__(self,vehicleComunication,sensorsAlgorithm,avoidThread):
        Thread.__init__(self)
        self.avoidThread = avoidThread
        self.vehicle = vehicleComunication
        self.sensorsThreads = []
        self.sensorsAlgorithm = sensorsAlgorithm
        self.collisionSensor = Collision_sensor()

class Detect(Thread):
    stop = False

    def __init__(self,startObj,vehicleComunication,sensorsAlgorithm,avoidThread,config_path='config.yml'):
        Thread.__init__(self)
        with open(config_path, 'r') as file_config:
            self.config = yaml.full_load(file_config)
        self.avoidThread = avoidThread
        self.vehicle = vehicleComunication
        self.sensorsThreads = []
        self.sensorsAlgorithm = sensorsAlgorithm
        self.collisionSensor = Collision_sensor(self)
        self.startObj = startObj

    def startAlgorithms(self):
        for sensor in self.sensorsAlgorithm:
            if type(self.sensorsAlgorithm[sensor]) is list:
                for algorithm in self.sensorsAlgorithm[sensor]:
                    newAlgorithm = algorithm(self)
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
                dict_sensor_data[sensorThread.name] = sensorThread.getDetectData()
            #colocar um eval para funsão do algoritmos
            detect_data = self.fusion_data(dict_sensor_data)
            self.sendData(detect_data)
            #Colisão
            if self.collisionSensor.check_collision():
                self.startObj.set_status('collision')
                break
            time.sleep(0.1)
            #Observando tempo de execução
            time_exec = time.time()
        self.end_run()

    def fusion_data(self,dict_sensor_data):
        sensor_base = list(dict_sensor_data.keys())[0]
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



