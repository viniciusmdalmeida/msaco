from Interface.SenseAvoid import *
from Avoid.Avoid import *
from Control.Control import *
from MyUtils.Semaphore import *

class Start:
    def __init__(self,routePoints,sensors=['Vision'],algorithms={'Vision':['SVMTracker']},avoid=None):
        # Parametros
        semaphore = Semaphore(True)

        # Conectando ao simulador AirSim
        control = Control(semaphore, routePoints)
        control.moveUAS()

        # Iniciand SenseAvoid
        main = SenseAvoid(control, semaphore, sensors, algorithms,avoid)
        main.start()
