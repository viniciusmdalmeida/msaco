import airsim  # pip install airsim
import numpy as np
import time
from datetime import datetime
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from os import listdir,mkdir

class LidarGetData(AlgorithmSensor):
    name = "Lidar Get Data"

    def __init__(self,detectRoot):
        print('Start',self.name)
        AlgorithmSensor.__init__(self, detectRoot)
        self.dir_cloud_point = None
        self.save_path = self.config['sensors']['LIDAR']['save_path']
        self.save_file_prefix = self.config['sensors']['LIDAR']['save_file_prefix']

    def run(self):
        while True:
            self.saveData()
            time.sleep(1/6)

    def saveData(self):
        #create save directory
        if not self.dir_cloud_point:
            now_str = datetime.now().strftime('%Y-%m-%d_%H_%M')
            self.dir_cloud_point = f'{self.save_path}{self.save_file_prefix}_{now_str}'
            mkdir(self.dir_cloud_point)
        #create name of file
        name = str(datetime.now().timestamp()) + '.npz'
        #get data from lidar
        lidarData = self.getData()
        points = np.array(lidarData.point_cloud, dtype=np.dtype('f4'))
        #check if have data
        if len(points) <= 3:
            return
        points = np.reshape(points, (int(points.shape[0] / 3), 3))
        data = np.asarray(points)
        #save file
        file = open(f'{self.dir_cloud_point}\{name}','wb')
        np.savez_compressed(file,data)
        file.close()

    def getData(self):
        lidarData = self.client.getLidarData()
        return lidarData

    def getStatus(self):
        return
