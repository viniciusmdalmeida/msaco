import airsim  # pip install airsim
import time
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor

class Collision_sensor(AlgorithmSensor):
    name = "Colision Sensor"

    def __init__(self,detectRoot):
        print('Start',self.name)
        AlgorithmSensor.__init__(self, detectRoot)
        self.path_file = None

    def run(self):
        pass

    def getData(self):
        colision_info = self.client.simGetCollisionInfo()
        return colision_info.has_collided

    def getInfo(self):
        self.client.simGetCollisionInfo()
