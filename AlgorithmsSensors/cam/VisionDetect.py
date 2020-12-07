from AlgorithmsSensors.cam.VisionBase import *
from AlgorithmsSensors.cam.DetectObjClasses import *
import time

#class VisionRGBDefault(VisionBase):
class VisionDetectBase(VisionDepthBase):
    name = "Vision RGB Default Algorithm"

    def __init__(self,detectRoot):
        VisionBase.__init__(self, detectRoot)
        self.depth = False
        self.tracker = None
        self.detectObject = DetectSVM(self.config)
        #self.detectObject = DetectMog(self.config)
        self.cont_status = 0
        self.status = 'start'

    def detect(self):
        #Pegando o primeiro frame
        if self.status == 'start':
            self.base_frame = self.getImage()
        #Detectando avião
        frame = self.getImage()
        bbox = self.detectObject.detect(frame,self.base_frame)
        if self.depth == True:
            frame = self.normalize_image(frame)
        self.printDetection(frame,bbox)
        if bbox:
            # Se detectado enviar dados
            distanceMin = self.calc_distance(bbox)
            self.detectData.updateData(distance=distanceMin)
            #Atualizar os frame base e o status
            self.base_frame = self.getImage()
            self.status = 'detect'
        else:
            #Se não detectado atualizar o status
            self.status = 'lost'

class VisionDetect_SVM(VisionDetectBase):
    def __init__(self,detectRoot):
        VisionDetectBase.__init__(self, detectRoot)
        self.detectObject = DetectSVM(self.config)

class VisionDetect_MOG(VisionDetectBase):
    def __init__(self,detectRoot):
        VisionDetectBase.__init__(self, detectRoot)
        self.detectObject = DetectMog(self.config)

class VisionDetect_Neural(VisionDetectBase):
    def __init__(self,detectRoot):
        VisionDetectBase.__init__(self, detectRoot)
        self.detectObject = DetectNeural(self.config)

class VisionDetect_Keras(VisionDetectBase):
    def __init__(self,detectRoot):
        VisionDetectBase.__init__(self, detectRoot)
        self.detectObject = DetectKeras(self.config)


class VisionDetectDepth_SVM(VisionDetectBase):
    def __init__(self,detectRoot):
        print("Vision Detect Depth")
        VisionDetectBase.__init__(self, detectRoot)
        self.detectObject = DetectSVM(self.config)
        self.depth = True

    def getImage(self):
        return self.getDepth()