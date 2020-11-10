from AlgorithmsSensors.cam.VisionBase import *

from sklearn.svm import SVC
from sklearn.decomposition import PCA
from os import listdir
from os.path import isfile

class VisionRGBSVM(VisionBase):
    name = 'vision SVM algorithm'
    latsBbox = None
    cont = 0
    svm = None
    dirPositveImagem = "Others/Imagens/ImagenAviao/"
    dirNegativeImagem= "Others/Imagens/SemAviao/"

    def __init__(self,detectRoot,train=True):
        VisionBase.__init__(self, detectRoot)
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
        while len(np.unique(primeroFrame)) < self.config['algorithm']['Vision']['min_area']:
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

