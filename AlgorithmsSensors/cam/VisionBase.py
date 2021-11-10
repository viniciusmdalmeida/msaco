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
                if min(x2-x1,y2-y1) >= 0:
                    p1 = (x1, y1)
                    p2 = (x2, y2)
                    if self.depth:
                        cv2.rectangle(frame, p1, p2, 0, 2, 1)
                    else:
                        cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
                    if distance:
                        cv2.putText(frame, "distancia:{}".format(distance), (100, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                else:
                    # Tracking failure
                    print(f"X:{x1-x2},Y:{y1-y2},MIN:{min(x1-x2,y1-y2)}")
                    cv2.putText(frame, "Tracking failure detected", (100, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
            cv2.imshow("Detect", frame)
            cv2.waitKey(1)

    def terminate(self):
        print("Tentando terminar ",self.name)
        self._stop_detect = True
        if self.showVideo:
            cv2.destroyAllWindows()
        print("Terminando windows")

    def get_calc_pos(self):
        file_type_calc = open('type_calc.txt', 'r')
        type = file_type_calc.read()
        file_type_calc.close()
        return type.strip()

    def calc_obj_position(self, bbox, fov_angle=120, width_image=1024, alt_image = 580):
        distance_real = self.calc_distance(bbox)
        # calc x e y camera
        y_camera = (bbox[0] + bbox[2]) / 2  # largura (y) camera
        z_camera = ((bbox[1] + bbox[3]) / 2) - alt_image   # altura (z) camera
        # get focal legth
        angle = float(fov_angle / 2.0)
        part_width = float(width_image / 2.0)
        focal_legh = (part_width / np.sin(np.deg2rad(angle))) * np.sin(np.deg2rad(30.0))  # regra seno: x camera
        x_camera = focal_legh
        #Caculando valor Aux
        aux_linha = (y_camera**2 + x_camera**2)**(1/2)
        distance_linha = (aux_linha**2 + z_camera**2)**(1/2)
        seno_Z = z_camera  / distance_linha # (z_camera * seno(90º)) / distancia_linha
        AUX = distance_real * seno_Z  # (distancia_real / seno(90º)) * seno(angle_Z)
        #Calculando Z
        Z = (distance_real**2 - AUX**2) ** (1/2) ### ca^2 = hip^2 - co^2
        #Calculando Y
        seno_Y = y_camera / AUX  #(y_camera * seno(90º)) / AUX
        Y = AUX * seno_Y # (AUX / seno(90º)) * seno(angle_Y)
        X = (AUX**2 - Y**2) ** (1/2) ### ca^2 = hip^2 - co^2
        print(f"y_camera:{y_camera}, x_camera:{x_camera}, focal_legh: {focal_legh}, aux_linha: {aux_linha}, senoZ:{seno_Z}, AUX:{AUX}, senoY:{seno_Y}, distance: {distance_real}")
        relativePosition = (X, Y, Z)
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
        #resize image
        if img1d.shape != (1024, 580):
            img1d = cv2.resize(img1d, dsize=(1024, 580), interpolation=cv2.INTER_AREA)
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
        cv2.waitKey(1)

    def calc_distance(self,bbox):
        x1, y1, x2, y2 = self.getPoints(bbox)
        if x2 < x1:
            aux = x1.copy()
            x1 = x2
            x2 = aux
        elif x2 == x1:
            return None
        if y2 < y1:
            aux = y1.copy()
            y1 = y2
            y2 = aux
        elif y2 == y1:
            return None
        y1 = max(0,y1)
        x1 = max(0,x1)
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
        self.getDepth(True)
