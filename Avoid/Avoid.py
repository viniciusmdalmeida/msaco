from threading import Thread
import yaml
import numpy as np
from abc import ABC, abstractmethod


class BaseAvoid(Thread,ABC):
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

    @abstractmethod
    def avoid_strategy(self,detection_data):
        pass

    def run(self):
        pass
        '''
        self.status = "Desviando"
        print("Avoid Thread Start!")
        while self.status != "success" and self.status != "collision":
            time.sleep(0.1)
        self.status = "Finalizado"
        '''

    def replanning_route(self,detectionData):
        route, velocity = self.avoid_strategy(detectionData)
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
                self.replanning_route(detectionData)
        elif self.status == "inactive" and detectionData.distance < self.config['detect']['min_distance']:
            print(f"Start avoid, Distance:{detectionData.distance}")
            self.replanning_route(detectionData)
            self.status = "avoiding"

    def update_progress(self,detectionData):
        if not detectionData:
            return
        self.progress_data.append(detectionData)
        if len(self.progress_data) > self.config['detect']['max_progress_data']:
            self.progress_data.pop(0)

    def check_progress(self):
        if len(self.progress_data) < self.config['detect']['min_progress_data']:
            return 0
        distance_list = []
        for data in self.progress_data:
            if data.distance:
                distance_list.append(data.distance)
        if len(distance_list)<= 0:
            print("distance list pequneo")
            return 0
        #verificando se a media de atualizações de distancia é um ponto seguro
        mean_distance = sum(distance_list)/len(distance_list)
        mean_gradient = np.gradient(distance_list).mean()
        print("Gradiente:",mean_gradient)
        if mean_distance > self.config['detect']['min_distance'] \
                and len(distance_list) >= self.config['detect']['max_progress_data']\
                and mean_gradient > 0:
            print(f'mean_distance:{mean_distance}, len(distance_list):{len(distance_list)},mean_gradient:{mean_gradient}')
            print('distance list',distance_list)
            #se é seguro retorna  1 (significa sucesso)
            return 1
        #calculando a inclinação media da curva de distancia, ou seja para que ponto ela aponta em media
        if mean_gradient >= 0:
            # se a inclinação é positiva significa que o drone esta afastando do risco
            return 0
        else:
            #se a inclinação é negativa significa que o drone esta aproximando do risco
            #Reinicia a lista de progresso e retorna erro
            self.progress_data = []
            return -1

class FixAvoid(BaseAvoid):
    def avoid_strategy(self,detection_data):
        route = [[0, 1, -40]]
        velocity = 8
        return route, velocity

class VerticalAvoid(BaseAvoid):
    def avoid_strategy(self,detection_data):
        print('detection_data',detection_data.getDictData())
        my_position = detection_data.getDictData()['myPosition']
        other_position = detection_data.getDictData()['otherPosition']
        if my_position and other_position and my_position[2] and other_position[2]:
            high_diference = (my_position[2]*-1) - other_position[2]
            print('high_diference',high_diference)
            if high_diference > 0:
                #sobe
                my_position[2] -= 10
            elif my_position[2] > -10:
                #desce
                my_position[2] += 10
            else:
                #vai para o ponto mais baixo
                my_position[2] = -2
        print('new my_position:',[list(my_position)],8)
        return [list(my_position)],8

class HorizontalAvoid(BaseAvoid):
    def avoid_strategy(self,detection_data):
        my_position = detection_data.getDictData()['myPosition']
        other_position = detection_data.getDictData()['otherPosition']
        if my_position[1] and other_position[1]:
            horizontal_diference = my_position[1] - other_position[1]
            if horizontal_diference > 0:
                #direita
                my_position[1] -= 60
            else:
                #vai para o ponto mais baixo
                my_position[1] += 60
        return [list(my_position)],8