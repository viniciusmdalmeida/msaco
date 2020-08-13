import airsim  # pip install airsim
import numpy as np
import time
from datetime import datetime
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from os import listdir,mkdir

class InertialSensorsPrint(AlgorithmSensor):
    name = "InertialSensors Base"

    def __init__(self,detectRoot):
        print('Start',self.name)
        AlgorithmSensor.__init__(self, detectRoot)

    def run(self):
        while True:
            self.saveData(file_name='log_drone')
            time.sleep(1/6)

    def saveData(self,path='Others/CloudPoints/arrays/',file_name='test'):
        #get data from lidar
        data = self.getData(to_str=True)
        #save data
        file = open(f'{path}{file_name}.txt','a')
        file.write(data+"\n")
        file.close()

    def getData(self,to_str=True):
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
        return str(dict_data)

    def getStatus(self):
        return
