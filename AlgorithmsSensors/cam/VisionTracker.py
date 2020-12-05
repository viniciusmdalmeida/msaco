from AlgorithmsSensors.cam.VisionBase import *
from AlgorithmsSensors.cam.DetectObjClasses import *
import time
import numpy as np

#class VisionRGBDefault(VisionBase):
class VisionTrackerBase(VisionDepthBase):
    name = "Vision RGB Default Algorithm"

    def __init__(self,detectRoot,depth_cam=False):
        VisionBase.__init__(self, detectRoot)
        self.tracker = None
        self.detectObject = DetectSVM(self.config)
        #self.detectObject = DetectMog(self.config)
        self.cont_status = 0
        if depth_cam:
            self.getImage = self.getDepth

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
        # Pegando o primeiro frame
        start_frame = self.getImage()
        while len(np.unique(start_frame)) < 20:
            start_frame = self.getImage()
        #Primeira detecção
        bbox,frame = self.firstDetect(start_frame)
        self.tracker.init(frame, bbox)

    def detect(self):
        status = self.updateTracker()
        if not self.check_status(status):
            #restart tracker
            self.start_tracker()

    def firstDetect(self,start_frame):
        bbox = None
        while bbox is None:
            frame = self.getImage()
            bbox = self.detectObject.detect(frame,start_frame)
            self.printDetection(frame,bbox)
        return bbox,frame

    def updateTracker(self):
        frame = self.getImage()
        # Update tracker
        if frame is not None:
            ok, bbox = self.tracker.update(frame[:, :, :3])
            self.printDetection(frame,bbox)
            self.calc_obj_position(bbox)
            return ok
        else:
            return False

class VisionTracker_KFC(VisionTrackerBase):
    def __init__(self,detectRoot):
        VisionTrackerBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerKCF_create()

class VisionTracker_TLD(VisionTrackerBase):
    def __init__(self,detectRoot):
        VisionTrackerBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerTLD_create()

class VisionTracker_MIL(VisionTrackerBase):
    def __init__(self,detectRoot):
        VisionTrackerBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerMIL_create()

class VisionTracker_Boosting(VisionTrackerBase):
    def __init__(self,detectRoot):
        VisionTrackerBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerBoosting_create()


