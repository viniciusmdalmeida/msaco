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
import yaml

"""
Este codigo é uma segunda tetantiva de separar dados para teste.
Ele pecorre uma imagem com a função de janela deslizante, e separar este dados conforme a classe
caso a janela tenha mais 10% de sua area em algum poligono pre classificado ela e salva em uma pasta 
que representa a classe, caso não e salva com background
"""


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

    def slidingWindows(self, config_path='../config.yml'):
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
        with open(config_path, 'r') as file_config:
            config = yaml.full_load(file_config)
        windowSizeX = config['algorithm']['vision']['windowSizeX']
        windowSizeY = config['algorithm']['vision']['windowSizeY']
        stepSize = config['algorithm']['vision']['stepSize']

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

    def save_windows(self, path, name, dic_windows, list_poligon, inters_area=0.3):
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
                try:
                    poligon = Polygon(eixo_poligon['points'])
                    intersection = image_poligon.intersection(poligon)
                    label = eixo_poligon['label']
                    if intersection.area > img_area * inters_area:
                        if not label in listdir(path):
                            mkdir(path + '/' + label)
                        file_path = "{}/{}/{}_{}.jpg".format(path, label, name, cont_windows)
                        cv2.imwrite(file_path, image)
                        isEixo = True
                except Exception as e:
                    print("ERROR:",e)
            if isEixo == False:
                if not 'background' in listdir(path):
                    mkdir(path + '/' + 'background')
                file_path = "{}/{}/{}_{}.jpg".format(path, 'background', name, cont_windows)
                cv2.imwrite(file_path, image)
            cont_windows += 1

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


class PrepData:
    def __init__(self):
        pass

    def get_car_ids(self,file_path,percent_car=1):
        list_files = listdir(file_path)
        list_ids = []
        for file in list_files:
            id = file.split('_')[0]
            if id not in list_ids:
                list_ids.append(id)
        shuffle(list_ids)
        cut_point = int(len(list_ids) * percent_car)
        return list_ids[:cut_point]

    def filter_files(self,lisdir,list_id):
        list_return = []
        for item in lisdir:
            if item.split('_')[0] in list_id:
                list_return.append(item)
        return list_return

    def save_all_bbox(self, base_path, save_path, y_eixo=True,sep_label=False,eixo=True):
        # Vereificando os caminhos
        if base_path[-1] != '/':
            base_path += '/'
        if save_path[-1] != '/':
            save_path += '/'
        # Pegando as imagens
        for file in listdir(base_path):
            file_path = base_path + file
            if isdir(file_path):
                # Caso ainda seja um diretorio chamar a mesma função recursivamente
                if not file in listdir(save_path):
                    mkdir(save_path + file)
                self.save_all_bbox(file_path+ '/', save_path + file+'/', y_eixo)
            elif 'json' in file_path:
                image_file = file.replace('json', 'jpg')
                image = Imagem_data(base_path + image_file)
                # print(image_file,"\n",image.image)
                json_file = Json_Poligon(file_path)
                json_file.save_imgPoligons(image.image, image_file, save_path, y_eixo,seplabel=sep_label,eixo=eixo)
    def get_data(self, class_path, keras=True):
        """
        Pega as imagens cortadas por rotulo
        :return:
            dict: com a chave sendo o rotulo e o valor a imagem (nparray)
        """
        dir_imagens = {}
        if class_path[-1] == '/':
            class_path = class_path[:-1]
        for label in listdir(class_path):
            # Verificando todas as pastas (classes)
            cont = 0
            # print("Label:",label)
            for image in listdir(class_path + "/" + label):
                # Pegando as imagens em cada pastas e salvando no dicionario
                # print(cont/len(listdir(class_path+"/"+label)),"%")
                image_path = class_path + "/" + label + "/" + image
                if keras:
                    img = load_img(image_path)
                else:
                    img = cv2.imread(image_path)
                if label in dir_imagens:
                    list_imagens = dir_imagens[label]
                    list_imagens.append(img.copy())
                    dir_imagens[label] = list_imagens
                else:
                    dir_imagens[label] = [img]
                if keras and img.fp is not None:
                    img.fp.closed
                cont += 1
        return dir_imagens

    def merge_labels(self, data, merge_labels):
        """
        Função para juntar dados de labels, usada para juntar os eixos em apenas um dado
        """
        out_put = {}
        for merge_name in merge_labels:
            merge_data = None
            for label in merge_labels[merge_name]:
                if merge_data is None:
                    merge_data = data[label]
                else:
                    merge_data.append(data[label])
            out_put[merge_name] = merge_data
        return out_put

    def normalize_class(self, data):
        """
        Função para normaliza base de dados desbalanceadas, colocando que todas tenham o mesmo numero de dados
        :return: lista de dados com menos
        """
        print(data.keys())
        # Pegando classe com menos exemplos
        min = float('inf')
        for label in data:
            if min > len(data[label]):
                min = len(data[label])
        for label in data:
            data[label] = sample(data[label], min)
        return data

    def train_test_split(self, data, test_size=0.25):
        train = {}
        test = {}
        for label in data:
            shuffle(data[label])
            split_point = int(len(data[label]) * test_size)
            test[label] = data[label][:split_point]
            train[label] = data[label][split_point:]
        return train, test

    def path_train_test(self,path_file,save_path,train_size=0.66,balance=True):
        dic_id = {}
        mkdir(save_path + 'test/')
        mkdir(save_path + 'train/')
        # Separando os eixos
        for file in listdir(path_file):
            if '.json' in file:
                json_file = open(path_file + file)
                json_data = json.load(json_file)
                car_id = file.split('_')[0]
                for shape in json_data['shapes']:
                    label = shape['label'].split('_')[1]
                    if label == 'outros':
                        label = 'outro'
                    if not car_id in dic_id:
                        dic_id[car_id] = label
                    elif 'outros' in dic_id[car_id] or dic_id[car_id] == 'suspenso':
                        continue
                    else:
                        dic_id[car_id] = label
                json_file.close()
        dic_label = {}
        for id in dic_id:
            label = dic_id[id]
            if not label in dic_label:
                dic_label[label] = [id]
            else:
                dic_label[label].append(id)
        # Separando treino e teste por tipo de eixo presente
        train_ids = []
        test_ids = []
        for label in dic_label:
            list_type = dic_label[label]
            print( "label:{}, tamanho:{}".format(label,len(list_type)))
            cut_point = int(len(list_type) * train_size)
            shuffle(list_type)
            train_ids += list_type[:cut_point]
            test_ids += list_type[cut_point:]
        print("Teste:", len(test_ids), 'Train', len(train_ids))
        print("Salvando arquivos")
        # salvando arquivos
        for file in listdir(path_file):
            id_car = file.split('_')[0]
            if id_car in test_ids:
                file = path_file + file
                copy(file, save_path + 'test/')
            else:
                file = path_file + file
                copy(file, save_path + 'train/')

    def save_windows_from_path(self, path, save_path):
        list_files = listdir(path)
        cont = 0
        print(save_path)
        for file in list_files:
            if isdir(path+file):
                if not file in listdir(save_path):
                    mkdir(save_path + file)
                self.save_windows_from_path(path +file+'/', save_path + file )
            elif 'jpg' in file:
                name = file.replace('.jpg', '')
                image_path = path + '/' + file
                json_path = image_path.replace('jpg', 'json')
                if not name + '.json' in list_files:
                    continue
                data = Imagem_data(image_path)
                dict_windows = data.slidingWindows()
                json_poligon = Json_Poligon(json_path)
                list_poligon = json_poligon.get_list_poligons()
                data.save_windows(save_path, name, dict_windows, list_poligon)
            cont += 1
            size = len(list_files)
            percent = cont / len(list_files)*100
            print("{}/{} : {:0.3f}%".format(cont, size, percent), end="\r")
        print("{}/{} : {:0.3f}%".format(cont, size, percent))

    def save_widows(self, list_images, path_name):
        """
        Salva a todas as imagens da lista no caminho passado
        """
        for i in range(len(list_images)):
            print(path_name + str(i) + ".jpg")
            cv2.imwrite(path_name + "-" + str(i) + ".jpg", list_images[i])

    def save_dic_image(self, dic, save_path):
        for label in dic:
            cont = 0
            for image in dic[label]:
                if not label in listdir(save_path):
                    mkdir(save_path + '/' + label)
                nameimg = "{}/{}/{}.jpg".format(save_path, label, str(cont))
                cv2.imwrite(nameimg, np.array(image))
                cont += 1

    def create_table(self, path_data, file_name,verbose=False,save=True):
        table = pd.DataFrame(columns=['car_id', 'hour', 'axle_number', 'axle_class', 'xmax', 'xmin', 'ymax', 'ymin'])
        if path_data[-1] != '/':
            path_data += '/'
        list_files = listdir(path_data)
        for file in list_files:
            if 'json' in file:
                json_data = Json_Poligon(path_data + file)
                list_poligons = json_data.get_list_poligons()
                car_id = file.split('_')[0]
                hour = car_id[-6:-4]
                for poligon in list_poligons:
                    label = poligon['label']
                    number = label.split('_')[-1]
                    ax_class = label.split('_')[1]
                    xmax, xmin, ymax, ymin = json_data.get_bboxfpoligon(poligon['points'])
                    if verbose:
                        print(label,'_',number,':',xmax, xmin, ymax, ymin)
                    table=table.append(
                        {'car_id': car_id, 'hour': hour,
                         'axle_number': number, 'axle_class': ax_class,
                         'xmax': xmax, 'xmin': xmin, 'ymax': ymax, 'ymin': ymin},
                        ignore_index=True)
        if save:
            table.to_csv(file_name, index_label ='index')
        return table

    def normalize_paths(self, root_path):
        """
        balanceia o numero de arquivos na pastas dentro de um direitorio raiz
        """
        dir_files = {}
        min = Inf
        for dir in listdir(root_path):
            dir_files[dir] = listdir(root_path + dir + '/')
            if len(dir_files[dir]) < min:
                min = len(dir_files[dir])
        print('min:',min)
        for dir in dir_files:
            if len(dir_files[dir]) > min:
                shuffle(dir_files[dir])
                list_remove = dir_files[dir][min:]
                for file in list_remove:
                    file_path = root_path + dir + '/' + file
                    # print(file_path)
                    if isfile(file_path):
                        remove(file_path)


class Post_processing:
    def show_windows(self, image, list_windows, bbox_width=80, bbox_heigth=80, color=(0, 0, 255)):
        image_out = image.copy()
        for window in list_windows:
            if type(window) == dict:
                x = window['x']
                y = window['y']
                cv2.rectangle(image_out, (x + bbox_width, y), (x, y + bbox_heigth), color, 2)
            else:
                cv2.rectangle(image_out, (int(window[0]), int(window[1])), (int(window[2]), int(window[3])), color, 2)
        cv2.imshow('fim', image_out)
        cv2.waitKey()

    def filter_detect(self, list_windows, threshold=0.1, min_widows=2, w_width=80, w_height=80):
        list_out = []
        list_poligon = []
        for window in list_windows:
            x = int(window['x'])
            y = int(window['y'])
            points = [(x, y), (x, y + w_height), (x + w_width, y + w_height), (x + w_width, y)]
            poligon = Polygon(points)
            list_poligon.append(poligon)
        list_poligon_copy = list_poligon.copy()
        for poligon in list_poligon_copy:
            list_poligon_copy.remove(poligon)
            n_intersect = 0  # Numero de itens removidos, serve para ajustar o error causado por remover em um for
            for n_poligon2 in range(len(list_poligon_copy)):
                poligon2 = list_poligon_copy[n_poligon2 - n_intersect]
                if poligon.intersection(poligon2).area / poligon.area > threshold:
                    poligon = cascaded_union([poligon, poligon2])
                    list_poligon_copy.remove(poligon2)
                    n_intersect += 1
            if n_intersect + 1 >= min_widows:
                bbox = self.get_max_bbox(list(poligon.exterior.coords))
                if bbox is not None:
                    list_out.append(bbox)
        return list_out

    def get_max_bbox(self, list_bbox, min_bbox=2):
        minX = np.Inf
        maxX = 0
        minY = np.Inf
        maxY = 0
        if len(list_bbox) <= min_bbox:
            return None
        for bbox in list_bbox:
            x = bbox[0]
            y = bbox[1]
            if x > maxX:
                maxX = x
            if x < minX:
                minX = x
            if y > maxY:
                maxY = y
            if y < minY:
                minY = y
        #print('get_max_bbox:',minX, minY, maxX, maxY)
        return minX, minY, maxX, maxY

    def get_class_labels(self, label_file, list_class):
        labels_file = open(label_file, 'r')
        labels = eval(labels_file.read())
        labels_file.close()
        output_list = []
        for n_result in range(len(list_class)):
            actual_class = list_class[n_result].argmax()
            output_list.append(labels[actual_class])
        return output_list

    def count_eixos(self, class_list, class_name='eixo_solo'):
        n_eixo = 0
        for item in class_list:
            if item == class_name:
                n_eixo += 1
        return n_eixo


###############################################################
###############################################################
#         Criando bbox
###############################################################
###############################################################

def save_widows(self, list_images, path_name):
    for i in range(len(list_images)):
        print(path_name + str(i) + ".jpg")
        cv2.imwrite(path_name + "-" + str(i) + ".jpg", list_images[i])

def get_data_dic(self, list_imagens, save=False,stepSize=50):
    dicData = PrepData().get_data(class_path)
    targets = []
    datas = []
    cont = 0
    for image in list_imagens:
        # Trocar por particionar imagem!
        image_obj = Imagem_data(image)
        list_windows = image_obj.slidingWindows(stepSize)['windows']
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
import os
from shutil import copyfile

labels_path = '../../data/imagens/RGB/labelme/'
dest_path = '../../data/imagens/RGB/windows/'
imagens_path = '../../data/imagens/RGB/voo/'
list_label = os.listdir(labels_path)
list_image = os.listdir(labels_path)
for label in list_label:
    name_file = label.replace('.json','.jpg')
    if not name_file in list_image:
        copyfile(imagens_path+name_file,labels_path+name_file)
prep_data=PrepData()
prep_data.save_windows_from_path(labels_path,dest_path)