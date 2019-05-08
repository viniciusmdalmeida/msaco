import cv2
import numpy as np
from os import listdir,rename
from os.path import isfile,isdir



SZ=20
bin_n = 16 # Number of bins

affine_flags = cv2.WARP_INVERSE_MAP|cv2.INTER_LINEAR


def deskew(img):
    m = cv2.moments(img)
    if abs(m['mu02']) < 1e-2:
        # no deskewing needed. 
        return img.copy()
    # Calculate skew based on central momemts. 
    skew = m['mu11']/m['mu02']
    # Calculate affine transform to correct skewness. 
    M = np.float32([[1, skew, -0.5*SZ*skew], [0, 1, 0]])
    # Apply affine transform
    img = cv2.warpAffine(img, M, (SZ, SZ), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)
    return img

def hog(img):
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
    mag, ang = cv2.cartToPolar(gx, gy)

    # quantizing binvalues in (0...16)
    bins = np.int32(bin_n*ang/(2*np.pi))

    # Divide to 4 sub-squares
    bin_cells = bins[:10,:10], bins[10:,:10], bins[:10,10:], bins[10:,10:]
    mag_cells = mag[:10,:10], mag[10:,:10], mag[:10,10:], mag[10:,10:]
    hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
    hist = np.hstack(hists)
    return hist


def getDados():
    imgs = []
    hogs = []
    datas = []
    target = []
    dir = 'SemAviao/'
    listPaths = listdir(dir)

    # Dados positivos
    for item in listPaths:
        path = dir + item
        if isfile(path):
            image = cv2.imread(path,0)
            imgs.append(image)
            datas.append(image.reshape(-1))
            target.append(1)
    dir = 'ImagenAviao/'
    listPaths = listdir(dir)

    #Dados Negativos
    for item in listPaths:
        path = dir + item
        if isfile(path):
            image = cv2.imread(path, 0)
            imgs.append(image)
            datas.append(image.reshape(-1))
            target.append(0)
    for image in imgs:
        deskImg = deskew(image)
        hogs.append(hog(deskImg))
    dict = {'img':imgs,'target':target,'hog':hogs,'data':datas}
    return dict

from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from  sklearn.naive_bayes import GaussianNB
from  sklearn.decomposition import PCA

dicData = getDados()
data = np.array(dicData['data'])
target = dicData['target']

#PCA
n_components = 150
data = PCA(n_components=n_components, svd_solver='randomized',
          whiten=True).fit_transform(data)


# Treino e teste
xTreino,xTeste,yTreino,yTeste = train_test_split(data,target)
#SVM
print("SVM1")
svm = SVC()
print('target:',len(xTreino),'data',len(yTreino))
svm.fit(xTreino,yTreino)
preditos = svm.predict(xTeste)
#Verificado
print(classification_report(preditos,yTeste))
#Grid
print("----grid-------")
param = {"C":[100,10,2,1,0.1],'gamma':[10,5,1,0.1,0.01,0.001],'kernel':['rbf','linear']}
grid = GridSearchCV(svm,param,refit=True,verbose=2,scoring='recall')
grid.fit(xTreino,yTreino)
preditos = svm.predict(xTeste)
print(grid.best_params_)
#Verificado
print(classification_report(preditos,yTeste))
#naive
nb = GaussianNB()
nb.fit(xTreino,yTreino)
preditos = nb.predict(xTeste)
#Verificado
print(classification_report(preditos,yTeste))