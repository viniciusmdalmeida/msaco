from Control.Control import *
from Avoid.Avoid import *
from Detect.Detect import *
from AlgorithmsSensors.cam_others.Vision_RGB_Depth import *
from Interface.Communication import AirSimCommunication
from Utils.UnrealCommunication import UnrealCommunication

class Start(Thread):
    avoidThread = None
    detect = None

    def __init__(self,routePoints,sensorsAlgorithms={'Vision':[VisionRDSVMTracker]},avoidClass=Avoid,comunication=AirSimCommunication,showVideo=True):
        Thread.__init__(self)
        self.status = 'start'
        # vehicleComunication = comunication.getVehicle()
        # Conectando ao simulador AirSim
        print("Communication")
        self.vehicleComunication = AirSimCommunication()
        self.control = Control(self.vehicleComunication,routePoints)
        self.unrealControl = UnrealCommunication()

        if avoidClass is not None:
            self.avoidThread  = avoidClass(self,self.control)
        if sensorsAlgorithms is not None:
            self.detect = Detect(self,self.vehicleComunication,sensorsAlgorithms,self.avoidThread)
        #self.start()

    def run(self):
        self.control.start()
        #Start thread detect and avoid
        if self.detect is not None:
            self.detect.start()
        #if self.avoidThread is not None:
        #    self.avoidThread.start()
        #Run threads detect and avoid
        if self.detect is not None:
            self.detect.join()
        #if self.avoidThread is not None:
        #    self.avoidThread.join()

    def end_run(self):
        pass

    def get_status(self):
        return self.status

    def set_status(self,status,):
        print("Start status:",status)
        self.status = status
        if status == 'collision':
            self.unrealControl.reset_plane()
            self.vehicleComunication.client.reset()
        if status == "success":
            self.unrealControl.reset_plane()
            self.vehicleComunication.client.reset()
            self.detect.stop = True
