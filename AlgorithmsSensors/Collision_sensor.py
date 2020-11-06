import airsim  # pip install airsim
import time
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor

class Collision_sensor(AlgorithmSensor):
    name = "Colision Sensor"

    def __init__(self,detectRoot):
        AlgorithmSensor.__init__(self, detectRoot)
        self.path_file = None

    def run(self):
        pass

    def getData(self):
        self.colision_info = self.client.simGetCollisionInfo()

    def getInfo(self):
        self.client.simGetCollisionInfo()

    def check_collision(self):
        self.getData()
        return self.colision_info.has_collided
