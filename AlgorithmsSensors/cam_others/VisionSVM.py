from Detect.DetectionData import *
import cv2
from AlgorithmsSensors.AlgorithmSensor import *
from os import listdir
from os.path import isfile

from sklearn.svm import SVC
from sklearn.decomposition import PCA

class VisionSVM(AlgorithmSensor):
    name = 'vision'
    latsBbox = None
    cont = 0
    svm = None

    def __init__(self,desvioThread):
        AlgorithmSensor.__init__(self)
        print("Iniciando Visão")
        self.desvioThread = desvioThread
        self.train()

    def getDados(self):
        imgs = []
        datas = []
        target = []
        dir = 'Others/Imagens/SemAviao/'
        listPaths = listdir(dir)
        # Dados positivos
        for item in listPaths:
            path = dir + item
            if isfile(path):
                image = cv2.imread(path, 0)
                imgs.append(image)
                datas.append(image.reshape(-1))
                target.append(0)
        dir = 'Others/Imagens/ImagenAviao/'
        listPaths = listdir(dir)
        # Dados Negativos
        for item in listPaths:
            path = dir + item
            if isfile(path):
                image = cv2.imread(path, 0)
                imgs.append(image)
                datas.append(image.reshape(-1))
                target.append(1)
        dict = {'img': imgs, 'target': target, 'data': datas}
        return dict

    def train(self):
        dicData =self.getDados()
        data = np.array(dicData['data'])
        target = dicData['target']
        # PCA
        n_components = 150
        self.pca = PCA(n_components=n_components, svd_solver='randomized',
                   whiten=True).fit(data)
        data = self.pca.transform(data)
        #SVM
        self.svm = SVC(C=100,gamma=0.01)
        print('target:', len(data), 'data', len(target))
        self.svm.fit(data, target)


    def slidingWindows(self,frame):
        stepSize = 20
        windowSizeX = 120
        windowSizeY = 60
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for y in range(0, frame.shape[0], stepSize):
            if (y+windowSizeY > frame.shape[0]):
                y = frame.shape[0] - windowSizeY
            for x in range(0, frame.shape[1], stepSize):
                if (x + windowSizeX > frame.shape[1]):
                    x = frame.shape[1] - windowSizeX
                crop_img = frame[y:y+windowSizeY, x:x+windowSizeX]
                crop_img = crop_img.reshape(-1)
                data = self.pca.transform([crop_img])
                predito = self.svm.predict(data)
                if predito[0] == 1:
                    bbox = (x,x+windowSizeX,y,y+windowSizeY)
                    return bbox
        return None

    def run(self):
        print("Iniciar Video")

        primeroFrame = self.getImage()
        while len(np.unique(primeroFrame)) < 20:
            # Verifica se o frame não é vazio
            primeroFrame = self.getImage()
        while True:
            frameatual = self.getImage()
            bbox = self.slidingWindows(frameatual)
            if not bbox is None:
                p1 = (int(bbox[0]), int(bbox[2]))
                p2 = (bbox[1],bbox[3])
                cv2.rectangle(frameatual, p1, p2, (255, 0, 0), 2, 1)

                depthImage = self.getDepth()
                distanceMin = depthImage[bbox[2]:bbox[3], bbox[0]:bbox[1]].min()
                self.detectData = DetectionData(distanceMin)
                self.desvioThread.detectionData = self.detectData
                cv2.putText(frameatual, "distancia:{}".format(distanceMin), (100, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            cv2.imshow("Primeiro Frame", frameatual)
            cv2.waitKey(1)

        # Verificando se algum objeto saliente
        bbox, size = self.detectObject(primeroFrame)
        self.tracker.init(primeroFrame, bbox)
        self.cont = 0

    def getImage(self):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
        response = response[0]
        # get numpy array
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        # reshape array to 4 channel image array H X W X 4
        img_rgba = img1d.reshape(response.height, response.width, 4)
        return img_rgba

    def getDepth(self):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthPlanner, True)])
        response = response[0]
        # get numpy array
        img1d = airsim.list_to_2d_float_array(response.image_data_float, response.width, response.height)
        return img1d

