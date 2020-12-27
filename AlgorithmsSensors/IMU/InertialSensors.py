import airsim  # pip install airsim
import numpy as np
import time
from datetime import datetime
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from Detect.DetectionData import *
from os import listdir,mkdir

class InertialSensor(AlgorithmSensor):
    name = "InertialSensors Base"

    def __init__(self,detectRoot):
        AlgorithmSensor.__init__(self, detectRoot)
        self.path_file = None
        self.detectData = DetectionData(None)

    def detect(self):
        data = self.getData()
        self.detectData.updateData(myPosition=list(data['position'].values()))

    def getData(self):
        dict_data = {}
        gps_location = self.client.simGetGroundTruthEnvironment().geo_point#self.client.getGpsLocation()
        position = self.client.simGetGroundTruthKinematics().position
        orientation = self.client.simGetGroundTruthKinematics().orientation
        velocity = self.client.simGetGroundTruthKinematics().linear_velocity

        dict_data['gps'] = vars(gps_location)
        dict_data['position'] = vars(position)
        dict_data['orientation'] = vars(orientation)
        dict_data['velocity'] = vars(velocity)
        dict_data['time'] = str(datetime.now().timestamp())
        return dict_data

    def getStatus(self):
        return

    def getDetectData(self):
        return self.detectData

class InertialSensorPrint(InertialSensor):
    def detect(self):
        data = self.getData()
        self.detectData.updateData(myPosition=tuple(data['position'].values()))
        self.saveData(str(data), file_name='log_drone')

    def saveData(self, data, path='../data/logs_voos/', file_name='log_drone'):
        # get data from lidar
        if not self.path_file:
            now_str = datetime.now().strftime('%Y-%m-%d_%H_%M')
            self.path_file = f'{path}{file_name}_{now_str}.txt'
        # save data
        file = open(self.path_file, 'a')
        str_data = str(data).replace("'", '"') + ",\n"
        file.write(str_data)
        file.close()
