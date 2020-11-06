from AlgorithmsSensors.cam.VisionBase import *


#class VisionRGBDefault(VisionBase):
class VisionTrackerBase(VisionBase):
    name = "Vision RGB Default Algorithm"

    def __init__(self,detectRoot):
        VisionBase.__init__(self, detectRoot)
        self.tracker = None
        #self.detectObjectFunction = None
        self.firstDetectFunction = self.mogObjectDetect
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
        while True:
            #Verificando se algum objeto saliente
            bbox = self.firstDetectFunction()
            frame = self.getImage()
            self.tracker.init(frame, bbox)
            print("Tracker Iniciado")
            tracker_status = True
            while self.check_status(tracker_status):
                tracker_status = self.updateTracker()

    def mogObjectDetect(self):
        #Pegando o primeiro frame
        primeroFrame = self.getImage()
        while len(np.unique(primeroFrame)) < 20:
            primeroFrame = self.getImage()
        bbox = None
        while bbox is None:
            bbox = self.MOGbackgroundDetect(primeroFrame)
            self.printDetection(primeroFrame,bbox)
        return bbox

    def MOGbackgroundDetect(self, frameInicial):
        #Aplicando operações basicas no primeiro frame
        primeroFrame = frameInicial.copy()
        primeroFrame = cv2.cvtColor(primeroFrame, cv2.COLOR_BGR2GRAY)
        primeroFrame = cv2.GaussianBlur(primeroFrame, (21, 21), 0)
        #Aplicando operações basicas no frame atual
        frame = self.getImage()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (21, 21), 0)
        #calculanod diferença entre os frames
        frameDelta = cv2.absdiff(primeroFrame, frame)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        #Dilatando o thresholded image para preencher os buracos e encontrar os contornos
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        #procurando maior boundbox encontrado
        if type(cnts) is None or len(cnts) <= 0:
            return
        max_cnts = cnts[0]
        for c in cnts:
            if cv2.contourArea(c) > cv2.contourArea(max_cnts):
                max_cnts = c
        #Verificando se o maior contorno é maior que minimo da configuração
        if cv2.contourArea(max_cnts) < self.config['sensors']['Vision']['min_area']:
            return None
        else:
            print("Area:",cv2.contourArea(max_cnts))
        #Buncando tamanho do boundbox e retornando
        (x, y, w, h) = cv2.boundingRect(max_cnts)
        return (x, y, w, h)

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
        ok, bbox = self.tracker.update(frame[:, :, :3])
        self.printDetection(frame,bbox)
        return ok

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
