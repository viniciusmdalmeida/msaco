from AlgorithmsSensors.cam.StereoCam import *

class VisionStereoLGB(VisionStereoBase):
    name = 'lgb'
    def __init__(self, detectRoot):
        VisionStereoBase.__init__(self, detectRoot,model_name=self.name)

class VisionStereoRF(VisionStereoBase):
    name = 'rf'
    def __init__(self, detectRoot):
        VisionStereoBase.__init__(self, detectRoot,model_name=self.name)

class VisionStereoNeural(VisionStereoBase):
    name = 'neural'

    def __init__(self, detectRoot):
        VisionStereoBase.__init__(self, detectRoot, model_name=self.name)

class VisionStereoNaiveBayes(VisionStereoBase):
    name = 'naive'
    def __init__(self, detectRoot):
        VisionStereoBase.__init__(self, detectRoot, model_name=self.name)

class VisionStereoSVM(VisionStereoBase):
    name = 'svm'
    def __init__(self, detectRoot):
        VisionStereoBase.__init__(self, detectRoot, model_name=self.name)


###################################
# Tracker
###################################

class VisionStereoLGB(VisionStereoBase):
    name = 'lgb'
    def __init__(self, detectRoot):
        VisionStereoBase.__init__(self, detectRoot,model_name=self.name)

class VisionStereoRF(VisionStereoBase):
    name = 'rf'
    def __init__(self, detectRoot):
        VisionStereoBase.__init__(self, detectRoot,model_name=self.name)

class VisionStereoNeural(VisionStereoBase):
    name = 'neural'

    def __init__(self, detectRoot):
        VisionStereoBase.__init__(self, detectRoot, model_name=self.name)

class VisionStereoNaiveBayes(VisionStereoBase):
    name = 'naive'
    def __init__(self, detectRoot):
        VisionStereoBase.__init__(self, detectRoot, model_name=self.name)

class VisionStereoSVM(VisionStereoBase):
    name = 'svm'
    def __init__(self, detectRoot):
        VisionStereoBase.__init__(self, detectRoot, model_name=self.name)

########################################
# Tracker
########################################


class VisionTrackerStereo_KFC_RF(VisionStereoTracker):
    def __init__(self,detectRoot):
        VisionStereoTracker.__init__(self, detectRoot,model_name='rf')
        self.tracker = cv2.TrackerKCF_create()

class VisionTrackerStereo_KFC_Naive(VisionStereoTracker):
    def __init__(self,detectRoot):
        VisionStereoTracker.__init__(self, detectRoot,model_name='naive')
        self.tracker = cv2.TrackerKCF_create()


class VisionTrackerStereo_KFC_RF(VisionStereoTracker):
    def __init__(self, detectRoot):
        VisionStereoTracker.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerKCF_create()


class VisionTrackerStereo_KFC_Naive(VisionStereoTracker):
    def __init__(self, detectRoot):
        VisionStereoTracker.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerKCF_create()


class VisionTrackerStereo_MIL_RF(VisionStereoTracker):
    def __init__(self, detectRoot):
        VisionStereoTracker.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerMIL_create()


class VisionTrackerStereo_MIL_Naive(VisionStereoTracker):
    def __init__(self, detectRoot):
        VisionStereoTracker.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerMIL_create()


class VisionTrackerStereo_TLD_RF(VisionStereoTracker):
    def __init__(self, detectRoot):
        VisionStereoTracker.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerTLD_create()


class VisionTrackerStereo_TLD_Naive(VisionStereoTracker):
    def __init__(self, detectRoot):
        VisionStereoTracker.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerTLD_create()


class VisionTrackerStereo_Boosting_RF(VisionStereoTracker):
    def __init__(self, detectRoot):
        VisionStereoTracker.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerBoosting_create()


class VisionTrackerStereo_Boosting_Naive(VisionStereoTracker):
    def __init__(self, detectRoot):
        VisionStereoTracker.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerBoosting_create()

