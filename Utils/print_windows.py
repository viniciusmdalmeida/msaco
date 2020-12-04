import cv2
import json
from shapely.geometry import Polygon
from shapely.ops import cascaded_union
from os import listdir, mkdir,remove
from os.path import isdir,isfile
from random import sample, shuffle
import numpy as np
from keras.preprocessing.image import load_img
from numpy import Inf
import pandas as pd
from shutil import copy

"""
Este codigo é uma segunda tetantiva de separar dados para teste.
Ele pecorre uma imagem com a função de janela deslizante, e separar este dados conforme a classe
caso a janela tenha mais 10% de sua area em algum poligono pre classificado ela e salva em uma pasta 
que representa a classe, caso não e salva com background
"""
import random

class Json_Poligon:
    def __init__(self, file_path):
        self.file_path = file_path
        json_file = open(file_path, 'r')
        self.json_data = json.load(json_file)

    def get_list_poligons(self):
        list_shape = self.json_data['shapes']
        list_poligon = []
        # Criando lista de saida
        for n_shape in range(len(list_shape)):
            points = list_shape[n_shape]['points']
            label = list_shape[n_shape]['label']
            item = {'points': points, 'label': label}
            list_poligon.append(item)
        return list_poligon

    def get_bboxfpoligon(self, list_points):
        max_x = 1
        min_x = np.Inf
        max_y = 1
        min_y = np.Inf
        for point in list_points:
            if point[0] > max_x:
                max_x = point[0]
            if point[0] < min_x:
                min_x = point[0]
            if point[1] > max_y:
                max_y = point[1]
            if point[1] < min_y:
                min_y = point[1]
        return [min_x, max_x, min_y, max_y]

    def save_imgPoligons(self, image, nameImage, path, y_eixo=True, pos_y=20,seplabel=False,eixo=True):
        list_poligons = self.get_list_poligons()
        cont = 0
        nameImage = nameImage.replace('.jpg', '')
        path_file = path
        for poligon in list_poligons:
            bbox = self.get_bboxfpoligon(poligon['points'])
            label = poligon['label']
            if not eixo:
                point = label.rfind('_')
                label = label[:point]
            if seplabel:
                if not label in listdir(path):
                    mkdir(path+label+'/')
                path_file = path + label+'/'
            if y_eixo:
                crop_img = image[int(bbox[2]):int(bbox[3]) + pos_y, int(bbox[0]):int(bbox[1])]
            else:
                crop_img = image[:int(bbox[3]) + pos_y, int(bbox[0]):int(bbox[1])]
            file_name = "{}{}_{}.jpg".format(path_file, nameImage, label)
            cv2.imwrite(file_name, crop_img)
            cont += 1

    def update_label(self, new_label, num_label):
        if new_label[0] == '_':
            self.json_data['shapes'][num_label]['label'] += new_label
        elif len(new_label) > 1:
            self.json_data['shapes'][num_label]['label'] = new_label
        with open(self.file_path, 'w') as f:
            json.dump(self.json_data, f)

    def poligonFbbox(self, bbox):
        xmin = bbox[0]
        xmax = bbox[1]
        ymin = bbox[2]
        ymax = bbox[3]
        return Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)])

    def IOU(self,poligon1,poligon2):
        union = poligon1.union(poligon2).area
        intersection = poligon1.intersection(poligon2).area
        if union == 0:
            return 0
        return intersection/union


class Imagem_data:
    def __init__(self, image, keras=False):
        # print(image)
        self.keras = keras
        if type(image) == str:
            if keras:
                self.image = load_img(image)
            else:
                self.image = cv2.imread(image)
        else:
            self.image = image
            self.keras = False

    def slidingWindows(self, stepSize=50, windowSizeX=80, windowSizeY=80):
        """
        Função para fazer a janela deslizante, ela pecorre a imagem e retorna um dicionario
        pequenas janelas com o tamanho windowSizeX x windowSizeY, no dicionario estão as
        imagens, seus pontos iniciais x e y

        :param stepSize: tamanho dos saltos entre as imagens (ela pode ser menor que o tamanho da imagem)
        :param windowSizeX: largura das imagem retornadas
        :param windowSizeY: altura das imagens retornadas
        :return: dict: com três chaves, "windows" : a lista de imagens,
        "x": o ponto x aonde a janela começa, "y": o ponto y aonde a imagem começa
        """
        windows = []
        xs = []
        ys = []
        for y in range(0, self.image.shape[0], stepSize):
            if (y + windowSizeY > self.image.shape[0]):
                y = self.image.shape[0] - windowSizeY
            for x in range(0, self.image.shape[1], stepSize):
                if (x + windowSizeX > self.image.shape[1]):
                    x = self.image.shape[1] - windowSizeX
                crop_img = self.image[y:y + windowSizeY, x:x + windowSizeX]
                if crop_img.shape[0] != 50 or crop_img.shape[1] != 50:
                    crop_img = cv2.resize(crop_img, (windowSizeX, windowSizeY))
                windows.append(crop_img)
                xs.append(x)
                ys.append(y)
        dic_windows = {'windows': windows, 'x': xs, 'y': ys}
        return dic_windows

    def get_poligon_json(self, file_path):
        list_poligon = []
        # Lendo arquivo
        json_file = open(file_path, 'r')
        json_data = json.load(json_file)
        list_shape = json_data['shapes']
        # Criando lista de saida
        for n_shape in range(len(list_shape)):
            points = list_shape[n_shape]['points']
            label = list_shape[n_shape]['label']
            item = {'points': points, 'label': label}
            list_poligon.append(item)
        return list_poligon

    def save_windows(self, path, name, dic_windows, list_poligon, inters_area=0.05):
        cont_windows = 0
        name = name.replace('.jpg', '')
        for n_window in range(len(dic_windows['windows'])):
            image = dic_windows['windows'][n_window]
            larg = image.shape[0]
            alt = image.shape[1]
            img_area = larg * alt
            x = dic_windows['x'][n_window]
            y = dic_windows['y'][n_window]
            image_poligon = Polygon([(x, y), (x, y + alt), (x + larg, y + alt), (x + larg, y)])
            isEixo = False
            for eixo_poligon in list_poligon:
                poligon = Polygon(eixo_poligon['points'])
                intersection = image_poligon.intersection(poligon)
                label = eixo_poligon['label']
                if intersection.area > img_area * inters_area:
                    if not label in listdir(path):
                        mkdir(path + '/' + label)
                    file_path = "{}/{}/{}_{}.jpg".format(path, label, name, cont_windows)
                    cv2.imwrite(file_path, image)
                    isEixo = True
            if isEixo == False:
                if not 'background' in listdir(path):
                    mkdir(path + '/' + 'background')
                file_path = "{}/{}/{}_{}.jpg".format(path, 'background', name, cont_windows)
                cv2.imwrite(file_path, image)
            cont_windows += 1

    def printslidingWindows(self, poligon,stepSize=80, windowSizeX=80, windowSizeY=80):
        list_detect = []
        list_not_detect = []
        for y in range(0, self.image.shape[0], stepSize):
            if (y + windowSizeY > self.image.shape[0]):
                y = self.image.shape[0] - windowSizeY
            for x in range(0, self.image.shape[1], stepSize):
                if (x + windowSizeX > self.image.shape[1]):
                    x = self.image.shape[1] - windowSizeX
                p1 = (x, y)
                p2 = (x + windowSizeX , y + windowSizeY)
                windows_poligon = Polygon([(x, y), (x, y + windowSizeY), (x + windowSizeX, y + windowSizeY), (x + windowSizeX, y)])
                intersection = windows_poligon.intersection(poligon)
                if intersection.area > (windowSizeY*windowSizeX) * 0.02:
                    list_detect.append([p1,p2])
                else:
                    list_not_detect.append([p1, p2])
        random.shuffle(list_not_detect)
        list_not_detect = list_not_detect[: len(list_detect)+2]
        for item in list_not_detect:
            cv2.rectangle(self.image, item[0], item[1], (0, 0, 255), 2, 1)
        for item in list_detect:
            cv2.rectangle(self.image, item[0], item[1], (255, 0, 0), 2, 1)
        return self.image



    def get_windows(self, list_bbox, expand_y=True):
        list_output = []
        for bbox in list_bbox:
            xmin, ymin,xmax, ymax = bbox
            #print('get_windows:: xmin:{},ymin:{},xmax:{},ymax:{}'.format(xmin, ymin,xmax, ymax))
            if expand_y:
                ymin = 0
            if self.keras:
                image_out = self.image.crop((xmin, ymin, xmax, ymax))
                #print("image_size:",image_out.size)
            else:
                image_out = self.image[xmin:xmax, ymin:ymax]
                #print("image_size:", image_out.shape)
            list_output.append(image_out)
        return list_output

###############################################################
###############################################################
#         Criando bbox
###############################################################
###############################################################

def save_widows(self, list_images, path_name):
    for i in range(len(list_images)):
        print(path_name + str(i) + ".jpg")
        cv2.imwrite(path_name + "-" + str(i) + ".jpg", list_images[i])

def get_data_dic(self, list_imagens, save=False):
    dicData = PrepData().get_data(class_path)
    targets = []
    datas = []
    cont = 0
    for image in list_imagens:
        # Trocar por particionar imagem!
        image_obj = Imagem_data(image)
        list_windows = image_obj.slidingWindows(stepSize=50)['windows']
        for window in list_windows:
            # print(window.shape)
            datas.append(window.reshape(-1))
            targets.append(target)
        if save:
            from random import random
            num = random()
            if random() > 0.85:
                tipo = 'test'
            else:
                tipo = 'train'
            path = 'SPMar/' + tipo + '/'
            if not target in listdir(path):
                mkdir(path + target)
            # print(path)
            path = path + str(target) + "/" + str(cont)
            self.save_widows(list_windows, path)
        cont += 1

    return targets, np.array(datas)




###################
#  Main
###################
base_path = 'C:/Users/vinic/OneDrive/Mestrado/Programa/Python/data/imagens/RGB/labelme/'
image_path = f'{base_path}frame_133.jpg'
json_path = f'{base_path}frame_133.json'
data = Imagem_data(image_path)
dict_windows = data.slidingWindows()
json_poligon = Json_Poligon(json_path)
list_poligon = json_poligon.get_list_poligons()
poligon = Polygon(list_poligon[0]['points'])
img_new = data.printslidingWindows(poligon)
cv2.imwrite('test.jpg', img_new)
