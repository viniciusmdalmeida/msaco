from Control.Control import *
from Avoid.Avoid import *
from Detect.Detect import *
from AlgorithmsSensors.cam_others.Vision_RGB_Depth import *
from Interface.Communication import AirSimCommunication
from Utils.UnrealCommunication import UnrealCommunication

class Start(Thread):
    avoidThread = None
    detect = None

    def __init__(self,routePoints,sensorsAlgorithms={'Vision':[VisionRDSVMTracker]},avoidClass=Avoid,comunication=AirSimCommunication,config_path='config.yml',start_point=None):
        Thread.__init__(self)
        self.start_point = start_point
        self.status = 'start'
        # vehicleComunication = comunication.getVehicle()
        # Conectando ao simulador AirSim
        self.vehicleComunication = AirSimCommunication()
        self.control = Control(self.vehicleComunication,routePoints)
        self.unrealControl = UnrealCommunication()
        self.stop = False

        with open(config_path, 'r') as file_config:
            self.config = yaml.full_load(file_config)

        if avoidClass is not None:
            self.avoidThread  = avoidClass(self,self.control)
        if sensorsAlgorithms is not None:
            self.detect = Detect(self,self.vehicleComunication,sensorsAlgorithms,self.avoidThread)

        #self.start()

    def start_run(self):
        # Start drone
        self.control.takeOff()
        # got to start point
        if self.start_point:
            print("Start point",self.start_point)
            self.vehicleComunication.moveToPoint(self.start_point[:3],self.start_point[3],True)
        # Start move path
        self.control.start()
        time.sleep(2)
        # Start thread detect
        if self.detect is not None:
            self.detect.start()

    def run(self):
        self.start_run()
        #Wating from  time or collision
        max_time = time.time() + self.config['algorithm']['time_max']
        while not self.stop:
            time.sleep(1)
            if time.time() >= max_time:
                print("Max time execution")
                break
        #Reset Plane
        self.end_run()

    def end_run(self):
        #stop detect
        self.detect.stop = True
        if self.detect is not None:
            #Wating detect
            self.detect.join()
        #stop control
        if self.control is not None:
            self.control.join()
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
