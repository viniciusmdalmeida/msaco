from Control.Control import *
from Avoid.Avoid import *
from Detect.Detect import *

class Start(Thread):
    def __init__(self,routePoints,sensors=['Vision'],algorithms={'Vision':['SVMTracker']},avoidClass=None):
        Thread.__init__(self)
        self.sensors = sensors

        # Parametros
        semaphore = Semaphore(True)

        # Conectando ao simulador AirSim
        self.control = Control(semaphore, routePoints)

        if avoidClass is None:
            self.desvioThread = Avoid(self.control)
        else:
            self.desvioThread = avoidClass(self.control)
        self.deteccao = Detect(semaphore,self.desvioThread,self.sensors,algorithms)

        self.start()

    def run(self):
        self.control.moveUAS()
        self.deteccao.start()
        self.desvioThread.start()
        self.deteccao.join()
        self.desvioThread.join()
