import cv2
import airsim

from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from Detect.DetectionData import *
from AlgorithmsSensors.cam.DetectObjClasses import *
from AlgorithmsSensors.cam.VisionBase import VisionBase


class VisionStereoBase(VisionBase):
    name = 'vision'

    def __init__(self, detectRoot, prep_data_name = 'pca', model_name='rf', template_matching_method='cv2.TM_CCOEFF'):
        AlgorithmSensor.__init__(self, detectRoot)
        self.template_matching_method = template_matching_method
        self.showVideo = self.config['sensors']['Vision']['show_video']
        self.save_vision_detect = self.config['sensors']['Vision']['save_vision_detect']
        self.cont = 0
        #get data
        date_now = datetime.now()
        self.date_str = f"{date_now.day}-{date_now.month}_{date_now.hour}-{date_now.minute}-{date_now.second}"
        #get detect class
        model_sufix = self.config['algorithm']['vision']['model_sufix']
        model_name = f'{model_name}_{model_sufix}'
        prep_data_name = f'{prep_data_name}_{model_sufix}'
        self.detectObject = DetectMLBase(self.config, nameModel=model_name, namePrepDataModel=prep_data_name)


    def get_images(self):
        response = self.client.simGetImages([airsim.ImageRequest("front_left", airsim.ImageType.Scene, False, False),
                                             airsim.ImageRequest("front_right", airsim.ImageType.Scene, False, False)])
        # get numpy array
        img_rgba_left = np.fromstring(response[0].image_data_uint8, dtype=np.uint8)
        img_rgba_right = np.fromstring(response[1].image_data_uint8, dtype=np.uint8)

        # reshape array to 4 channel image array H X W X 4
        if len(img_rgba_left) == 1 or len(img_rgba_right) == 1:
            return None
        img_rgba_left = img_rgba_left.reshape(response[0].height, response[0].width, 3)
        img_rgba_right = img_rgba_right.reshape(response[1].height, response[1].width, 3)
        return img_rgba_left, img_rgba_right

    def template_matching(self, img_left, img_rigth, bbox):
        img = img_rigth.copy()
        # Cortando a imagem para otimizar o algoritmo
        img = img[int(bbox[1] - bbox[3] / 2):int(bbox[1] + (bbox[3] * 2)), :]
        method = eval(self.template_matching_method)
        template = img_left[int(bbox[1]):int(bbox[1] + bbox[3]), int(bbox[0]):int(bbox[0] + bbox[2])]

        # Apply template Matching
        res = cv2.matchTemplate(img, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = list(min_loc)
        else:
            top_left = list(max_loc)
        # Adicionando o valor cortado no bbox
        top_left[1] = top_left[1] + int(bbox[1]) - int(bbox[3] / 2)
        bbox_matching = [top_left[0], top_left[1], bbox[2], bbox[3]]
        return bbox_matching

    def calc_relative_pos(self,  img_left, img_rigth, bbox,
                          focal_lengh_x=295, focal_lengh_y=295, px=511, py=290.1, b=25):
        bbox_matching = self.template_matching(img_left, img_rigth, bbox)

        x1, y1 = bbox[0] + (bbox[2] / 2), bbox[1] + (bbox[3] / 2)
        x2, y2 = bbox_matching[0] + (bbox_matching[2]/2), bbox_matching[1] + (bbox_matching[3]/2)

        d = x2 - x1
        if d == 0:
            d = 1

        z = (b * focal_lengh_x) / d
        x = (b * (px - x1)) / d
        y = (b * focal_lengh_x * (y1 - py)) / (focal_lengh_y * d)

        return z/100, x/100, y/100


    def calc_distance(self, relative_pos):
        distancia = (relative_pos[0] ** 2 + relative_pos[1] ** 2 +  relative_pos[2]**2)**0.5
        return distancia


    def get_start_frame(self):
        # Pegando o primeiro frame
        self.start_frame = self.getImage()
        while len(np.unique(self.start_frame)) < 20:
            self.start_frame = self.getImage()


    def detect(self, focal_lengh_x=295, focal_lengh_y=295, px=511, py=290.1, b=25):
        # Calculando bbox
        self.get_start_frame()
        img_left, img_rigth  = self.get_images()
        timestamp_detect = datetime.now().timestamp()
        print("detect get_timestamp",datetime.now().isoformat())
        bbox = self.detectObject.detect(img_left, self.start_frame)
        if not bbox:
            print("Objeto não encontrado! timestamp:", datetime.now().isoformat())
            return
        if self.save_vision_detect:
            print("detect após escontrar imagem, timestamp:", datetime.now().isoformat())
            save_path = self.config['sensors']['Vision']['save_path']
            image_name_base = f'{save_path}/frame_{self.cont}_{timestamp_detect}'
            cv2.imwrite(f'{image_name_base}_left.jpg', img_left)
            cv2.imwrite(f'{image_name_base}_right.jpg', img_rigth)
            print("detect após imprimir imagens", datetime.now().isoformat())
            self.cont += 1
        print(f"bbox:{bbox}, timestamp:{timestamp_detect}")
        self.printDetection(img_left, bbox, timestamp=timestamp_detect)
        # Calculando posição relativa
        x, y, z = self.calc_relative_pos(img_left, img_rigth, bbox,
                                    focal_lengh_x=focal_lengh_x, focal_lengh_y=focal_lengh_y, px=px, py=py, b=b)
        relative_pos = np.array([x, y, z])

        # Aplicando translaçãmote to patho e rotação
        rotation_matrix,translation_matrix = self.calc_extrinsics_matrix()
        extrinsic_matrix = np.c_[rotation_matrix, translation_matrix]
        real_pos = np.dot(extrinsic_matrix, np.array([x, y, z, 1]))

        # Convertendo de cm para metros
        real_pos = [x * 100 for x in real_pos]

        distance = self.calc_distance(relative_pos)

        print(f"bbox final:{bbox}, timestamp:{int(timestamp_detect)}, distance: {distance}")
        self.detectData.updateData(distance=distance, otherPosition=np.array(real_pos),relativePosition=relative_pos,
                                   bbox=bbox, timestamp= int(timestamp_detect))
        print(f"Data atualizada => bbox:{bbox}, real data:{real_pos}, relative:{relative_pos}")
        return real_pos