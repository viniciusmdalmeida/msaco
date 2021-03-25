from  os.path import isfile,isdir
from os import makedirs
from datetime import datetime
import numpy as np

class DetectionData:

    def __init__(self,algoritmo=''):
        now_str = datetime.now().strftime('%Y-%m-%d_%H')
        self.file_path = f'../data/logs_voos/sensor_data_{now_str}.csv'
        self.algoritmo = algoritmo
        self.distance = np.inf
        self.myDirection = None  # (0,0,0)
        self.otherDirection = None  # (0,0,0)
        self.relativePosition = None  # (0,0,0)
        self.relativeDirection = None  # (0,0,0)
        self.myPosition = None  # (0,0,0)
        self.otherPosition = None

    def updateData(self,algoritmo=None,distance=np.inf,relativePosition=None,relativeDirection=None,myDirection=None,
                 otherDirection=None,myPosition=None,otherPosition=None):
        args_functions = locals()
        for arg_name in args_functions:
            value = args_functions[arg_name]
            if not value is None:
                self.__dict__[arg_name] = value
        if self.otherPosition is None:
            self.__dict__['otherPosition'] = self.calcOtherPosition()
        if self.otherDirection is None:
            self.__dict__['otherDirection'] = self.calcOtherDirection()

    def calcOtherPosition(self):
        if self.myPosition is not None and self.relativePosition is not None:
            x_position = self.myPosition[0] +\
                         self.relativePosition[0]
            y_position = self.myPosition[1] - self.relativePosition[1]
            z_position = self.myPosition[2]*-1
            otherPosition = (x_position,y_position,z_position)
            return otherPosition
        else:
            return None

    def calcOtherDirection(self):
        pass

    def add_listdata_str(self,str,listdata):
        if listdata:
            str += f"{listdata[0]},{listdata[1]},{listdata[2]},"
        else:
            str += ',,,'
        return str

    def check_have_file(self,file_path):
        if isfile(file_path) == False:
            file_name = file_path.split('/')[-1]
            path = file_path.replace(file_name, '')
            if isdir(path) == False:
                makedirs(path)
            with open(file_path, 'a') as file:
                header = 'timestamp,algoritmo,distance,myX,myY,myZ,myDirX,myDirY,myDirZ,' \
                         'relX,relY,relZ,reldirX,reldirY,reldirZ,otherX,otherY,otherZ,' \
                         'otherDirX,otherDirY,otherDirZ'
                file.write(header+'\n')

    def print_data(self):
        timestamp = datetime.now().timestamp()
        str_print = f'{timestamp},'
        dict_data = self.getDictData()
        for key in dict_data:
            if key == 'distance' and key == 'algoritmo':
                str_data += str(dict_data[key])
            elif dict_data[key] is None:
                str_data = ',,'
            else:
                str_data = str(dict_data[key]).replace(')', '').replace('(', '')
            str_print += str_data+","
        if self.file_path:
            self.check_have_file(self.file_path)
            with open(self.file_path,'a') as file:
                file.write(str_print+'\n')

    def getDictData(self):
        dict_Data = {}
        dict_Data['algoritmo'] = self.algoritmo
        dict_Data['distance'] = self.distance
        dict_Data['myPosition'] = self.myPosition
        dict_Data['myDirection'] = self.myDirection
        dict_Data['relativePosition'] = self.relativePosition
        dict_Data['relativeDirection'] = self.relativeDirection
        dict_Data['otherPosition'] = self.otherPosition
        dict_Data['otherDirection'] = self.otherDirection
        return dict_Data

