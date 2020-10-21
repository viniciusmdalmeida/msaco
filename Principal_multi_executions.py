from Interface.Start import Start
from AlgorithmsSensors.cam.Vision_RGB_Depth import *
from AlgorithmsSensors.cam.Vision_RGB import *
from AlgorithmsSensors.lidar.LidarBase import *
from AlgorithmsSensors.IMU.InertialSensors import *
from AlgorithmsSensors.passive.ADS_B import *
import pandas as pd

list_algorithms = [
    {"ADS_B":ADS_B,"IMU":InertialSensorsPrint},
    {"Vision":Vision_RGB_Depth,"IMU":InertialSensorsPrint},
    {"Vision":VisionRDDefault,"IMU":InertialSensorsPrint},
    {"Vision":VisionRDSVMTracker,"IMU":InertialSensorsPrint},
    {"Vision":Vision_RGB,"IMU":InertialSensorsPrint},
]

list_algorithms = [
    {"ADS_B":ADS_B,"IMU":InertialSensorsPrint},
    {"Vision":Vision_RGB_Depth,"IMU":InertialSensorsPrint},
    {"Vision":VisionRDDefault,"IMU":InertialSensorsPrint}
]

routePoints = [[0,-1,-6,5],[0,-2,-6,5]]
num_execution = 5 #Numero de execução por grupo algoritmo

list_status = []
for algorithm in list_algorithms:
    for count in range(num_execution):
        #Start simples
        print("Iniciando programa")
        run_simulation = Start(routePoints,algorithm)
        run_simulation.start()
        run_simulation.join()
        status = run_simulation.get_status()
        list_status.append(status)
df_out = pd.DataFrame({"Status":list_status})
df_out.to_csv("status_out.csv")
