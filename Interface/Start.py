from Control.Control import *
from Avoid.Avoid import *
from Detect.Detect import *
from Interface.Communication import AirSimCommunication

class Start(Thread):
    def __init__(self,routePoints,sensorsAlgorithms={'Vision':[VisionRDSVMTracker]},avoidClass=None,comunication=AirSimCommunication):
        Thread.__init__(self)
        # vehicleComunication = comunication.getVehicle()
        # Conectando ao simulador AirSim
        vehicleComunication = AirSimCommunication()
        self.control = Control(vehicleComunication,routePoints)

        if avoidClass is None:
            self.avoidThread = Avoid(self.control)
        else:
            self.avoidThread  = avoidClass(self.control)
        self.deteccao = Detect(vehicleComunication,sensorsAlgorithms,self.avoidThread)

        self.start()

    def run(self):
        self.control.start()
        self.deteccao.start()
        self.avoidThread.start()
        self.deteccao.join()
        self.avoidThread.join()
