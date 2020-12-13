from Detect.DetectionData import *
import cv2
from AlgorithmsSensors.AlgorithmSensor import *
from os import listdir
from os.path import isfile
import airsim

from sklearn.svm import SVC
from sklearn.decomposition import PCA


class VisionSVMTracker(AlgorithmSensor):
    name = 'vision'
    latsBbox = None
    cont = 0
    svm = None

    def __init__(self,desvioThread,tracker='KFC',dir = 'Others/Imagens/SemAviao/'):
        AlgorithmSensor.__init__(self)
        print("Iniciando Visão")
        self.desvioThread = desvioThread
        self.client = airsim.MultirotorClient()
        self.dir = dir
        self.train()
        if tracker == 'MIL':
            self.tracker = cv2.TrackerMIL_create()
        elif tracker == 'TLD':
            self.tracker = cv2.TrackerTLD_create()
        else:
            self.tracker = cv2.TrackerKCF_create()

    def getDados(self):
        imgs = []
        datas = []
        target = []
        listPaths = listdir(self.dir)
        # Dados positivos
        for item in listPaths:
            path = self.dir + item
            if isfile(path):
                image = cv2.imread(path, 0)
                imgs.append(image)
                datas.append(image.reshape(-1))
                target.append(0)
        listPaths = listdir(self.dir )
        # Dados Negativos
        for item in listPaths:
            path = self.dir  + item
            if isfile(path):
                image = cv2.imread(path, 0)
                imgs.append(image)
                datas.append(image.reshape(-1))
                target.append(1)
        dict = {'img': imgs, 'target': target, 'data': datas}
        return dict

    def train(self):
        print("Treinando")
        dicData = self.getDados()
        data = np.array(dicData['data'])
        target = dicData['target']
        # PCA
        n_components = 150
        self.pca = PCA(n_components=n_components, svd_solver='randomized',
                       whiten=True).fit(data)
        data = self.pca.transform(data)
        # SVM
        self.svm = SVC(C=100, gamma=0.01)
        print('target:', len(data), 'data', len(target))
        self.svm.fit(data, target)
        print("Treino Finalizado")

    def slidingWindows(self, frame):
        stepSize = 30
        windowSizeX = 120
        windowSizeY = 60
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for y in range(0, frame.shape[0], stepSize):
            if (y + windowSizeY > frame.shape[0]):
                y = frame.shape[0] - windowSizeY
            for x in range(0, frame.shape[1], stepSize):
                if (x + windowSizeX > frame.shape[1]):
                    x = frame.shape[1] - windowSizeX
                crop_img = frame[y:y + windowSizeY, x:x + windowSizeX]
                crop_img = crop_img.reshape(-1)
                data = self.pca.transform([crop_img])
                predito = self.svm.predict(data)
                print("Predito",predito)
                if predito[0] == 1:
                    bbox = (x, x + windowSizeX, y, y + windowSizeY)
                    return bbox
        return None

    def run(self):
        #Iniciando o video
        print("Iniciar Video")
        primeroFrame = self.getImage()
        # Verifica se o frame não é vazio
        while len(np.unique(primeroFrame)) < 20:
            primeroFrame = self.getImage()

        #Começa a mostrar o video
        cv2.imshow("svm", primeroFrame)
        cv2.waitKey(1)
        #Detectando com SVM
        frame,bboxInicial = self.detect()
        frame = self.getImage()

        #Iniciando o rastreamento
        self.tracker.init(frame, bboxInicial)
        while True:
            print("Tracker Iniciado")
            self.updateTracker()

    def getImage(self):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
        response = response[0]
        # get numpy array
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        # reshape array to 4 channel image array H X W X 4
        img_rgba = img1d.reshape(response.height, response.width, 4)
        return img_rgba

    def detect(self):
        bbox = None
        while bbox is None:
            frameatual = self.getImage()
            bbox = self.slidingWindows(frameatual)
            cv2.imshow("svm", frameatual)
            cv2.waitKey(1)
        bboxReturn = (bbox[0],bbox[2],bbox[1]-bbox[0],bbox[3]-bbox[2])
        return frameatual,bboxReturn

    def updateTracker(self):
        frame = self.getImage()
        # Start timer
        timer = cv2.getTickCount()
        # Update tracker

        ok, bbox = self.tracker.update(frame[:, :, :3])
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
        x1,y1,x2,y2 = self.getPoints(bbox)

        if ok:
            # Desenhando Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2, 1)
            #Verificando Distancia
            depthImage = self.getDepth()
            print("depth:",y1,y2,x1,x2)
            distanceMin = depthImage[y1:y2,x1:x2].min()
            cv2.putText(frame, "distancia:{}".format(distanceMin), (100, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            #Enviar dados recebidos
            detectData = DetectionData(distanceMin)
            self.desvioThread.detectionData = detectData

        else:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
            distanceMin = np.inf

        # Display FPS on frame
        cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);
        # Display resultado
        cv2.imshow("svm", frame)
        cv2.waitKey(1)


    def getPoints(self,bbox):
        x1 = abs(int(bbox[0]))
        y1 = abs(int(bbox[1]))
        larg = int(bbox[2])
        alt = int(bbox[3])
        x2 = int(x1 + larg)
        y2 = int(y1 + alt)
        return x1,y1,x2,y2

    def getDepth(self):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthPlanner, True)])
        response = response[0]
        # get numpy array
        img1d = airsim.list_to_2d_float_array(response.image_data_float, response.width, response.height)
        return img1d