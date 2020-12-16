from  os.path import isfile,isdir
from os import makedirs
from datetime import datetime
import numpy as np

class DetectionData:
    distance = np.inf
    myDirection = None#(0,0,0)
    otherDirection = None#(0,0,0)
    relativePosition = None#(0,0,0)
    relativeDirection = None#(0,0,0)
    myPosition = None#(0,0,0)
    otherPosition = None

    def __init__(self,algoritmo):
        now_str = datetime.now().strftime('%Y-%m-%d_%H')
        self.file_path = f'../data/logs_voos/sensor_data_{now_str}.csv'
        self.algoritmo = algoritmo

    def updateData(self,algoritmo=None,distance=None,relativePosition=None,relativeDirection=None,myDirection=None,
                 otherDirection=None,myPosition=None,otherPosition=None):
        if not algoritmo is None:
            self.algoritmo = algoritmo
        if not distance is None:
            self.distance = distance
        if not myPosition is None:
            self.myPosition = myPosition
        if not myDirection is None:
            self.myDirection = myDirection
        if not relativePosition is None:
            self.relativePosition= relativePosition
        if not relativeDirection is None:
            self.relativeDirection = relativeDirection

        #calc outherPosition
        if not otherPosition is None:
            self.otherPosition = otherPosition
        else:
            self.otherPosition = self.calcOtherPosition()
        #calc outherDirection
        if otherDirection is None:
            self.otherDirection = self.calcOtherDirection()
        else:
            self.otherPosition = otherDirection

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
            if dict_data[key] is None:
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

