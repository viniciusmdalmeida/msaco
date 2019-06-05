from  MyUtils.ThreadKillable import *
import time
from threading import Thread

class Route:
    points = []
    stop = False
    def __init__(self,points):
        self.points = points

    def getNextPoint(self):
        next_point = self.points.pop(0)
        return next_point

    def getPoint(self):
        return self.points

    def replanning(self,points):
        #Esta função pode acrestar logicas para replanejamento
        #Acrescentando por exemplos, restrições de movimento do veiculo
        self.points = points

    def getNumPoints(self):
        return len(self.points)