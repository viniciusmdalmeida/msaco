from AlgorithmsSensors.cam.VisionBase import *

class VisionRGBMOG(VisionBase):
    name = 'vision MOG algorithm'
    latsBbox = None
    cont = 0

    def __init__(self,detectRoot):
        VisionBase.__init__(self, detectRoot)

    def run(self):
        print("Iniciar Video")
        # self.camShifTracker()
        # self.tracker = cv2.TrackerKCF_create()
        self.tracker = cv2.TrackerBoosting_create()

        #Esperando dados validos
        primeroFrame = self.getImage()
        while len(np.unique(primeroFrame)) < 20:
            #Verifica se o frame não é vazio
            primeroFrame = self.getImage()

        self.backgroundDetectMog2()

    def backgroundDetectMog2(self):
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

        fgmask = fgbg.apply(frame)

