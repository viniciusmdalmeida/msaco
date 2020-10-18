from Interface.Simulation import Simulation
from AlgorithmsSensors.cam.Vision_RGB_Depth import *
from AlgorithmsSensors.cam.Vision_RGB import *
from AlgorithmsSensors.lidar.LidarBase import *
from AlgorithmsSensors.IMU.InertialSensors import *
from AlgorithmsSensors.passive.ADS_B import *

routePoints = [[0,-20,-20,5],[50,-20,-20,5]]
algorithm = {"ADS_B":ADS_B,"LIDAR":LidarGetData,"IMU":InertialSensorsPrint}

#Start simples
print("Iniciando programa")
run_simulation = Simulation(routePoints,algorithm)
run_simulation.start()
