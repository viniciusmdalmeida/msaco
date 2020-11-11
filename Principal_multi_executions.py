from Interface.Start import Start
from AlgorithmsSensors.cam_others.Vision_RGB_Depth import *
from AlgorithmsSensors.cam_others.VisionRGB import VisionRGBDefault
from AlgorithmsSensors.cam.VisionTracker import *
from AlgorithmsSensors.cam.VisionDepthTracker import *
from AlgorithmsSensors.cam_others.Vision_MOG import *
from AlgorithmsSensors.passive.ADS_B import *
import pandas as pd
from Utils.UnrealCommunication import UnrealCommunication
from datetime import datetime

#Read Config
config_path='config.yml'
with open(config_path, 'r') as file_config:
    config = yaml.full_load(file_config)

#Get Day
date_now = datetime.now()
date_str = f"{date_now.day}-{date_now.month}-{date_now.hour}"

list_algorithms = [
    {"ADS_B": ADS_B},
    {"Vision":VisionMOG},
    {"Vision": VisionRGBDefault}, #Não detecta
    {"Vision":VisionRDDefault}, #Não detecta
    {"Vision:":VisionRDSVM}, #Error tamanho da imagem
    {"Vision:":VisionRDSVMTracker}
]

list_algorithms = [
    #{"ADS_B": ADS_B},
    {"Vision": VisionTrackerDepth_MIL},
    {"Vision":VisionTrackerDepth_KFC},
    {"Vision:":VisionTrackerDepth_Boosting},
    {"Vision:": VisionTrackerDepth_TLD},
]
#list_algorithms = [{"Vision":VisionCaptureImage}]

#rotas = [lateral,frente(negativa),cima] #em metros
routePoints = [[0,2,-6,5]]
list_position = [[[-1700, -5900, 700],[0,71,0]],
                 [[750, -5900, 700],[0,95,0]],
                 [[3600, -5900, 700],[0,120,0]]]
num_repetitions = 1

list_status = []
unreal_communication = UnrealCommunication()
for position in list_position:
    location = position[0]
    rotation = position[1]
    for algorithm in list_algorithms:
        for count in range(num_repetitions):
            #Start simples
            print("\n\n###############")
            print(f"Iniciando execução Algoritmos:{algorithm}, rota:{routePoints}")
            print("###############")
            run_simulation = Start(routePoints,algorithm)
            run_simulation.start()
            run_simulation.join()
            status = run_simulation.get_status()
            list_status.append([algorithm,status])
            unreal_communication.reset_plane(location,rotation)
df_out = pd.DataFrame({"Status":list_status})
df_out.to_csv(f"{config['test']['out_put_path']}status_out_{date_str}.csv")
print("Finalizado")
