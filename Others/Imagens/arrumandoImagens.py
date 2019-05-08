from os import listdir,rename
from os.path import isfile,isdir
import cv2
from random import randint

def TrocarNomeImageAviao():
    dir = 'ImagenAviao/'
    cont = 0
    listadirertorio = [dir]
    for diretorio in listadirertorio:
        listaPaths = listdir(diretorio)
        print(listaPaths)
        for path in listaPaths:
            if isfile(diretorio+path):
                print(path)
                rename(diretorio+path,diretorio+'frame_{}.jpg'.format(cont))
                cont += 1
            else:
                listadirertorio.append(diretorio+path+'/')


def CortarSemAviao():
    dir = 'SemAviao/'
    listPaths = listdir(dir)
    cont = 0
    for item in listPaths:
        if isfile(dir+item):
            print(item)
            imagem = cv2.imread(dir+item,cv2.COLOR_BGR2RGB)
            y0,x0,z = imagem.shape
            x = randint(0,x0-120)
            y = randint(0, y0 - 60)
            crop_img = imagem[y:y+60, x:x+120]
            cv2.imwrite(dir+'Cortadas/imagem{}.jpg'.format(cont),crop_img)
            cont += 1


CortarSemAviao()


