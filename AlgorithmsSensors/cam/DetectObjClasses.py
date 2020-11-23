import airsim  # pip install airsim
import numpy as np
import cv2
from abc import abstractmethod
from os import listdir
from os.path import isfile
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.decomposition import PCA
import pickle

class DetectBase:
    def __init__(self,config):
        self.config = config

    @abstractmethod
    def detect(self,frameAtual,frameInicial=None):
        pass

class DetectMog(DetectBase):
    def detect(self, frameAtual,frameInicial=None):
        # Aplicando operações basicas no primeiro frame
        primeroFrame = frameInicial.copy()
        primeroFrame = cv2.cvtColor(primeroFrame, cv2.COLOR_BGR2GRAY)
        primeroFrame = cv2.GaussianBlur(primeroFrame, (21, 21), 0)
        # Aplicando operações basicas no frame atual
        frame = cv2.cvtColor(frameAtual, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (21, 21), 0)
        # calculanod diferença entre os frames
        frameDelta = cv2.absdiff(primeroFrame, frame)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        # Dilatando o thresholded image para preencher os buracos e encontrar os contornos
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)
        # procurando maior boundbox encontrado
        if type(cnts) is None or len(cnts) <= 0:
            return None
        max_cnts = cnts[0]
        for c in cnts:
            if cv2.contourArea(c) > cv2.contourArea(max_cnts):
                max_cnts = c
        # Verificando se o maior contorno é maior que minimo da configuração
        if cv2.contourArea(max_cnts) < self.config['algorithm']['vision']['min_area']:
            return None
        else:
            print("Area:", cv2.contourArea(max_cnts))
        # Buncando tamanho do boundbox e retornando
        (x, y, w, h) = cv2.boundingRect(max_cnts)
        return (x, y, w, h)

class DetectMLBase(DetectBase):
    def __init__(self, config,nameModel=None,namePrepDataModel=None,train=False):
        self.config = config
        self.nameModel = nameModel
        self.namePrepDataModel = namePrepDataModel
        self.windowSizeX = self.config['algorithm']['vision']['windowSizeX']
        self.windowSizeY = self.config['algorithm']['vision']['windowSizeY']

        self.dirPositveImagem = self.config['algorithm']['vision']['dirPositveImagem']
        self.dirNegativeImagem = self.config['algorithm']['vision']['dirNegativeImagem']
        self.dirModel = self.config['algorithm']['vision']['dirModels']+self.nameModel+'.sav'
        if namePrepDataModel:
            self.dirModelPrepData = self.config['algorithm']['vision']['dirModels'] + self.namePrepDataModel + '.sav'
        if train:
            self.train()
        else:
            self.model = pickle.load(open(self.dirModel, 'rb'))
            self.prepData = pickle.load(open(self.dirModelPrepData, 'rb'))

    def getDados(self):
        dim = (self.windowSizeY, self.windowSizeX)

        imgs = []
        datas = []
        target = []

        listPaths = listdir(self.dirNegativeImagem)
        # Dados Negativos: Sem o avião
        for item in listPaths:
            path = self.dirNegativeImagem + item
            if isfile(path):
                image = cv2.imread(path, 0)
                image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
                imgs.append(image)
                datas.append(image.reshape(-1))
                target.append(0)
        listPaths = listdir(self.dirPositveImagem)
        # Dados positivos: Com o avião
        for item in listPaths:
            path = self.dirPositveImagem + item
            if isfile(path):
                image = cv2.imread(path, 0)
                image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
                imgs.append(image)
                datas.append(image.reshape(-1))
                target.append(1)
        dict = {'img': imgs, 'target': target, 'data': datas}
        return dict

    def train(self):
        dicData = self.getDados()
        data = np.array(dicData['data'])
        target = dicData['target']
        if self.namePrepDataModel:
            data = self.prepData.fit(data).transform(data)
            pickle.dump(self.prepData, open(self.dirModelPrepData, 'wb'))

        # SVM
        self.model.fit(data, target)
        pickle.dump(self.model, open(self.dirModel, 'wb'))
        print("Fim do treino")

    def detect(self, frame, primeiroFrame=None):
        stepSize = 20
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for y in range(0, frame.shape[0], stepSize):
            if (y + self.windowSizeY > frame.shape[0]):
                y = frame.shape[0] - self.windowSizeY
            for x in range(0, frame.shape[1], stepSize):
                if (x + self.windowSizeX > frame.shape[1]):
                    x = frame.shape[1] - self.windowSizeX
                crop_img = frame[y:y + self.windowSizeY, x:x + self.windowSizeX]
                data = crop_img.reshape(-1)
                if self.namePrepDataModel :
                    data = self.prepData.transform([data])
                predito = self.model.predict([data])
                if predito[0] == 1:
                    bbox = (x, y, self.windowSizeX, self.windowSizeY)
                    return bbox
        return None


class DetectSVM(DetectMLBase):
    def __init__(self, config,nameModel='svm',namePrepDataModel='pca',train=False):
        # PCA
        n_components = 150
        self.prepData = PCA(n_components=n_components, svd_solver='randomized', whiten=True)
        # SVM
        self.model = SVC(C=100, gamma=0.01)
        DetectMLBase.__init__(self,config, nameModel=nameModel, namePrepDataModel=namePrepDataModel, train=train)

class DetectNeural(DetectMLBase):
    def __init__(self, config,nameModel='neural network',namePrepDataModel='pca',train=True):
        if namePrepDataModel == 'pca':
            # PCA
            n_components = 150
            self.prepData = PCA(n_components=n_components, svd_solver='randomized', whiten=True)
        # SVM
        self.model = MLPClassifier(hidden_layer_sizes=(75,20))
        DetectMLBase.__init__(self,config, nameModel=nameModel, namePrepDataModel=namePrepDataModel, train=train)
