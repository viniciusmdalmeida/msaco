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

## import keras
#Read Config
config_path='config.yml'
with open(config_path, 'r') as file_config:
    config = yaml.full_load(file_config)

#Para iniciar o keras
"""
from keras.models import Model,model_from_json
path_model = '../data/models/'
with open(path_model + 'keras_Xception.json', 'r') as json_file:
    model_json = json_file.read()
model = model_from_json(model_json)
model.load_weights(path_model + 'keras_Xception.h5')
"""

list_algorithms = [
    {"ADS-B":ADS_B,"Vision Depth": VisionTracker_KFC_SVM_Depth,"Vision RGB": VisionDetectRF},
]
list_fusion_algorithms = [FusionData_Mean]
list_avoid_algorithms = [HorizontalAvoid]
#Posição do avião

#Configuração testes
altura = 28
#routePoints = [[0,1,-altura,10],[0,-10,-altura,confiFinalizado move to pointg['test']['time_to_colision']]] #[lateral,frente(negativa),cima,tempo] #em metros
drone_start_point = [0,1,-altura,10]
routePoints = [[0,1,-altura,10]]
colision_point = [260, 230, 2800]
list_angle = [30,20,10,0,-10,-20,-30]
distance_plane = 5000
num_repetitions = 1

#Get Day
date_now = datetime.now()
date_str = f"{date_now.day}-{date_now.month}_" \
           f"{date_now.hour}-{date_now.minute}"
#out_put file
df_out_put = pd.DataFrame(columns={'algoritmo','status'})

##############################
#           Codigo           #
##############################
list_status = []
unreal_communication = UnrealCommunication()
time_to_colision = config['test']['time_to_colision']
plane_velocity = config['test']['plane_velocity']
for angle in tqdm(list_angle):
    location,rotation = calc_plane_position(angle,colision_point,time_to_colision,plane_velocity)
    print("Colision:", colision_point)
    print("Plane location:",location,"Plane rotation:",rotation)
    for avoid_algorithm in list_avoid_algorithms:
        print(f"Avoid algorithm:{avoid_algorithm}")
        for fusion_algorithm in  list_fusion_algorithms:
            print(f"Fusion algorithm:{fusion_algorithm}")
            for algorithm in list_algorithms:
                for count in range(num_repetitions):
                    #Start simples
                    print("\n###############")
                    print(f"Iniciando execução Algoritmos:{algorithm}, rota:{routePoints}")
                    print("###############")
                    # Reset avião
                    unreal_communication.reset_plane(location, rotation)
                    #rodando algoritmo
                    run_simulation = Start(routePoints,algorithm,startPoint=drone_start_point,
                                           fusionAlgorithm=fusion_algorithm,avoidClass=avoid_algorithm)
                    run_simulation.start()
                    run_simulation.join()
                    print("Finish Test",algorithm)
                    #salvando resultado
                    status = run_simulation.get_status()
                    df_result = pd.DataFrame({'algoritmo': [algorithm], 'status': [status],'location_plane':[location],
                                              'angle':[angle], 'fusion_algo':fusion_algorithm,
                                              'avoid_algo':avoid_algorithm})
                    df_out_put = df_out_put.append(df_result,ignore_index=True)
                    df_out_put.to_csv(f"{config['test']['out_put_path']}status_out_{date_str}.csv")
                    #Finalizando simulação
                    time.sleep(2.5)
                    del run_simulation
print("Finalizado")
