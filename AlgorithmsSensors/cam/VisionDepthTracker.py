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
        print(f"Algorithm {self.name} Start Tracker")
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

    def mog2_ObjectDetect(self):
        fgbg = cv2.createBackgroundSubtractorMOG2()
        while True:
            frame = self.getImage()
            fgmask = fgbg.apply(frame)

            thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            contours,hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            if type(contours) is None or len(contours) <= 0:
                continue
            max = contours[0]
            for c in contours:
                if cv2.contourArea(c) >cv2.contourArea(max) :
                    max = c
            # (x, y, w, h) = cv2.boundingRect(max)
            #Desenhando quadrado
            # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2, 1)
            self.printDetection(frame,cv2.boundingRect(max))
            self.detectRoot.receiveData(self.detectData)

    def updateTracker(self):
        frame = self.getImage()
        # Update tracker
        if frame is None:
            return False
        else:
            status_tracker, bbox = self.tracker.update(frame[:, :, :3])
            distanceMin = self.calc_distance(bbox)
            self.detectData = DetectionData(distanceMin)
            self.detectRoot.receiveData(self.detectData)
            self.printDetection(frame, bbox)
            status = status_tracker and distanceMin
            return status

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
