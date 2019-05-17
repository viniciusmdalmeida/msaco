from Interface.Start import Start
from AlgorithmsSensors.cam.Vision_RGB_Depth import VisionRDSVMTracker
from AlgorithmsSensors.cam.Vision_RGB import VisionRGBDefault

routePoints = [[0,-15,0],[0,-25,0],[0,-35,0],[0,-40,0]]

sensor = ["vision"]
algorithm = {"vision":VisionRDSVMTracker}

#Start simples
Start(routePoints)

#Start com lista
#Start(routePoints,sensor)

#Start com dicionario
#Start(routePoints,algorithm)
