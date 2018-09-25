from threading import Thread
import airsim
from Controle.Route import *

class Controle():
    desvio = False
    def startConnection(self):
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)

    def __init__(self,semaphore):
        Thread.__init__(self)
        self.semaphore = semaphore

    def moveUAS(self):
        self.startConnection()
        self.client.armDisarm(True)
        # Async methods returns Future. Call join() to wait for task to complete.
        self.client.takeoffAsync().join()
        self.semaphore.value = False
        routePoints = [[0,0,-10],[2,0,-10],[2,1,-10],[-2,1,-10],[-2,-1,-10]]
        self.route = Route(self.client,routePoints)
        self.route.start()

    def updateRota(self,listaPontos):
        print("Update Rota")
        if not self.desvio :
            self.desvio = True
            self.route.terminate()
            rotaFuga = Route(self.client, listaPontos)
            rotaFuga.tempo = 0
            rotaFuga.start()
            # self.rota.join() #Tratar isso!!!!!!
            self.route = rotaFuga





