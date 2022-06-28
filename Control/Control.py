from Control.Route import *
from Utils.ThreadKillable import *
from Utils.UnrealCommunication import UnrealCommunication

class Control():
    #avoiding = False
    moving = False
    def __init__(self,vehicleComunication,points,tempo = 0):
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
        print("Take Off")

    def start(self):
        print("### Control Thread: Start")
        self.moving =True
        self.unrealControl.start_plane()
        self.moveByPath()
        print("### Control Thread: Finish")

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
        print("control => Start path",self.points)
        self.vehicle.movePath(self.points,velocity)

    def updatePath(self,points,velocity):
        print("control => update Path:",points,velocity)
        self.points = points
        self.vehicle.movePath(points, velocity)

    def move_to_point(self,point,wait=False):
        self.vehicle.moveToPoint(point[:3], point[3],wait)

    def updateRota(self,points):
        #print("Update Rota")
        #if not self.avoiding :
        #self.avoiding = True
        self.vehicle.sendRoute(points[0])
        self.route.replanning(points[1:])




