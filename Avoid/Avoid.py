from threading import Thread
import yaml
from Control.DetectionData import *
import time
import numpy as np


class Avoid(Thread):
    detectionData = None
    avoiding = False

    def __init__(self, startObj,control, config_path='config.yml'):
        Thread.__init__(self)
        self.startObj = startObj
        self.control = control
        self.progress_data = []
        with open(config_path, 'r') as file_config:
            self.config = yaml.full_load(file_config)
        self.status = "inactive"


    def avoid_strategy(self):
        route = [[20, -20, -9]]
        velocity = 3
        return route,velocity

    def run(self):
        pass
        '''
        self.status = "Desviando"
        print("Avoid Thread Start!")
        while self.status != "success" and self.status != "collision":
            time.sleep(0.1)
        self.status = "Finalizado"
        '''

    def replanning_route(self):
        route, velocity = self.avoid_strategy()
        self.control.updatePath(route, velocity)

    def update_detect_data(self, detectionData):
        self.update_progress(detectionData)
        if detectionData is None or detectionData.distance is None:
            #invalit data
            return
        elif self.status == 'avoiding':
            progress = self.check_progress()
            if progress == 1:
                self.status = "success"
                self.startObj.set_status("success")
            elif progress == 0:
                return
            elif progress == -1:
                print("Progress:",progress)
                print("Progress avoid  is negative")
                self.replanning_route()
        elif self.status == "inactive" and detectionData.distance < self.config['detect']['min_distance']:
            print(f"Start avoid, Distance:{detectionData.distance}")
            self.replanning_route()
            self.status = "avoiding"

    def update_progress(self,detectionData):
        if not detectionData:
            return
        self.progress_data.insert(0, detectionData)
        if len(self.progress_data) > self.config['detect']['max_progress_data']:
            self.progress_data.pop()

    def check_progress(self):
        if not self.progress_data:
            print("Progress Zero!!")
            return 0
        distance_list = []
        for data in self.progress_data:
            distance_list.append(data.distance)
        #verificando se a media de atualizações de distancia é um ponto seguro
        mean_distance = sum(distance_list)/len(distance_list)
        mean_gradient = np.gradient(distance_list).mean()
        if mean_distance > self.config['detect']['min_distance'] \
                and len(distance_list) >= self.config['detect']['max_progress_data']\
                and mean_gradient >= 0:
            print(f"mean_distance:{mean_distance}||mean_gradient:{mean_gradient}||Tamanho:{len(distance_list)}")
            #se é seguro retorna  1 (significa sucesso)
            return 1
        #calculando a inclinação media da curva de distancia, ou seja para que ponto ela aponta em media
        if mean_gradient >= 0:
            # se a inclinação é positiva significa que o drone esta afastando do risco
            return 0
        else:
            # se a inclinação é negativa significa que o drone esta aproximando do risco
            return -1
