import airsim  # pip install airsim
import numpy as np
import cv2
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
import time
from datetime import datetime
from Control.DetectionData import *
from abc import abstractmethod

class VisionBase(AlgorithmSensor):
    name = 'vision'

    def __init__(self, detectRoot):
        AlgorithmSensor.__init__(self, detectRoot)
        self.detectData = None
        self.depth = False
        self.cont = 0
        self.showVideo = self.config['sensors']['Vision']['show_video']
        #get data
        date_now = datetime.now()
        self.date_str = f"{date_now.day}-{date_now.month}_{date_now.hour}-{date_now.minute}-{date_now.second}"

    def getPoints(self, bbox):
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        larg = int(bbox[2])
        alt = int(bbox[3])
        x2 = int(x1 + larg)
        y2 = int(y1 + alt)
        return x1, y1, x2, y2

    def getImage(self,save=False):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
        response = response[0]
        # get numpy array
        img_rgba = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        # reshape array to 4 channel image array H X W X 4
        if len(img_rgba) == 1:
            return None
        img_rgba = img_rgba.reshape(response.height, response.width, 3)
        if save:
            cv2.imwrite(f'../data/imagens/RGB/voo/frame_{self.cont}_{self.date_str}.jpg',img_rgba)
            self.cont += 1
        return img_rgba

    def printDetection(self, frame, bbox=None,distance=None):
        if self.showVideo:
            if bbox is not None and len(bbox) >= 4:
                x1,y1,x2,y2 = self.getPoints(bbox)
                # Draw Bounding box
                if min(x1,x2,y1,y2) >= 0:
                    p1 = (x1, y1)
                    p2 = (x2, y2)
                    cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
                    if distance:
                        cv2.putText(frame, "distancia:{}".format(distance), (100, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                else:
                    # Tracking failure
                    cv2.putText(frame, "Tracking failure detected", (100, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
            cv2.imshow("Detect", frame)
            cv2.waitKey(1)

    def terminate(self):
        cv2.destroyAllWindows()
        self._stop_detect = True
'''
    def terminate(self):
        AlgorithmSensor.terminate(self)
        if self.showVideo:
            print("Force destroy!")
            cv2.destroyAllWindows()
            cv2.waitKey(1)
'''
class VisionDepthBase(VisionBase):
    def __init__(self,detectRoot):
        VisionBase.__init__(self, detectRoot)
        self.cont_depth = 0

    def getDepth(self,save=False):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthPlanner, True)])
        response = response[0]
        # get numpy array
        img1d = airsim.list_to_2d_float_array(response.image_data_float, response.width, response.height)
        if save:
            cv2.imwrite(f'../data/imagens/Depth/voo/frame_{self.cont_depth}_{self.date_str}.jpg', img1d)
            self.cont_depth += 1
        if len(img1d) < 1:
            return None
        return img1d

    def normalize_image(self,image,max=np.inf,invert=True):
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
        return image

    def printDepthDetection(self, image, bbox=None, max=np.inf, invert=True):
        image = self.normalize_image(image,max,invert)
        if not (bbox is None):
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(image, p1, p2, (255, 0, 0), 2, 1)
        cv2.imshow("Depth", image)

    def calc_distance(self,bbox):
        x1, y1, x2, y2 = self.getPoints(bbox)
        if x2 < x1:
            aux = x1
            x1 = x2
            x2 = aux
        elif x2 == x1:
            return None
        if y2 < y1:
            aux = y1
            y1 = y2
            y2 = aux
        elif y2 == y1:
            return None
        depthImage = self.getDepth()
        distanceMin = depthImage[y1:y2, x1:x2].min()
        return distanceMin

class VisionCaptureImage(VisionBase):
    def __init__(self, detectRoot):
        VisionBase.__init__(self, detectRoot)

    def detect(self):
        self.getImage(True)

class VisionCaptureImageDeth(VisionDepthBase):
    def __init__(self, detectRoot):
        VisionDepthBase.__init__(self, detectRoot)

    def detect(self):
        self.getDepth(True)