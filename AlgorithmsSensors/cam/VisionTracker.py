from AlgorithmsSensors.cam.VisionBase import *
from AlgorithmsSensors.cam.DetectObjClasses import *
import numpy as np

#class VisionRGBDefault(VisionBase):
class VisionTrackerBase(VisionDepthBase):
    name = "Vision Tracker Base"

    def __init__(self,detectRoot,depth=False,model_name='rf',prep_data_name='pca'):
        VisionBase.__init__(self, detectRoot)
        self.tracker = None
        model_sufix = self.config['algorithm']['vision']['model_sufix']
        self.mode_name = f'{model_name}_{model_sufix}'
        prep_data_name = f'{prep_data_name}_{model_sufix}'
        self.detectObject = DetectMLBase(self.config,nameModel=self.mode_name,namePrepDataModel=prep_data_name)
        self.cont_status = 0
        self.depth = depth
        if self.depth:
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
        print(f"Start or Restart Tracker {self.name}")
        start_frame = self.getImage()
        while len(np.unique(start_frame)) < 20:
            start_frame = self.getImage()
        #Primeira detecção
        bbox,frame = self.firstDetect(start_frame)
        if (not frame is None) and (len(frame.shape) < 3):
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        if (not bbox is  None) and (not frame is  None):
            self.calc_obj_position(bbox)
            print(f"Start Tracker {self.name}, with bbox: {bbox}")
            self.tracker.init(frame, bbox)
        else:
            print("Target not detect!")

    def firstDetect(self,start_frame):
        bbox = None
        frame = None
        print(f"Get First Detect {self.name}")
        while bbox is None and self._stop_detect == False:
            frame = self.getImage()
            bbox = self.detectObject.detect(frame,start_frame)
            self.printDetection(frame,bbox)
        print(f"First Detect ok, bbox:{bbox}")
        return bbox,frame

    def detect(self):
        status = self.updateTracker()
        if not self.check_status(status):
            #restart tracker
            self.start_tracker()

    def updateTracker(self):
        frame = self.getImage()
        # Update tracker
        if frame is not None:
            if len(frame.shape) > 2:
                ok, bbox = self.tracker.update(frame[:, :, :3])
            else:
                frame = cv2.cvtColor(frame,cv2.COLOR_GRAY2RGB)
                ok, bbox = self.tracker.update(frame)
            self.printDetection(frame,bbox)
            self.calc_obj_position(bbox)
            return ok
        else:
            return False

class VisionDetectOnly(VisionTrackerBase):
    name = "Vision Detect Only"

    def __init__(self,detectRoot,model='lgb',depth=False):
        VisionTrackerBase.__init__(self, detectRoot,model_name=model)
        self.depth = depth

    def start_tracker(self):
        # Pegando o primeiro frame
        self.start_frame = self.getImage()
        while len(np.unique(self.start_frame)) < 20:
            self.start_frame = self.getImage()

    def detect(self):
        frame = self.getImage()
        bbox = self.detectObject.detect(frame)
        if bbox :
            self.printDetection(frame, bbox)
            self.calc_obj_position(bbox)
            status = True
        else:
            status = False
        if not self.check_status(status):
            self.start_tracker()