from Interface.Start import Start
from AlgorithmsSensors.cam.Vision_RGB_Depth import *
from AlgorithmsSensors.cam.Vision_RGB import *

routePoints = [[10,-5,0,4],[15,-15,0,4],[30,-35,0,4],[40,-40,0,4]]

sensor = ["vision"]
algorithm = {"vision":VisionRGBDefault}

#Start simples
print("Iniciando programa")
Start(routePoints,algorithm)

#Start com lista
#Start(routePoints,sensor)

#Start com dicionario
#Start(routePoints,algorithm)
