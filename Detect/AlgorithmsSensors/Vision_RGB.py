import airsim  # pip install airsim
import numpy as np
from Avoid.Avoid import *
from Control.DetectionData import *
import cv2
from Detect.Sensor import Sensor
import time

class Vision_RGB(Sensor):
    name = 'vision'

    def __init__(self,semaphore,avoidThread):
        Sensor.__init__(self,semaphore)
        self.avoidThread = avoidThread
        self.detectData = None

    def getStatus(self):
        return self.detectData

    def getImage(self):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
        response = response[0]
        # get numpy array
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        # reshape array to 4 channel image array H X W X 4
        img_rgba = img1d.reshape(response.height, response.width, 4)
        return img_rgba

    #Tracker sozinho
    def run(self):
        while self.semaphore.value:
            pass
        print("Iniciar Video")

        # self.tracker = cv2.TrackerMIL_create()
        self.tracker = cv2.TrackerKCF_create()
        # self.tracker = cv2.TrackerTLD_create()
        primeroFrame = self.getImage()
        while len(np.unique(primeroFrame)) < 20:
            primeroFrame = self.getImage()
        #Verificando se algum objeto saliente
        bbox,size = self.detectObject(primeroFrame)
        self.tracker.init(primeroFrame, bbox)
        self.cont = 0
        print("Tracker Iniciado")
        while True:
            self.updateTracker()
            # Exit se ESC for pressionado
            k = cv2.waitKey(1) & 0xff
            if k == 27: break
            self.cont += 1

    def detectObject(self,frameBase):
        bbox = None
        while bbox is None:
            bbox = self.backgroundDetect(frameBase)
            cv2.imshow("Tracking", frameBase)
            cv2.waitKey(1)
        size = bbox[2] * bbox[3]
        return bbox,size

    def updateTracker(self):
        frame = self.getImage()
        # Start timer
        timer = cv2.getTickCount()
        # Update tracker
        ok, bbox = self.tracker.update(frame[:, :, :3])

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        larg = int(bbox[2])
        alt = int(bbox[3])
        if ok and (x1>=0 and y1>=0 and int(larg) >=1 and int(alt)>=1):
            # Desenhando Bounding box
            x2 = int(x1 + larg)
            y2 = int(y1 + alt)
            p1 = (x1, y1)
            p2 = (x2, y2)
            cv2.rectangle(frame, p1, p2, (255, 0, 0), 2,1)
        else:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)

        # Display FPS on frame
        cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);
        # Display resultado
        cv2.imshow("Tracking", frame)
        self.send_result()

    def backgroundDetect(self,frameInicial):
        primeroFrame = frameInicial.copy()
        primeroFrame = cv2.cvtColor(primeroFrame, cv2.COLOR_BGR2GRAY)
        primeroFrame = cv2.GaussianBlur(primeroFrame, (21, 21), 0)
        # compute the absolute difference between the current frame and
        # first frame
        frame = self.getImage()
        frame = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame , (21, 21), 0)
        frameDelta = cv2.absdiff(primeroFrame, frame)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[1]
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 500:
                return None
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            # retangulo = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # text = "Occupied"
            return (x, y, w, h)
        return None

    def send_result(self):
        #Calculando resultado
        self.detectData = DetectionData()
        self.avoidThread.detectionData = self.detectData
            # Desvio(self.controle).start()