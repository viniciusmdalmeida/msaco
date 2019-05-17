from Control.Control import *
from Avoid.Avoid import *
from Detect.Detect import *

class Start(Thread):
    def __init__(self,routePoints,sensorsAlgorithms={'Vision':['SVMTracker']},avoidClass=None):
        Thread.__init__(self)
        self.sensorsAlgorithms = sensorsAlgorithms
        # Parametros
        semaphore = Semaphore(True)
        # Conectando ao simulador AirSim
        self.control = Control(semaphore, routePoints)

        if avoidClass is None:
            self.avoidThread = Avoid(self.control)
        else:
            self.avoidThread  = avoidClass(self.control)
        self.deteccao = Detect(semaphore,self.avoidThread,self.sensorsAlgorithms)

        self.start()

    def run(self):
        self.control.moveUAS()
        self.deteccao.start()
        self.avoidThread.start()
        self.deteccao.join()
        self.avoidThread.join()
