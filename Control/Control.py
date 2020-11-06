from Control.Route import *
from Utils.ThreadKillable import *
from Utils.UnrealCommunication import UnrealCommunication

class Control(Thread):
    #avoiding = False
    moving = False
    def __init__(self,vehicleComunication,points,tempo = 0):
        Thread.__init__(self)
        self.vehicle = vehicleComunication
        self.route = Route(points)
        self.tempo = tempo
        self.points = points
        self.unrealControl = UnrealCommunication()

    def startConnection(self):
        pass
        # self.client.connect()

    def takeOff(self):
        self.startConnection()
        self.vehicle.takeOff()

    def run(self):
        print("Control Start")
        self.startConnection()
        self.takeOff()
        print("Takeoff finalized")
        self.moving =True
        self.unrealControl.start_plane()
        self.moveByPath()

    def moveByPoints(self):
        print("Iniciando Rota")
        pontoAtual = 0
        time.sleep(self.tempo)
        while self.route.getNumPoints() > 0:
            ponto = self.route.getNextPoint()
            print("movendo {}".format(ponto))
            self.vehicle.sendRoute(ponto)
            pontoAtual += 1
        print("Fim")

    def moveByPath(self,velocity=10):
        print("Start path",self.points)
        self.vehicle.movePath(self.points,velocity)

    def updatePath(self,points,velocity):
        print("Start update Path")
        self.points = points
        self.vehicle.movePath(points, velocity)

    def updateRota(self,points):
        #print("Update Rota")
        #if not self.avoiding :
        #self.avoiding = True
        self.vehicle.sendRoute(points[0])
        self.route.replanning(points[1:])




