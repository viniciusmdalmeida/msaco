from Interface.Simulation import Simulation
from AlgorithmsSensors.cam.Vision_RGB_Depth import *
from AlgorithmsSensors.cam.Vision_RGB import *
from AlgorithmsSensors.lidar.LidarBase import *
from AlgorithmsSensors.IMU.InertialSensors import *
from AlgorithmsSensors.passive.ADS_B import *

list_algorithms = [
    {"ADS_B":ADS_B,"IMU":InertialSensorsPrint},
    {"Vision":Vision_RGB_Depth,"IMU":InertialSensorsPrint},
    {"Vision":VisionRDDefault,"IMU":InertialSensorsPrint},
    {"Vision":VisionRDSVMTracker,"IMU":InertialSensorsPrint},
    {"Vision":Vision_RGB,"IMU":InertialSensorsPrint},
]

routePoints = [[0,-20,-20,5],[50,-20,-20,5]]
num_execution = 5 #Numero de execução por grupo algoritmo

for algorithm in list_algorithms:
    for count in range(num_execution):
        #Start simples
        print("Iniciando programa")
        run_simulation = Simulation(routePoints,algorithm)
        run_simulation.start()
        run_simulation.join()
        status = run_simulation.get_status()
