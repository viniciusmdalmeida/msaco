from AlgorithmsSensors.cam_others.Vision_MOG import *
from Interface.Start import Start

#rotas = [lateral,frente(negativa),cima]
routePoints = [[-1,-2,-6,5]]
algorithm = {"Vision":VisionMOG}

#Start simples
print("Iniciando programa")
run_simulation = Start(routePoints,algorithm)
run_simulation.start()
run_simulation.join()
print("Programa Finalzado")