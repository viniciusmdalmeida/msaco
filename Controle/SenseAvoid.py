from Detecção.Sensores.Vision import *
from Controle.Controle import *
from Desvio.Desvio import *

class SenseAvoid(Thread):
    def __init__(self, sensores,classDesvio=None,semaphore=None):
        Thread.__init__(self)
        self.semaphore = semaphore
        self.control = Controle(self.semaphore)
        self.sensores = sensores
        if classDesvio is None:
            self.desvioThread = Desvio(self.control)
        else:
            self.desvioThread = classDesvio(self.control)
    def run(self):
        self.control.moveUAS()
        self.desvioThread.start()
        if 'visao' in self.sensores:
            print("Ok")
            visao = Visao(self.semaphore, self.control,self.desvioThread)
            visao.start()
            visao.join()