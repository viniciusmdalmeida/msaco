from Controle.SenseAvoid import *
from Desvio.Desvio import *
from Desvio.DesvioParado import *
from Controle.Controle import *
from MyUtils.Semaphore import *

#Parametros
semaphore = Semaphore(True)
sensors = ['vision']
routePoints = [[0,0,-10],[2,0,-10],[2,1,-10],[-2,1,-10],[-2,-1,-10]]

# Conectando ao simulador AirSim
control = Controle(semaphore,routePoints)
control.moveUAS()

#Iniciand SenseAvoid
principal = SenseAvoid(control,sensors,DesvioParado,semaphore)
principal.start()
principal.join()



