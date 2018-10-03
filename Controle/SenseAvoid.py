from Detecção.Sensores.Vision import *
from Controle.Controle import *
from Desvio.Desvio import *
from Detecção.Deteccao import *
from MyUtils.Semaphore import *

class SenseAvoid(Thread):
    def __init__(self,control,sensors=['vision'],avoidClass=None,semaphore=None):
        Thread.__init__(self)
        self.sensors = sensors
        self.control = control
        if semaphore is None:
            self.semaphore = Semaphore(True)
        else:
            self.semaphore = semaphore
        if avoidClass is None:
            self.desvioThread = Desvio(self.control)
        else:
            self.desvioThread = avoidClass(self.control)
        self.deteccao = Deteccao(semaphore,self.desvioThread,self.sensors)

    def run(self):
        self.deteccao.start()
        self.desvioThread.start()
        self.deteccao.join()
        self.desvioThread.join()
        # if 'visao' in self.sensores:
        #     print("Ok")
        #     visao = Visao(self.semaphore, self.control,self.desvioThread)
        #     visao.start()
        #     visao.join()