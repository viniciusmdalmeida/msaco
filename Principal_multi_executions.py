from Interface.Start import Start
from AlgorithmsSensors.cam.VisionDepthTracker import *
from AlgorithmsSensors.cam.VisionDepthDetect import *
from AlgorithmsSensors.cam_others.Vision_MOG import *
from AlgorithmsSensors.passive.ADS_B import *
from AlgorithmsSensors.Collision_sensor import *
import pandas as pd
from Utils.UnrealCommunication import UnrealCommunication
from Utils.calc_colision import calc_plane_position
from datetime import datetime
from tqdm import tqdm

#Posição do avião
list_position = [[[-1700, -5900, 700],[0,71,0]],
                 [[750, -5900, 700],[0,95,0]],
                 [[3600, -5900, 700],[0,120,0]],
                 [[-2750, -5900, 700],[0,64,0]],
                 [[400, -5900, 700],[0,93,0]],
                 [[2650, -5900, 700],[0,113,0]]]
#Algoritmos
list_algorithms = [
    {"ADS_B": ADS_B},
    {"Vision": VisionTrackerDepth_MIL},
    {"Vision":VisionTrackerDepth_KFC},
    {"Vision:":VisionTrackerDepth_Boosting},
    {"Vision:": VisionTrackerDepth_TLD},
    {"Vision": VisionTrackerDepth_MIL_MOG},
    {"Vision": VisionTrackerDepth_KFC_MOG},
    {"Vision:": VisionTrackerDepth_Boosting_MOG},
    {"Vision":VisionDetect_SVM},
    {"Vision":VisionDetect_MOG}
]

list_algorithms = [{"Vision": VisionDetect_Neural}]
#Configuração testes
routePoints = [[0,1,-6,5]] #[lateral,frente(negativa),cima,tempo] #em metros
colision_point = [260, 260, 920]
list_angle = [30,20,10,0,-10,-20,-30]
distance_plane = 5000
num_repetitions = 1

#Read Config
config_path='config.yml'
with open(config_path, 'r') as file_config:
    config = yaml.full_load(file_config)
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
for angle in tqdm(list_angle):
    location,rotation = calc_plane_position(angle,distance_plane,colision_point)
    print("Colision:", colision_point)
    print("Plane location:",location,"Plane rotation:",rotation)
    for algorithm in list_algorithms:
        for count in range(num_repetitions):
            #Start simples
            print("\n\n###############")
            print(f"Iniciando execução Algoritmos:{algorithm}, rota:{routePoints}")
            print("###############")
            # Reset avião
            unreal_communication.reset_plane(location, rotation)
            #rodando algoritmo
            run_simulation = Start(routePoints,algorithm)
            run_simulation.start()
            run_simulation.join()
            #salvando resultado
            status = run_simulation.get_status()
            df_result = pd.DataFrame({'algoritmo': [algorithm], 'status': [status],'location_plane':[location],'angle':[angle]})
            df_out_put = df_out_put.append(df_result,ignore_index=True)
            df_out_put.to_csv(f"{config['test']['out_put_path']}status_out_{date_str}.csv")
            #Finalizando simulação
            del run_simulation
            time.sleep(0.5)
print("Finalizado")
