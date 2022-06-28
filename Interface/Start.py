from threading import Thread
from AlgorithmsSensors.cam.TrackersClass import VisionDetectSVM
from Control.Control import *
from Avoid.Avoid import *
from Detect.Detect import *
from Interface.Communication import AirSimCommunication
from Utils.UnrealCommunication import UnrealCommunication

class Start(Thread):
    avoidThread = None
    detect = None

    def __init__(self,routePoints,sensorsAlgorithms={'Vision':[VisionDetectSVM]},
                 avoidClass=FixAvoid,comunication=AirSimCommunication,fusionAlgorithm=FusionData_Mean,
                 configPath='config.yml',startPoint=None):
        print("Simulation Config - Start")
        Thread.__init__(self)
        # Iniciando variaveis
        self.status = 'start'
        self.stop = False
        self.start_point = startPoint

        # Buscando configuração
        with open(configPath, 'r') as file_config:
            self.config = yaml.full_load(file_config)

        # Conectando ao simulador AirSim e Unreal
        self.vehicleComunication = comunication()
        self.control = Control(self.vehicleComunication,routePoints)
        self.unrealControl = UnrealCommunication()

        # Iniciando funções (threads)
        if avoidClass is not None:
            self.avoidThread  = avoidClass(self,self.control)
        if sensorsAlgorithms is not None:
            self.detect = Detect(self,self.vehicleComunication,sensorsAlgorithms,
                                 self.avoidThread,fusionAlgorithm=fusionAlgorithm)
        print("Simulation Config - Finish")
        #self.start()

    def run(self):
        print("-----------------------------------------")
        print("-------- Start Thread :: Beging ---------")
        # Start Execution
        print("Starting Drone ...")
        self.start_run()
        print(f"Drone Started!")

        #Wating from  time or collision
        self.main_loop()

        #Reset Plane
        print(f"Ending Simulation, date:{datetime.now().isoformat()}")
        self.end_run()
        print(f"Finish Simulation")
        print("-------- Start Thread :: Finish --------")
        print("----------------------------------------")

    def main_loop(self):
        max_time = time.time() + self.config['algorithm']['time_max']
        while not self.stop:
            time.sleep(1)
            if time.time() >= max_time:
                print("Max time execution")
                break

    def start_run(self):
        # Start drone

        self.control.takeOff()
        if self.start_point:
            # got to start point
            print("Start point",self.start_point)
            move_point = self.start_point.copy()
            self.vehicleComunication.moveToPoint(move_point[:3],move_point[3],True)
        # Start move path
        self.control.start()
        time.sleep(2)
        # Start thread detect
        if self.detect is not None:
            self.detect.start()

    def end_run(self):
        #stop detect
        self.detect.stop = True
        if self.detect is not None:
            #Wating detect
            self.detect.join()
        #Reset Plane
        self.unrealControl.reset_plane()
        self.vehicleComunication.client.reset()
        #Delete detect thread
        del self.detect

    def get_status(self):
        return self.status

    def set_status(self,status,):
        print("Voo status:",status)
        self.status = status
        if status == 'collision':
            self.detect.stop = True
            self.stop = True
        #if status == "success":
        #    self.unrealControl.reset_plane()
        #    self.vehicleComunication.client.reset()
        #    self.detect.stop = True
