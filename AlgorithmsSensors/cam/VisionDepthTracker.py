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

    def run(self):
        print("Iniciando",self.name)
        start = time.time()
        time_max = start + self.config['algorithm']['time_max']
        while True:
            #Verificando se algum objeto saliente
            bbox = self.firstDetect()
            frame = self.getImage()
            print('bbox:', bbox)
            self.tracker.init(frame, bbox)
            print("Tracker Iniciado")
            tracker_status = True
            while self.check_status(tracker_status):
                tracker_status = self.updateTracker()
            if time.time() > time_max:
                print("Acabou o tempo!")
                break

    def firstDetect(self):
        #Pegando o primeiro frame
        primeroFrame = self.getImage()
        while len(np.unique(primeroFrame)) < 20:
            primeroFrame = self.getImage()
        bbox = None
        while bbox is None:
            frameAtual = self.getImage()
            bbox = self.detectObject.detect(frameAtual,primeroFrame)
            self.printDetection(primeroFrame,bbox)
        return bbox

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
            ok, bbox = self.tracker.update(frame[:, :, :3])
            self.printDetection(frame,bbox)
            distanceMin = self.printDetection(frame, bbox)
            self.detectData = DetectionData(distanceMin)
            self.detectRoot.receiveData(self.detectData)
            return ok

class VisionTrackerDepth_KFC(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerKCF_create()

class VisionTrackerDepth_TLD(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerTLD_create()

class VisionTrackerDepth_MIL(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerMIL_create()

class VisionTrackerDepth_Boosting(VisionTrackerDepthBase):
    def __init__(self,detectRoot):
        VisionTrackerDepthBase.__init__(self, detectRoot)
        self.tracker = cv2.TrackerBoosting_create()


