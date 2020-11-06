import airsim  # pip install airsim
import numpy as np
from Control.DetectionData import *
import cv2
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from abc import abstractmethod



class VisionBase(AlgorithmSensor):
    name = 'vision'

    def __init__(self, detectRoot, showVideo=None):
        AlgorithmSensor.__init__(self, detectRoot)
        self.detectData = None
        self.depth = False
        if showVideo is None:
            self.showVideo = self.config['sensors']['Vision']['show_video']
        else:
            self.showVideo = showVideo

    @abstractmethod
    def run(self):
        pass

    def getPoints(self, bbox):
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        larg = int(bbox[2])
        alt = int(bbox[3])
        x2 = int(x1 + larg)
        y2 = int(y1 + alt)
        return x1, y1, x2, y2

    def getImage(self):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
        response = response[0]
        # get numpy array
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        # reshape array to 4 channel image array H X W X 4
        if len(img1d) == 1:
            return None
        img_rgba = img1d.reshape(response.height, response.width, 3)
        return img_rgba

    def printDetection(self, frame, bbox=None):
        # Start timer
        if self.showVideo:
            if bbox is not None and len(bbox) >= 4:
                x1,y1,x2,y2 = self.getPoints(bbox)
                # Draw Bounding box
                p1 = (x1, y1)
                p2 = (x2, y2)
                if min(x1,x2,y1,y2) >= 0:
                    cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
                else:
                    # Tracking failure
                    cv2.putText(frame, "Tracking failure detected", (100, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
            cv2.imshow("Detect", frame)
            cv2.waitKey(1)

class VisionDepthBase(VisionBase):

    @abstractmethod
    def run(self):
        pass

    def getDepth(self):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthPlanner, True)])
        response = response[0]
        # get numpy array
        img1d = airsim.list_to_2d_float_array(response.image_data_float, response.width, response.height)
        return img1d

    def showDepth(self, image, max=np.inf, invert=True, bbox=None):
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
        cv2.imshow("Depth", image)

    def calc_distance(self,x1,x2,y1,y2):
        depthImage = self.getDepth()
        distanceMin = depthImage[y1:y2, x1:x2].min()
        return distanceMin

    def printDetection(self, frame, bbox=None):
        # Start timer
        if self.showVideo:
            if bbox is not None and len(bbox) >= 4:
                x1,x2,y1,y2 = self.getPoints(bbox)
                # Draw Bounding box
                p1 = (x1, y1)
                p2 = (x2, y2)
                if p1 >= 0 and p2 >= 0:
                    cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
                    distance = self.calc_distance(x1,x2,y1,y2)
                    cv2.putText(frame, "distancia:{}".format(distance), (100, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                else:
                    # Tracking failure
                    cv2.putText(frame, "Tracking failure detected", (100, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
            cv2.imshow("Detect", frame)
            cv2.waitKey(1)
