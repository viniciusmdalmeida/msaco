from Avoid.Avoid import *
from Detect.Detect import *


class SenseAvoid(Thread):
    def __init__(self,control,semaphore,sensors=['vision'],algorithms={'vision':'SVMTracker'},avoidClass=None):
        Thread.__init__(self)
        self.sensors = sensors
        self.control = control
        self.semaphore = semaphore
        if avoidClass is None:
            self.desvioThread = Avoid(self.control)
        else:
            self.desvioThread = avoidClass(self.control)
        self.deteccao = Detect(semaphore,self.desvioThread,self.sensors,algorithms)

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