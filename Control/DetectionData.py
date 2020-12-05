from  os.path import isfile,isdir
from os import makedirs
from datetime import datetime

class DetectionData:
    distance = 0
    myDirection = (0,0,0)
    otherDirection = (0,0,0)
    relativeDirection = (0,0,0)
    myPossition = (0,0,0)
    otherPosition = (0,0,0)

    def __init__(self):
        now_str = datetime.now().strftime('%Y-%m-%d_%H_%M')
        self.file_path = f'../data/logs_voos/sensor_data_{now_str}.csv'

    def updateData(self,distance=None,myDirection=None,relativePosition=None,
                 otherDirection=None,myPosition=None,otherPosition=None):
        self.distance = distance
        self.myPosition = myPosition
        self.myDirection = myDirection
        self.relativePosition= relativePosition
        self.otherPosition = otherPosition

        if otherPosition is None:
            self.otherPosition = self.calcOtherPosition()
        else:
            self.otherPosition = otherDirection

        if otherDirection is None:
            self.otherDirection = self.calcOtherDirection()
        else:
            self.otherPosition = otherDirection

    def calcOtherPosition(self):
        if self.myDirection is not None and self.relativePosition is not None:
            self.otherDirection = (self.myDirection[0] + self.relativePosition[0],
                                   self.myDirection[1] + self.relativePosition[1],
                                   self.myDirection[2] + self.relativePosition[2])
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
            with open(file_path, 'w') as file:
                header = 'timestamp,distance,myX,myY,myZ,myDirX,myDirY,myDirZ,' \
                         'relX,relY,relZ,otherX,otherY,otherZ,' \
                         'otherDirX,otherDirY,otherDirZ'
                file.write(header+'\n')

    def print_data(self):
        timestamp = datetime.timestamp()
        str_print = f'{timestamp},{self.distance},'
        list_datas = [self.myPosition,self.myDirection,
                      self.relativePosition,self.otherPosition,
                      self.otherDirection]
        for data in list_datas:
            str_print = self.add_listdata_str(str_print,data)
        if self.file_path :
            print(self.file_path,':',str_print)
            self.check_have_file(self.file_path)
            with open(self.file_path,'a') as file:
                file.write(str_print+'\n')
        else:
            print(str_print)