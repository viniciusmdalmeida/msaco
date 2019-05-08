from Interface.SenseAvoid import *
from Avoid.Avoid import *
from Control.Control import *
from MyUtils.Semaphore import *

class Start:
    def __init__(self,routePoints,sensors=None,algorithms=None,avoid=None):
        # Parametros
        semaphore = Semaphore(True)

        # Conectando ao simulador AirSim
        control = Control(semaphore, routePoints)
        control.moveUAS()

        # Iniciand SenseAvoid
        main = SenseAvoid(control, sensors, avoid, semaphore)
        main.start()
