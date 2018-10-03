from threading import Thread
import airsim
from Controle.Route import *

class Controle():
    desvio = False
    def __init__(self,semaphore,route):
        Thread.__init__(self)
        self.semaphore = semaphore
        self.inicialRoute = route

    def startConnection(self):
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)

    def moveUAS(self):
        self.startConnection()
        self.client.armDisarm(True)
        # Async methods returns Future. Call join() to wait for task to complete.
        self.client.takeoffAsync().join()
        self.semaphore.value = False
        self.route = Route(self.client,self.inicialRoute,30)
        self.route.start()

    def updateRota(self,listaPontos):
        print("Update Rota")
        if not self.desvio :
            self.desvio = True
            if self.route.is_alive():
                self.route.terminate()
            rotaFuga = Route(self.client, listaPontos,0)
            rotaFuga.start()
            # self.rota.join() #Tratar isso!!!!!!
            self.route = rotaFuga





