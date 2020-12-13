import airsim  # pip install airsim
import cv2
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from Detect.DetectionData import *


class VisionBase(AlgorithmSensor):
    name = 'vision'

    def __init__(self, detectRoot):
        AlgorithmSensor.__init__(self, detectRoot)
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

    def calc_obj_position(self, bbox, fov_angle=120, width_image=1024):
        # calc x e y camera
        x_camera = (bbox[0] + bbox[2]) / 2
        y_camera = (bbox[1] + bbox[3]) / 2
        # get focal legth
        angle = float(fov_angle / 2.0)
        part_width = float(width_image / 2.0)
        focal_legh = (part_width / np.sin(np.deg2rad(angle))) * np.sin(np.deg2rad(30.0))  # regra seno
        # calc distance camera
        distance_camera_x = (x_camera ** 2 + focal_legh ** 2) ** 0.5  # hipotenusa
        seno_angulo_plane_x =  x_camera / (np.sin(np.deg2rad(90)) * distance_camera_x)  # regra senos
        distance_camera_y = (y_camera ** 2 + focal_legh ** 2) ** 0.5  # hipotenusa
        seno_angulo_plane_y =   y_camera / (np.sin(np.deg2rad(90)) * distance_camera_y )   # regra senos
        # calc x e y real
        distance_real = self.calc_distance(bbox)
        x_real = seno_angulo_plane_x * (distance_real / np.sin(np.deg2rad(90)))
        y_real = seno_angulo_plane_y * (distance_real / np.sin(np.deg2rad(90)))
        # Testar o z com regra de 3
        # Seria nescessario decompor a distancia em x e y
        z_real = (focal_legh * distance_real) / distance_camera_x
        relativePosition = (x_real, y_real, z_real)
        self.detectData.updateData(distance=distance_real, relativePosition=relativePosition)
        
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


class VisionCaptureAll(VisionDepthBase):
    name = "Vision Save All Image"

    def __init__(self, detectRoot):
        VisionDepthBase.__init__(self, detectRoot)

    def detect(self):
        self.getImage(True)
        self.getDepth(True)
