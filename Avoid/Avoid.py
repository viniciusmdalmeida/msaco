from threading import Thread
import yaml
from Control.DetectionData import *
import time


class Avoid(Thread):
    detectionData = None
    avoiding = False

    def __init__(self, control, config_path='config.yml'):
        Thread.__init__(self)
        self.control = control
        with open(config_path, 'r') as file_config:
            self.config = yaml.full_load(file_config)
        self.status = "Inativo"

    def run(self):
        self.status = "Desviando"
        print("Avoid Thread Start!")
        print("Distancia:", self.detectionData.distance)
        route = [[20, -20, -9]]
        velocity = 3
        self.control.updatePath(route, velocity)
        self.status = "Finalizado"

    def check_risk_colision(self, detectionData):
        if self.status != "Inativo" or \
                detectionData is None or \
                detectionData.distance is None or \
                detectionData.distance > self.config['detect']['min_distance']:
            pass
        else:
            self.detectionData = detectionData
            print("---Desvio---")
            self.run()
