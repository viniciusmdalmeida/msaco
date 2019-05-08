import airsim  # pip install airsim
import numpy as np
from Avoid.Avoid import *
from Control.DetectionData import *
import cv2
from Detect.Sensor import *

class VisionMOG(Sensor):
    name = 'vision'
    latsBbox = None
    cont = 0

    def __init__(self,semaforo,desvioThread):
        Sensor.__init__(self,semaforo)
        self.desvioThread = desvioThread
        print("Iniciando Visão")

    def run(self):
        while self.semaforo.value:
            pass
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

        # while True:
        #     print("Tracker Iniciado")
        #     self.updateTracker()
        #     # self.backgroundTracker()
        #     # Exit se ESC for pressionado
        #     k = cv2.waitKey(1) & 0xff
        #     if k == 27: break
        #     self.cont += 1
        #

    def getImage(self):
        response = self.cliente.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
        response = response[0]
        # get numpy array
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        # reshape array to 4 channel image array H X W X 4
        img_rgba = img1d.reshape(response.height, response.width, 4)
        return img_rgba

    def getDepth(self):
        response = self.cliente.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthPlanner, True)])
        response = response[0]
        # get numpy array
        img1d = airsim.list_to_2d_float_array(response.image_data_float, response.width, response.height)
        return img1d

    def detectObject(self,frameBase):
        # print("detectObject")
        bbox = None
        while bbox is None:
            bbox = self.backgroundDetect(frameBase)
            cv2.imshow("Tracking", frameBase)
            cv2.waitKey(1)
        size = bbox[2] * bbox[3]
        #Imprime detecção!
        cv2.rectangle(frameBase, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (255, 0, 0), 2, 1)
        cv2.imshow("Detect", frameBase)
        cv2.waitKey(1)
        return bbox,size

    def getPoints(self,bbox):
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        larg = int(bbox[2])
        alt = int(bbox[3])
        x2 = int(x1 + larg)
        y2 = int(y1 + alt)
        return x1,y1,x2,y2


    def backgroundDetectMog2(self):
        fgbg = cv2.createBackgroundSubtractorMOG2()
        while True:
            frame = self.getImage()
            fgmask = fgbg.apply(frame)

            thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[1]
            max = cnts[0]
            for c in cnts:
                if cv2.contourArea(c) >cv2.contourArea(max) :
                    max = c
            (x, y, w, h) = cv2.boundingRect(max)


            depthImage = self.getDepth()
            print(x,y,w,h)
            print(depthImage.shape)
            distanceMin = depthImage[y:y+w, x:x+h].min()
            # Salvando Imagem
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2, 1)
            cv2.putText(frame, "distancia:{}".format(distanceMin), (100, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2, 1)

            cv2.imshow('frame', frame)
            self.detectData = DetectionData(distanceMin)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
            self.detectData = DetectionData(distanceMin)
            self.desvioThread.detectionData = self.detectData

        fgmask = fgbg.apply(frame)

