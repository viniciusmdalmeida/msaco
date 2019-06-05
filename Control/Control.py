from Control.Route import *
from MyUtils.ThreadKillable import *

class Control(Thread):
    desvio = False
    moving = False
    def __init__(self,vehicleComunication,points,tempo = 0):
        Thread.__init__(self)
        self.client = vehicleComunication
        self.route = Route(points)
        self.tempo = tempo

    def startConnection(self):
        pass
        # self.client.connect()

    def moveUAS(self):
        self.startConnection()
        self.client.takeOff()

    def run(self):
        self.startConnection()
        self.moveUAS()
        self.moving =True
        self.move()

    def move(self):
        print("Iniciando Rota")
        pontoAtual = 0
        time.sleep(self.tempo)
        while self.route.getNumPoints() > 0:
            ponto = self.route.getNextPoint()
            print("movendo {}".format(ponto))
            self.client.sendRoute(ponto)
            pontoAtual += 1
        print("Fim")

    def updateRota(self,points):
        print("Update Rota")
        if not self.desvio :
            self.desvio = True
            self.client.sendRoute(points[0])
            self.route.replanning(points[1:])




