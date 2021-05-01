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
list_algorithms = [
    {'Vision': ADS_B},
    {'Vision': VisionDetectNaiveBayes},
    {'Vision': VisionDetectSVM},
    {'Vision': VisionDetectLGB},
    {'Vision': VisionDetectNeural},
    {'Vision': VisionDetectRF},
    {'Vision': VisionDetectNaive_Depth},
    {'Vision': VisionDetectSVM_Depth},
    {'Vision': VisionDetectLGB_Depth},
    {'Vision': VisionDetectNeural_Depth},
    {'Vision': VisionDetectRF_Depth},

    {'Vision': VisionTracker_KFC_RF},
    {'Vision': VisionTracker_KFC_LGB},
    {'Vision': VisionTracker_KFC_SVM},
    {'Vision': VisionTracker_KFC_Naive},
    {'Vision': VisionTracker_KFC_RN},

    {'Vision': VisionTracker_KFC_RF_Depth},
    {'Vision': VisionTracker_KFC_LGB_Depth},
    {'Vision': VisionTracker_KFC_SVM_Depth},
    {'Vision': VisionTracker_KFC_Naive_Depth},
    {'Vision': VisionTracker_KFC_RN_Depth},
    {'Vision': VisionTracker_MIL_RF},
    {'Vision': VisionTracker_MIL_LGB},
    {'Vision': VisionTracker_MIL_SVM},
    {'Vision': VisionTracker_MIL_Naive},
    {'Vision': VisionTracker_MIL_RN},

    {'Vision': VisionTracker_MIL_RF_Depth},
    {'Vision': VisionTracker_MIL_LGB_Depth},
    {'Vision': VisionTracker_MIL_SVM_Depth},
    {'Vision': VisionTracker_MIL_Naive_Depth},
    {'Vision': VisionTracker_MIL_RN_Depth},

    {'Vision': VisionTracker_TLD_RF},
    {'Vision': VisionTracker_TLD_LGB},
    {'Vision': VisionTracker_TLD_SVM},
    {'Vision': VisionTracker_TLD_Naive},
    {'Vision': VisionTracker_TLD_RN},

    {'Vision': VisionTracker_TLD_RF_Depth},
    {'Vision': VisionTracker_TLD_LGB_Depth},
    {'Vision': VisionTracker_TLD_SVM_Depth},
    {'Vision': VisionTracker_TLD_Naive_Depth},
    {'Vision': VisionTracker_TLD_RN_Depth},

    {'Vision': VisionTracker_Boosting_RF},
    {'Vision': VisionTracker_Boosting_LGB},
    {'Vision': VisionTracker_Boosting_SVM},
    {'Vision': VisionTracker_Boosting_Naive},
    {'Vision': VisionTracker_Boosting_RN},

    {'Vision': VisionTracker_Boosting_RF_Depth},
    {'Vision': VisionTracker_Boosting_LGB_Depth},
    {'Vision': VisionTracker_Boosting_SVM_Depth},
    {'Vision': VisionTracker_Boosting_Naive_Depth},
    {'Vision': VisionTracker_Boosting_RN_Depth},

]
"""
from keras.models import Model,model_from_json
path_model = '../data/models/'
with open(path_model + 'keras_Xception.json', 'r') as json_file:
    model_json = json_file.read()
model = model_from_json(model_json)
model.load_weights(path_model + 'keras_Xception.h5')
"""

list_fusion_algorithms = [FusionData_Mean]
list_avoid_algorithms = [HorizontalAvoid,VerticalAvoid]
#Posição do avião

#Configuração testes
altura = 26
#routePoints = [[0,1,-altura,10],[0,-10,-altura,confiFinalizado move to pointg['test']['time_to_colision']]] #[lateral,frente(negativa),cima,tempo] #em metros
drone_start_point = [0,1,-altura,10]
routePoints = [[0,1,-altura,10]]
colision_point = [260, 230, 2800]
#list_angle = [30]
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
                    df_out_put = df_out_put.append(df_result,ignore_index=True,
                                                   sort=False)
                    df_out_put.to_csv(f"{config['test']['out_put_path']}status_out_{date_str}.csv")
                    #Finalizando simulação
                    time.sleep(2.5)
                    del run_simulation
print("Finalizado")
#os.system('shutdown -s')
