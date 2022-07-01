from Interface.Start import Start
from AlgorithmsSensors.cam.TrackersClass import *
from AlgorithmsSensors.passive.ADS_B import *
from AlgorithmsSensors.Collision_sensor import *
from Detect.FusionData import *
from Avoid.Avoid import *
import pandas as pd
from Utils.UnrealCommunication import UnrealCommunication
from Utils.calc_colision import calc_plane_position
from datetime import datetime
from tqdm import tqdm
import yaml
import os

## import keras
#Read Config
config_path='config.yml'
with open(config_path, 'r') as file_config:
    config = yaml.full_load(file_config)

#Para iniciar o keras

detect_algorithm = {"Vision": VisionCaptureImage}
fusion_algorithm = FusionData_Mean
avoid_algorithm = VerticalAvoid

#Configuração testes
altura = 20
drone_start_point = [1,1,47,10]
routePoints = [[-10,-10,altura,10]]#[[0,-5,altura,10]]

#Get Day
date_now = datetime.now()
date_str = f"{date_now.day}-{date_now.month}_" \
           f"{date_now.hour}-{date_now.minute}"
#out_put file
df_out_put = pd.DataFrame(columns={'algoritmo','status'})

##############################
#           Codigo           #
##############################
angle = 20
colision_point = [100,100,4900]
time_to_colision = config['test']['time_to_colision']
plane_velocity = config['test']['plane_velocity']
print("time_to_colision:",time_to_colision,"plane_velocity:",plane_velocity)
plane_location,plane_rotation = calc_plane_position(angle,colision_point,time_to_colision,plane_velocity)
print("plane_location",plane_location)
print("plane_rotation:",plane_rotation)

#plane_location = [-1200, -1800, (altura+5)*100]
#plane_rotation = [0,0,0]
#Plane location: [-3367.5744622074953, -5906.015147571708, 4870] Plane rotation: [0, 60, 0]

# Reset avião
unreal_communication = UnrealCommunication()
unreal_communication.reset_plane(plane_location, plane_rotation)

#rodando algoritmo
run_simulation = Start(routePoints,detect_algorithm,startPoint=drone_start_point,
                       fusionAlgorithm=fusion_algorithm,avoidClass=avoid_algorithm)
run_simulation.start()
run_simulation.join()
print("Finish Test",detect_algorithm)
#salvando resultado
status = run_simulation.get_status()
df_result = pd.DataFrame({'algoritmo': [detect_algorithm], 'status': [status],'location_plane':[plane_location],
                          'fusion_algo':fusion_algorithm,
                          'avoid_algo':avoid_algorithm,
                          'timestamp':datetime.now().timestamp()})
df_out_put = df_out_put.append(df_result,ignore_index=True,
                               sort=False)

#Finalizando simulação
time.sleep(2.5)
del run_simulation

df_out_put.to_csv(f"{config['test']['out_put_path']}status_out_{date_str}.csv")
print("Finalizado")
'''
##########################################
# AirSim sem usar o programa
##########################################

# Conectando airsim
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
client.takeoffAsync().join()
velocity = 10
client.moveToPositionAsync(-10,-10,-1 * altura,10).join()
for i  in range(10):
    client.rotateByYawRateAsync(10,1)
    #print(f"Drone location:{client.simGetGroundTruthKinematics().position}")
    print(f"Drone orientation:{client.simGetGroundTruthKinematics().orientation}")
    #print(f"Drone imu orientation:{client.getImuData().orientation}")
    #print(f"Drone imu orientation:{client.getImuData().angular_velocity}")
    time.sleep(10)
'''