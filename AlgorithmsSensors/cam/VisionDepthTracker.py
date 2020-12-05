from AlgorithmsSensors.cam.VisionBase import *
from AlgorithmsSensors.cam.DetectObjClasses import *
import time

#class VisionRGBDefault(VisionBase):
class VisionTrackerDepthBase(VisionDepthBase):
    name = "Vision RGB Default Algorithm"

    def __init__(self,detectRoot):
        VisionBase.__init__(self, detectRoot)
        self.tracker = None
        self.detectObject = DetectSVM(self.config)
        #self.detectObject = DetectMog(self.config)
        self.cont_status = 0

    def check_status(self,status):
        if status:
            self.cont_status = 0
            return True
        else:
            self.cont_status += 1
            if self.cont_status >= 5:
                self.cont_status = 0
                return False
        return True

    def start_tracker(self):
        print(f"Start tracker: algorithm {self.name}")
        # Pegando o primeiro frame
        start_frame = self.getImage()
        while len(np.unique(start_frame)) < 20:
            start_frame = self.getImage()
        # Primeira detecção
        bbox,frame = self.firstDetect(start_frame)
        self.tracker.init(frame, bbox)

    def detect(self):
        status = self.updateTracker()
        if not self.check_status(status):
            self.start_tracker()

    def firstDetect(self,start_frame):
        #Pegando o primeiro frame
        bbox = None
        while bbox is None:
            frame = self.getImage()
            bbox = self.detectObject.detect(frame,start_frame)
            self.printDetection(frame,bbox)
        return bbox,frame

    def updateTracker(self):
        frame = self.getImage()
        # Update tracker
        if frame is None:
            return False
        else:
            status_tracker, bbox = self.tracker.update(frame[:, :, :3])
            distanceMin = self.calc_distance(bbox)
            self.detectData.updateData(distance=distanceMin)
            self.printDetection(frame, bbox)
            status = status_tracker and distanceMin
            return status

############################################################
#               SVM
############################################################
class VisionTrackerDepth_KFC(VisionTrackerDepthBase):
    name = "Vision SVM KFC"
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerKCF_create()

class VisionTrackerDepth_TLD(VisionTrackerDepthBase):
    name = "Vision SVM TLD"
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerTLD_create()

class VisionTrackerDepth_MIL(VisionTrackerDepthBase):
    name = "Vision SVM MIL"
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerMIL_create()

class VisionTrackerDepth_Boosting(VisionTrackerDepthBase):
    name = "Vision SVM Boosting"
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerBoosting_create()

############################################################
#               MOG
############################################################
class VisionTrackerDepth_KFC_MOG(VisionTrackerDepthBase):
    name = "Vision SVM KFC"
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerKCF_create()
        self.detectObject = DetectMog(self.config)

class VisionTrackerDepth_TLD_MOG(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerTLD_create()
        self.detectObject = DetectMog(self.config)

class VisionTrackerDepth_MIL_MOG(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerMIL_create()
        self.detectObject = DetectMog(self.config)

class VisionTrackerDepth_Boosting_MOG(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerBoosting_create()
        self.detectObject = DetectMog(self.config)

############################################################
#          Neural Network
############################################################
class VisionTrackerDepth_KFC_MOG(VisionTrackerDepthBase):
    name = "Vision SVM KFC"
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerKCF_create()
        self.detectObject = DetectNeural(self.config)

class VisionTrackerDepth_TLD_MOG(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerTLD_create()
        self.detectObject = DetectNeural(self.config)

class VisionTrackerDepth_MIL_MOG(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerMIL_create()
        self.detectObject = DetectNeural(self.config)

class VisionTrackerDepth_Boosting_MOG(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerBoosting_create()
        self.detectObject = DetectNeural(self.config)

############################################################
#                   Depth Learning
############################################################
class VisionTrackerDepth_KFC_MOG(VisionTrackerDepthBase):
    name = "Vision SVM KFC"
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerKCF_create()
        self.detectObject = DetectKeras(self.config)

class VisionTrackerDepth_TLD_MOG(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerTLD_create()
        self.detectObject = DetectKeras(self.config)

class VisionTrackerDepth_MIL_MOG(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerMIL_create()
        self.detectObject = DetectKeras(self.config)

class VisionTrackerDepth_Boosting_MOG(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerBoosting_create()
        self.detectObject = DetectKeras(self.config)
