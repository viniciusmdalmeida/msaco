import airsim  # pip install airsim
import numpy as np
import cv2
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from abc import abstractmethod
#Para o SVM
from os import listdir
from os.path import isfile
from sklearn.svm import SVC
from sklearn.decomposition import PCA

class Vision_RGB(AlgorithmSensor):
    name = 'vision'

    def __init__(self,detectRoot,showVideo=True):
        print('Start',self.name)
        AlgorithmSensor.__init__(self, detectRoot)
        self.detectData = None
        self.showVideo = showVideo

    @abstractmethod
    def run(self):
        pass

    def getImage(self):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
        response = response[0]
        # get numpy array
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        # reshape array to 4 channel image array H X W X 4
        img_rgba = img1d.reshape(response.height, response.width, 4)
        return img_rgba

    def printDetection(self,frame,bbox=None):
        # Start timer
        if self.showVideo:
            timer = cv2.getTickCount()
            if bbox is not None and len(bbox) >= 4:
                fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
                x1 = int(bbox[0])
                y1 = int(bbox[1])
                larg = int(bbox[2])
                alt = int(bbox[3])
                if (x1 >= 0 and y1 >= 0 and int(larg) >= 1 and int(alt) >= 1):
                    # Draw Bounding box
                    x2 = int(x1 + larg)
                    y2 = int(y1 + alt)
                    p1 = (x1, y1)
                    p2 = (x2, y2)
                    cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
                else:
                    # Tracking failure
                    cv2.putText(frame, "Tracking failure detected", (100, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
                # Display FPS on frame
                cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);
            cv2.imshow("Detect", frame)
            cv2.waitKey(1)


class VisionRGBDefault(Vision_RGB):
    name = "Vision RGB Default Algorithm"

    def __init__(self,detectRoot):
        Vision_RGB.__init__(self, detectRoot)

    def run(self):
        print("Iniciando",self.name)

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
            self.printDetection(frameBase)
            cv2.waitKey(1)
        size = bbox[2] * bbox[3]
        self.printDetection(frameBase, bbox)
        return bbox,size

    def backgroundDetect(self, frameInicial):
        primeroFrame = frameInicial.copy()
        primeroFrame = cv2.cvtColor(primeroFrame, cv2.COLOR_BGR2GRAY)
        primeroFrame = cv2.GaussianBlur(primeroFrame, (21, 21), 0)
        # compute the absolute difference between the current frame and
        # first frame
        frame = self.getImage()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (21, 21), 0)
        frameDelta = cv2.absdiff(primeroFrame, frame)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        img, cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        if type(cnts) is not None and len(cnts) > 0:
            cnts = cnts[0]
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

    def updateTracker(self):
        frame = self.getImage()
        # Update tracker
        ok, bbox = self.tracker.update(frame[:, :, :3])
        self.printDetection(frame,bbox)

class VisionRGBMOG(Vision_RGB):
    name = 'vision MOG algorithm'
    latsBbox = None
    cont = 0

    def __init__(self,detectRoot):
        Vision_RGB.__init__(self, detectRoot)

    def run(self):
        print("Iniciar Video")
        # self.camShifTracker()
        # self.tracker = cv2.TrackerKCF_create()
        self.tracker = cv2.TrackerBoosting_create()

        #Esperando dados validos
        primeroFrame = self.getImage()
        while len(np.unique(primeroFrame)) < 20:
            #Verifica se o frame não é vazio
            primeroFrame = self.getImage()

        self.backgroundDetectMog2()

    def getPoints(self,bbox):
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        larg = int(bbox[2])
        alt = int(bbox[3])
        x2 = int(x1 + larg)
        y2 = int(y1 + alt)
        return x1,y1,x2,y2

    def backgroundDetectMog2(self):
        fgbg = cv2.createBackgroundSubtractorMOG2()
        while True:
            frame = self.getImage()
            fgmask = fgbg.apply(frame)

            thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            contours,hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            if type(contours) is None or len(contours) <= 0:
                continue
            max = contours[0]
            for c in contours:
                if cv2.contourArea(c) >cv2.contourArea(max) :
                    max = c
            # (x, y, w, h) = cv2.boundingRect(max)

            #Desenhando quadrado
            # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2, 1)
            self.printDetection(frame,cv2.boundingRect(max))
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
            self.detectRoot.receiveData(self.detectData)

        fgmask = fgbg.apply(frame)

class VisionRGBSVM(Vision_RGB):
    name = 'vision SVM algorithm'
    latsBbox = None
    cont = 0
    svm = None
    dirPositveImagem = "Others/Imagens/ImagenAviao/"
    dirNegativeImagem= "Others/Imagens/SemAviao/"


    def __init__(self,detectRoot,train=True):
        Vision_RGB.__init__(self, detectRoot)
        if train:
            self.train()

    def getDados(self):
        imgs = []
        datas = []
        target = []

        listPaths = listdir(self.dirNegativeImagem)
        # Dados Negativos: Sem o avião
        for item in listPaths:
            path = self.dirNegativeImagem + item
            if isfile(path):
                image = cv2.imread(path, 0)
                imgs.append(image)
                datas.append(image.reshape(-1))
                target.append(0)
        listPaths = listdir(self.dirPositveImagem)
        # Dados positivos: Com o avião
        for item in listPaths:
            path = self.dirPositveImagem + item
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
            frameBase = self.getImage()
            bbox = self.slidingWindows(frameBase)
            if not bbox is None:
                self.sendresult()
            self.printDetection(frameBase, bbox)

        # Verificando se algum objeto saliente
        bbox, size = self.detectObject(primeroFrame)
        self.tracker.init(primeroFrame, bbox)
        self.cont = 0

