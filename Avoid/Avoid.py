from threading import Thread
import yaml
from Control.DetectionData import *
import time


class Avoid(Thread):
    detectionData = None
    def __init__(self,control,config_path='config.yml'):
        Thread.__init__(self)
        self.control = control
        with open(config_path, 'r') as file_config:
            self.config = yaml.full_load(file_config)
        self.status = "Inativo"

    def run(self):
        self.status = "Desviando"
        print("Avoid Thread Start!")
        cont = 0
        print("Distancia:", self.detectionData.distance)
        route = [[60, -20, -9],[100, -40, -9],[30, -60, -9]]
        velocity = 3
        self.control.updatePath(route,velocity)
        self.status = "Finalizado"

    def check_colision(self,detectionData):
        if self.status != "Inativo" or \
            detectionData is None or \
            detectionData.distance is None or \
            detectionData.distance > self.config['detect']['min_distance']:
            pass
        else:
            self.detectionData = detectionData
            print("---Desvio---")
            self.run()

