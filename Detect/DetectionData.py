from  os.path import isfile,isdir
from os import makedirs
from datetime import datetime
import numpy as np

class DetectionData:

    def __init__(self,algoritmo):
        now_str = datetime.now().strftime('%Y-%m-%d_%H')
        self.file_path = f'../data/logs_voos/sensor_data_{now_str}.csv'
        self.algoritmo = algoritmo
        self.distance = None
        self.myDirection = None  # (0,0,0)
        self.otherDirection = None  # (0,0,0)
        self.relativePosition = None  # (0,0,0)
        self.relativeDirection = None  # (0,0,0)
        self.myPosition = None  # (0,0,0)
        self.otherPosition = None


    def updateValues(self,key,value):
        if str(key) == 'self':
            return
        if self.__dict__[key] is None:
            self.__dict__[key] = [value]
        else:
            self.__dict__[key].append(value)

    def finalizeData(self):
        args_functions = locals()
        for key in args_functions:
            if str(key) == 'self' or args_functions[key] == None:
                continue
            if type(args_functions[key]) == list:
                if type(args_functions[key][0])  == list:
                    args_functions[key] = args_functions[key][0]
                args_functions[key] = sum(args_functions[key]) / sum(args_functions[key])

    def updateData(self,algoritmo=None,distance=None,relativePosition=None,relativeDirection=None,myDirection=None,
                 otherDirection=None,myPosition=None,otherPosition=None):
        args_functions = locals()
        for arg_name in args_functions:
            value = args_functions[arg_name]
            if value is None and arg_name == 'otherPosition':
                value = self.calcOtherPosition()
            if value is None and arg_name == 'otherDirection':
                value = self.calcOtherDirection()
            if not value is None:
                self.updateValues(arg_name,value)

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

