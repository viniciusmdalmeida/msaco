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

