from abc import ABC, abstractmethod
from threading import Thread
import time

class ICommunication(ABC,Thread):
    #cliente is the source of communication with vehicle
    client = None
    name = "base"

    def __init__(self):
        super().__init__()

    def getVehicle():
        pass
        # function to get instance of singleton

    @abstractmethod
    def connect(self):
        # function to connect to the vehicle
        pass

    @abstractmethod
    def getSensorsData(self,sensor=None,**kargs):
        #function to get the data from a particular sensor
        pass

    @abstractmethod
    def sendCommand(self,command):
        #function to send a command to vehicle
        pass

    @abstractmethod
    def sendRoute(self,nextPoint):
        # function to send a command to vehicle to got to a certain point
        pass

    @abstractmethod
    def disconnect(self):
        # function to disconnect from the vehicle
        pass

    def sendMavlinkCommand(self,command):
        # function to send a command, in mavLink format, to vehicle to got to a certain point
        # This function return the command response data
        pass

    def run(self):
        print("Thread")

import airsim
import numpy as np
class AirSimCommunication(ICommunication):
    __instance = None
    name = "AirSim"

    # def getVehicle():
    #     if AirSimCommunication.__instance == None:
    #         AirSimCommunication()
    #     return AirSimCommunication.__instance

    def __init__(self):
        # if AirSimCommunication.__instance != None:
        #     raise Exception("This class is a singleton, use getInstance method.")
        # else:
        super().__init__()
        self.client = airsim.MultirotorClient()
        self.connect()
        # AirSimCommunication.__instance = self

    def connect(self):
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)

    def takeOff(self):
        # Async methods returns Future. Call join() to wait for task to complete.
        self.client.takeoffAsync().join()

    def getSensorsData(self,sensor,**kargs):
        if sensor is "cam":
            response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
            response = response[0]
            img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
            img_rgba = img1d.reshape(response.height, response.width, 4)
            return  img_rgba
        elif sensor is "dcam":
            response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthPlanner, True)])
            response = response[0]
            img1d = airsim.list_to_2d_float_array(response.image_data_float, response.width, response.height)
            return img1d
        else:
            return None

    def sendCommand(self,command):
        print("connect")

    def sendRoute(self,nextPoint):
        if len(nextPoint) > 3:
            velocity = nextPoint[3]
        else:
            velocity = 3
        self.client.moveToPositionAsync(nextPoint[0], nextPoint[1], nextPoint[2], velocity).join()

    def disconnect(self):
        self.client.armDisarm(False)
        self.client.reset()
        self.client.enableApiControl(False)

    def __str__(self):
        return "AirSimCommunication"


