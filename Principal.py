from AlgorithmsSensors.cam.Vision_RGB_Depth import *
from AlgorithmsSensors.cam.Vision_RGB import *
from AlgorithmsSensors.lidar.LidarBase import *
from AlgorithmsSensors.IMU.InertialSensors import *
from AlgorithmsSensors.passive.ADS_B import *
from Interface.Start import Start

routePoints = [[0,-1,-6,5],[0,-2,-6,5]]
algorithm = {"IMU":InertialSensorsPrint}

#Start simples
print("Iniciando programa")
run_simulation = Start(routePoints,algorithm)
run_simulation.start()
