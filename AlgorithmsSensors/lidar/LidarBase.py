import airsim  # pip install airsim
import numpy as np
import time
from datetime import datetime
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from os import listdir,mkdir

class LidarBase(AlgorithmSensor):
    name = "Lidar Base"

    def __init__(self,detectRoot):
        print('Start',self.name)
        AlgorithmSensor.__init__(self, detectRoot)

    def run(self):
        while True:
            self.saveData()
            time.sleep(1/6)

    def saveData(self,path='Others/CloudPoints/arrays/',name=None,test_name='test',log=True):
        str_time = datetime.now().strftime("%Y-%m-%d_%H")
        test_name += str_time
        #create save directory
        if not test_name in listdir(path):
            mkdir(path+test_name)
        #create name of file
        if name is None:
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
        file = open(f'{path}{test_name}/{name}','wb')
        np.savez_compressed(file,data)
        file.close()
        if log:
            file = open(f'{path}{test_name}/log_lidar.txt','a')
            file.write(str(datetime.now().timestamp()))
            file.close()

    def getData(self):
        lidarData = self.client.getLidarData()
        return lidarData

    def getStatus(self):
        return
