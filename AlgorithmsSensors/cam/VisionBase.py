import airsim  # pip install airsim
import cv2
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from Detect.DetectionData import *
import math
from scipy.spatial.transform import Rotation

class VisionBase(AlgorithmSensor):
    name = 'vision'

    def __init__(self, detectRoot):
        AlgorithmSensor.__init__(self, detectRoot)
        self.depth = False
        self.cont = 0
        self.showVideo = self.config['sensors']['Vision']['show_video']
        self.save_vision_detect = self.config['sensors']['Vision']['save_vision_detect']
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
            cv2.imwrite(f'../data/imagens/RGB/voo/frame_{self.cont}_{datetime.now().timestamp()}.jpg',img_rgba)
            self.cont += 1
        return img_rgba

    def printDetection(self, frame, bbox=None,distance=None, timestamp=None):
        if timestamp == None:
            timestamp = datetime.now().timestamp()
        if self.showVideo or self.save_vision_detect:
            if bbox is not None and len(bbox) >= 4:
                x1,y1,x2,y2 = self.getPoints(bbox)
                # Draw Bounding box
                if min(x2-x1,y2-y1) >= 0:
                    p1 = (x1, y1)
                    p2 = (x2, y2)
                    cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
                    h,w,l = frame.shape
                    cv2.putText(frame, f"p1:{p1}, p2:{p2}, w:{w}, h:{h}", (100, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
                    cv2.putText(frame, f"bbox:{bbox}, timestamp:{timestamp}", (200, 160),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
                    if distance:
                        cv2.putText(frame, "distancia:{}".format(distance), (100, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                else:
                    # Tracking failure
                    print(f"X:{x1-x2},Y:{y1-y2},MIN:{min(x1-x2,y1-y2)}")
                    cv2.putText(frame, "Tracking failure detected", (100, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
            if self.save_vision_detect:
                cv2.imwrite(f'../data/imagens/detect/voo/frame_{self.cont}_{timestamp}.jpg',frame)

            if self.showVideo:
                cv2.imshow("Detect", frame)
                cv2.waitKey(1)

    def terminate(self):
        self._stop_detect = True
        if self.showVideo:
            cv2.destroyAllWindows()
        print(f"Terminando algoritmo:{self.name}")

    def get_calc_pos(self):
        file_type_calc = open('type_calc.txt', 'r')
        type = file_type_calc.read()
        file_type_calc.close()
        return type.strip()

    def calc_extrinsics_matrix(self):
        quaternion_angles = self.client.simGetGroundTruthKinematics().orientation #get quaternoin anglers
        drone_location = self.client.simGetGroundTruthKinematics().position #get position of drone
        #print("drone_location:",drone_location)
        drone_location.z_val = drone_location.z_val# Corigindo o Z
        #Convert rotation to roll pitch yaw
        #Link: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.as_euler.html
        rotation_obj = Rotation.from_quat([quaternion_angles.x_val,quaternion_angles.y_val,quaternion_angles.z_val,
                                 quaternion_angles.w_val])
        (roll,pitch,yaw) = rotation_obj.as_euler('xyz', degrees=True)
        # calcule rotation matrix
        rotation_matrix = rotation_obj.as_matrix()
        translation_matrix = drone_location.to_numpy_array()

        return rotation_matrix,translation_matrix

    def calc_obj_position(self, bbox, fov_angle=120, width_image=1024, alt_image = 580, focal_lengh_x=179.53, focal_lengh_y=179.17):
        #Link para descobrir focal length https://github.com/microsoft/AirSim/issues/2396
        #Formula para focal length (Horizontal FoV = 2 * arctan( width / 2f ) )
        y_camera = (bbox[0] + bbox[2]) / 2  # largura (y) camera
        z_camera = ((bbox[1] + bbox[3]) / 2) - alt_image   # altura (z) camera
        position_cam_matrix = np.array([y_camera, z_camera, 1, 1])

        px = width_image/2
        py = alt_image/2
        #https://www.cs.cmu.edu/~16385/s17/Slides/11.1_Camera_matrix.pdf
        rotation_matrix,translation_matrix = self.calc_extrinsics_matrix()
        extrinsics_matrix = np.c_[rotation_matrix, translation_matrix]
        intrinsics_matrix = np.array([[focal_lengh_x, 0, px],
                                      [0, focal_lengh_y, py],
                                      [0,             0,  1]])

        #link: https://www.fdxlabs.com/calculate-x-y-z-real-world-coordinates-from-a-single-camera-using-opencv/
        XYZ = np.dot(extrinsics_matrix, position_cam_matrix)
        relativePosition = tuple(XYZ)

        #Escrevendo parametros
        file_path = f'../data/camera_data/camera_{datetime.now().strftime("%Y_%m_%d")}.csv'
        with open(file_path,'a') as file:
            file.write(f"{datetime.now().timestamp()},{focal_lengh_y},{focal_lengh_x},{px},{py},{rotation_matrix.tolist()},{translation_matrix.tolist()}\n")

        #Real distance
        distance_real = self.calc_distance(bbox)
        #print(f"calcule position: {relativePosition}")
        self.detectData.updateData(distance=distance_real, relativePosition=relativePosition, bbox=bbox)

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
        shape_depth = depthImage.shape
        y_proporcion = shape_depth[0] / 1080
        x_proporcion = shape_depth[1] / 1920
        distanceMin = depthImage[int(y1*y_proporcion):int(y2*y_proporcion),
                                 int(x1*x_proporcion):int(x2*x_proporcion)].min()
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
