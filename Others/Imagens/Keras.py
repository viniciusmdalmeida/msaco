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

import tensorflow as tf

from keras.utils import to_categorical

from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten

#create model
model = Sequential()

#add model layers
model.add(Conv2D(64, kernel_size=3, activation='relu', input_shape=(28,28,1)))
model.add(Conv2D(32, kernel_size=3, activation='relu'))
model.add(Flatten())
model.add(Dense(10, activation='softmax'))

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
#train the model
model.fit(xTreino, yTreino, validation_data=(xTeste, yTeste), epochs=3)
preditos = model.predict(xTeste)

print(classification_report(preditos,yTeste))