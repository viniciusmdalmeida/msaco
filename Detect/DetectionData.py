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
        self.myRotation = None
        self.bbox = None
        self.timestamp = None

    def updateData(self,algoritmo=None,distance=None,relativePosition=None,relativeDirection=None,myDirection=None,
                 otherDirection=None,myPosition=None,otherPosition=None, myRotation=None, bbox=None, timestamp=None):
        args_functions = locals()
        for arg_name in args_functions:
            value = args_functions[arg_name]
            if not value is None:
                self.__dict__[arg_name] = value
        if self.otherPosition is None:
            self.__dict__['otherPosition'] = self.calcOtherPosition()
        if self.otherDirection is None:
            self.__dict__['otherDirection'] = self.calcOtherDirection()
        #if not args_functions['bbox'] is None:
        #    print(f"updateData/DetectionData data:{datetime.now().isoformat()} atualizado: {args_functions}")

    def calcOtherPosition(self):
        #print(f"calcOtherPosition:: my:{self.myPosition}, relative: {self.relativePosition}")
        if self.myPosition is not None and self.relativePosition is not None:
            x_position = (self.myPosition[0]) - self.relativePosition[0]
            y_position = (self.myPosition[1]) - self.relativePosition[1]
            z_position = (self.myPosition[2]) - self.relativePosition[2]
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
                         'otherDirX,otherDirY,otherDirZ,rotationW,rotationX,rotationY,rotationZ,' \
                         'bbox1,bbox2,bbox3,bbox4'
                file.write(header+'\n')

    def print_data(self):
        if self.timestamp == None:
            self.timestamp = datetime.now().timestamp()
        str_print = f'{self.timestamp},'
        dict_data = self.getDictData()
        for key in dict_data:
            if key == 'distance' and key == 'algoritmo':
                str_data += str(dict_data[key])
            elif dict_data[key] is None:
                if key == 'bbox':
                    str_data = ',,,'
                else:
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
        dict_Data['myRotation'] = self.myRotation
        dict_Data['bbox'] = self.bbox
        dict_Data['timestamp'] = self.timestamp
        return dict_Data

