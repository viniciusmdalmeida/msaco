from AlgorithmsSensors.cam.VisionTracker import *

class VisionDetectKeras(VisionDetectOnly):
    name = 'keras'
    def __init__(self, detectRoot):
        VisionDetectOnly.__init__(self, detectRoot,model='lgb')
        self.detectObject = DetectKeras(self.config)

class VisionDetectSVM(VisionDetectOnly):
    name = 'svm'
    def __init__(self, detectRoot):
        VisionDetectOnly.__init__(self, detectRoot,model=self.name)

class VisionDetectLGB(VisionDetectOnly):
    name = 'lgb'
    def __init__(self, detectRoot):
        VisionDetectOnly.__init__(self, detectRoot,model=self.name)

class VisionDetectRF(VisionDetectOnly):
    name = 'rf'
    def __init__(self, detectRoot):
        VisionDetectOnly.__init__(self, detectRoot, model=self.name)

class VisionDetectNeural(VisionDetectOnly):
    name = 'neural'
    def __init__(self, detectRoot):
        VisionDetectOnly.__init__(self, detectRoot, model=self.name)

class VisionDetectNaiveBayes(VisionDetectOnly):
    name = 'naive'
    def __init__(self, detectRoot):
        VisionDetectOnly.__init__(self, detectRoot, model=self.name)

#################################
#   Depth Detect
#################################
class VisionTracker_Depth(VisionDetectOnly):
    def __init__(self, detectRoot):
        VisionDetectOnly.__init__(self, detectRoot, model=self.name, depth=True)

    def getImage(self, save=False):
        img = self.getDepth(save)
        img = img / img.max()
        img = img * 255
        return img

class VisionDetectSVM_Depth(VisionTracker_Depth):
    name = 'svm'

class VisionDetectLGB_Depth(VisionTracker_Depth):
    name = 'lgb'

class VisionDetectRF_Depth(VisionTracker_Depth):
    name = 'rf'

class VisionDetectNaive_Depth(VisionTracker_Depth):
    name = 'naive'

class VisionDetectNeural_Depth(VisionTracker_Depth):
    name = 'neural'


################################
#Trackers
################################
class VisionTracker_KFC_RF(VisionTrackerBase):
    def __init__(self,detectRoot):
        VisionTrackerBase.__init__(self, detectRoot,model_name='rf')
        self.tracker = cv2.TrackerKCF_create()

class VisionTracker_KFC_LGB(VisionTrackerBase):
    name = "KFC LGB"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='lgb')
        self.tracker = cv2.TrackerKCF_create()

class VisionTracker_KFC_SVM(VisionTrackerBase):
    name = "KFC SVM"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='svm')
        self.tracker = cv2.TrackerKCF_create()

class VisionTracker_KFC_Naive(VisionTrackerBase):
    name = "KFC Naive"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerKCF_create()

class VisionTracker_KFC_RN(VisionTrackerBase):
    name = "KFC RN"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='neural')
        self.tracker = cv2.TrackerKCF_create()


class VisionTracker_MIL_RF(VisionTrackerBase):
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerMIL_create()


class VisionTracker_MIL_LGB(VisionTrackerBase):
    name = "KFC LGB"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='lgb')
        self.tracker = cv2.TrackerMIL_create()


class VisionTracker_MIL_SVM(VisionTrackerBase):
    name = "KFC SVM"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='svm')
        self.tracker = cv2.TrackerMIL_create()


class VisionTracker_MIL_Naive(VisionTrackerBase):
    name = "KFC Naive"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerMIL_create()


class VisionTracker_MIL_RN(VisionTrackerBase):
    name = "KFC RN"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='neural')
        self.tracker = cv2.TrackerMIL_create()


class VisionTracker_TLD_RF(VisionTrackerBase):
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerTLD_create()


class VisionTracker_TLD_LGB(VisionTrackerBase):
    name = "KFC LGB"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='lgb')
        self.tracker = cv2.TrackerTLD_create()


class VisionTracker_TLD_SVM(VisionTrackerBase):
    name = "KFC SVM"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='svm')
        self.tracker = cv2.TrackerTLD_create()


class VisionTracker_TLD_Naive(VisionTrackerBase):
    name = "KFC Naive"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerTLD_create()


class VisionTracker_TLD_RN(VisionTrackerBase):
    name = "KFC RN"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='neural')
        self.tracker = cv2.TrackerTLD_create()

class VisionTracker_Boosting_RF(VisionTrackerBase):
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerBoosting_create()


class VisionTracker_Boosting_LGB(VisionTrackerBase):
    name = "KFC LGB"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='lgb')
        self.tracker = cv2.TrackerBoosting_create()


class VisionTracker_Boosting_SVM(VisionTrackerBase):
    name = "KFC SVM"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='svm')
        self.tracker = cv2.TrackerBoosting_create()


class VisionTracker_Boosting_Naive(VisionTrackerBase):
    name = "KFC Naive"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerBoosting_create()


class VisionTracker_Boosting_RN(VisionTrackerBase):
    name = "KFC RN"
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='neural')
        self.tracker = cv2.TrackerBoosting_create()

#################################
#   Depth Tracker
#################################
class VisionTracker_KFC_RF_Depth(VisionTrackerBase):
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerKCF_create()


class VisionTracker_KFC_LGB_Depth(VisionTrackerBase):
    name = "KFC LGB"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='lgb')
        self.tracker = cv2.TrackerKCF_create()


class VisionTracker_KFC_SVM_Depth(VisionTrackerBase):
    name = "KFC SVM"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='svm')
        self.tracker = cv2.TrackerKCF_create()


class VisionTracker_KFC_Naive_Depth(VisionTrackerBase):
    name = "KFC Naive"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerKCF_create()


class VisionTracker_KFC_RN_Depth(VisionTrackerBase):
    name = "KFC RN"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='neural')
        self.tracker = cv2.TrackerKCF_create()


class VisionTracker_MIL_RF_Depth(VisionTrackerBase):
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerMIL_create()


class VisionTracker_MIL_LGB_Depth(VisionTrackerBase):
    name = "KFC LGB"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='lgb')
        self.tracker = cv2.TrackerMIL_create()


class VisionTracker_MIL_SVM_Depth(VisionTrackerBase):
    name = "KFC SVM"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='svm')
        self.tracker = cv2.TrackerMIL_create()


class VisionTracker_MIL_Naive_Depth(VisionTrackerBase):
    name = "KFC Naive"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerMIL_create()


class VisionTracker_MIL_RN_Depth(VisionTrackerBase):
    name = "KFC RN"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='neural')
        self.tracker = cv2.TrackerMIL_create()


class VisionTracker_TLD_RF_Depth(VisionTrackerBase):
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerTLD_create()


class VisionTracker_TLD_LGB_Depth(VisionTrackerBase):
    name = "KFC LGB"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='lgb')
        self.tracker = cv2.TrackerTLD_create()


class VisionTracker_TLD_SVM_Depth(VisionTrackerBase):
    name = "KFC SVM"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='svm')
        self.tracker = cv2.TrackerTLD_create()


class VisionTracker_TLD_Naive_Depth(VisionTrackerBase):
    name = "KFC Naive"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerTLD_create()


class VisionTracker_TLD_RN_Depth(VisionTrackerBase):
    name = "KFC RN"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='neural')
        self.tracker = cv2.TrackerTLD_create()


class VisionTracker_Boosting_RF_Depth(VisionTrackerBase):
    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='rf')
        self.tracker = cv2.TrackerBoosting_create()


class VisionTracker_Boosting_LGB_Depth(VisionTrackerBase):
    name = "KFC LGB"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='lgb')
        self.tracker = cv2.TrackerBoosting_create()


class VisionTracker_Boosting_SVM_Depth(VisionTrackerBase):
    name = "KFC SVM"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='svm')
        self.tracker = cv2.TrackerBoosting_create()


class VisionTracker_Boosting_Naive_Depth(VisionTrackerBase):
    name = "KFC Naive"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='naive')
        self.tracker = cv2.TrackerBoosting_create()


class VisionTracker_Boosting_RN_Depth(VisionTrackerBase):
    name = "KFC RN"

    def __init__(self, detectRoot):
        VisionTrackerBase.__init__(self, detectRoot, model_name='neural')
        self.tracker = cv2.TrackerBoosting_create()