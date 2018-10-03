import airsim  # pip install airsim
import numpy as np
from Desvio.Desvio import *
from Controle.DetectionData import *
import cv2
from threading import Thread
import time

class Visao(Thread):
    name = 'vision'

    def __init__(self,semaforo):
        Thread.__init__(self)
        self.cliente = airsim.MultirotorClient()
        self.semaforo = semaforo
        # self.desvioThread = desvioThread
        self.detectData = None
        print("Iniciando Visão")

    def getStatus(self):
        return self.detectData

    def showDepth(self,image,max=np.inf,invert=True,bbox=None):
        def verifmax(x):
            if x > max:
                return max
            return x
        vector = np.vectorize(verifmax)
        image = vector(image)
        # Normalizando lista
        image = image / image.max()
        if invert:
            image = 255 - (image * 255)
        else:
            image = image * 255
        image = image.astype(np.uint8)
        if not (bbox is None):
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(image, p1, p2, (255, 0, 0), 2, 1)
        cv2.imshow("Depth",image)

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

    #Tracker sozinho
    def run(self):
        while self.semaforo.value:
            pass
        print("Iniciar Video")

        #self.tracker = cv2.TrackerKCF_create()
        self.tracker = cv2.TrackerBoosting_create()
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
        # print(bbox)
        # #Contagem para atualizar
        # if self.cont % 10 == 0:
        #     bbox = self.detectObject(frame)
        #     frame2 = self.getImage()
        #     ok, bbox = self.tracker.update(frame2,bbox)
        # calculando Frames por segundo
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
            depthImage = self.getDepth()
            # print("x:{} x2:{},y:{} y2:{},sizeD:{},sizeF:{}"
            #       .format(x1,x2,y1,y2,depthImage.shape,frame.shape))
            distanceMin = depthImage[y1:y2,x1:x2].min()

            cv2.rectangle(frame, p1, p2, (255, 0, 0), 2,1)
            cv2.putText(frame, "distancia:{}".format(distanceMin), (100, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        else:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
            distanceMin = np.inf

        # Display FPS on frame
        cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);
        # Display resultado
        cv2.imshow("Tracking", frame)


        #Calculando resultado
        self.detectData = DetectionData(distanceMin)
        return self.detectData
        # self.desvioThread.detectionData = self.detectData
            # Desvio(self.controle).start()


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


    #Optical flow
    def runOF(self):
        # params for ShiTomasi corner detection
        feature_params = dict(maxCorners=100,
                              qualityLevel=0.3,
                              minDistance=7,
                              blockSize=7)
        # Create some random colors
        color = np.random.randint(0, 255, (100, 3))
        # Parameters for lucas kanade optical flow
        lk_params = dict(winSize=(15, 15),
                         maxLevel=2,
                         criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        # Take first frame and find corners in it
        old_frame = self.getImage()
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
        # Create a mask image for drawing purposes
        mask = np.zeros_like(old_frame)
        while (1):
            frame = self.getImage()
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # calculate optical flow
            p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
            # Select good points
            good_new = p1[st == 1]
            good_old = p0[st == 1]
            # draw the tracks
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = new.ravel()
                c, d = old.ravel()
                mask = cv2.line(mask, (a, b), (c, d), color[i].tolist(), 2)
                frame = cv2.circle(frame, (a, b), 5, color[i].tolist(), -1)
            img = cv2.add(frame, mask)
            cv2.imshow('frame', img)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
            # Now update the previous frame and previous points
            old_gray = frame_gray.copy()
            p0 = good_new.reshape(-1, 1, 2)
        cv2.destroyAllWindows()