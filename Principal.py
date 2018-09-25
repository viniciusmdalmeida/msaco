from Controle.Controle import *
from Controle.SenseAvoid import *
from MyUtils.Semaphore import *
from Desvio.Desvio import *

controleSemaf = Semaphore(True)

# Conectando ao simulador AirSim
principal = SenseAvoid(['visao'],Desvio,semaphore=controleSemaf)

principal.start()
principal.join()



