import numpy as np
import cv2
from os import listdir
from os.path import isfile
import pickle
import yaml
#sklearn
from sklearn.model_selection import cross_val_score
#sklearn models
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.decomposition import PCA
#lightgbm
import lightgbm as lgb

import random


def get_dict_dados(windowSizeY,windowSizeX,negativeImg_path,positiveImg_path,depth=False):
    dim = (windowSizeY, windowSizeX)
    imgs = []
    datas = []
    target = []
    # Dados Negativos: Sem o avião
    num_class = 0
    #normalize data
    list_negative_files = listdir(negativeImg_path)
    list_positive_files = listdir(positiveImg_path)
    print(f"arquivos negativos:{len(list_negative_files)}, arquivos positivos:{len(list_positive_files)}")
    random.shuffle(list_negative_files)
    #list_negative_files = list_negative_files[:len(list_positive_files)]
    dict_data = {negativeImg_path:list_negative_files,positiveImg_path:list_positive_files}
    for path in dict_data:
        list_files = dict_data[path]
        print(f"Lendo arquivos do tipo:{path}")
        for file_name in list_files:
            file_path = path + file_name
            if isfile(file_path):
                if depth:
                    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                else:
                    image = cv2.imread(file_path, 1)
                #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
                imgs.append(image)
                datas.append(image.reshape(-1))
                target.append(num_class)
        num_class += 1
    dict = {'img': imgs, 'target': target, 'data': datas}
    return dict


def train_model(dict_data,model,prep_data_model=None,model_name=None,save_path='../data/models/',prep_model_name=None):
    X = dict_data['data']
    X = prep_data_model.fit_transform(X)
    y = dict_data['target']
    model.fit(X,y)
    if model_name:
        pickle.dump(model, open(save_path+model_name, 'wb'))
    if prep_model_name:
        pickle.dump(prep_data_model, open(save_path+prep_data_model, 'wb'))
    return model

def normalize_class(X,y):
    print("normalize class")
    #separando dados em um dicionario
    dict_class_data = {}
    for num_item in range(len(X)):
        item = X[num_item]
        classe = y[num_item]
        if not classe in dict_class_data:
            dict_class_data[classe] = [item]
        else:
            dict_class_data[classe].append(item)
    #calculando classe com menos itens
    cont_min_class = np.inf
    for classe in dict_class_data:
        if len(dict_class_data[classe]) < cont_min_class:
            cont_min_class = len(dict_class_data[classe])
    #normalizando classes
    for classe in dict_class_data:
        random.shuffle(dict_class_data[classe])
        dict_class_data[classe] = dict_class_data[classe][:cont_min_class]
    #Voltando a ser uma lista
    X = []
    y = []
    for classe in dict_class_data:
        num_items = len(dict_class_data[classe])
        X += dict_class_data[classe]
        y += [classe]*num_items
    return X,y

def cross_over_train_model(dict_data,model,prep_model,save_path='../../../data/models/',
                           model_name=None,prep_model_name='prep_model.sav', metric = 'balanced_accuracy'):
    X = np.array(dict_data['data'])
    y = dict_data['target']
    if prep_model:
        #X,y = normalize_class(X,y)
        prep_model.fit(X)
        X = prep_model.transform(X)
        pickle.dump(prep_model, open(save_path + prep_model_name + '.sav', 'wb'))
    #calc_cross Validade
    print("Start cross validade")
    scores = cross_val_score(model, X, y, cv=5,scoring=metric)
    #train
    print("Start train")
    model.fit(X,y)
    if model_name:
        pickle.dump(model, open(save_path+model_name, 'wb'))
    return model,scores




################################################
# Começando o codigo
################################################
print("Iniciando os treinos")
print("Lendo as configurações")
config_path='../../config.yml'

with open(config_path, 'r') as file_config:
    config = yaml.full_load(file_config)
img_width = config['algorithm']['vision']['windowSizeX']
img_height = config['algorithm']['vision']['windowSizeY']
negativeImg_path =  config['algorithm']['vision']['dirPositveImagem']
positiveImg_path =  config['algorithm']['vision']['dirNegativeImagem']
Msufix = config['algorithm']['vision']['model_sufix']

print("Lendo as imagens")
#get data
dict_data = get_dict_dados(img_width,img_height,negativeImg_path,positiveImg_path,depth=True)
#load model
print("Ler arquivos terminados")
print("Treinando PCA")
prep_model = PCA(n_components=200, svd_solver='randomized', whiten=True)
dict_models = {f'svm_{Msufix}':SVC(C=100, gamma=0.01),
               f'lgb_{Msufix}':lgb.LGBMClassifier(),
               f'rf_{Msufix}':RandomForestClassifier(),
               f'naive_{Msufix}':GaussianNB(),
               f'neural_{Msufix}':MLPClassifier()}

print("Treinando modelos!")
#Save status
for model_name in dict_models:
    file_name = model_name + '.sav'
    model = dict_models[model_name]
    metric = 'precision'
    model, cross_validade = cross_over_train_model(dict_data, model, prep_model, model_name=file_name,
                                                   prep_model_name=f'pca_{Msufix}', metric=metric)
    print(cross_validade, ":", cross_validade.sum() / len(cross_validade))
    with open('../../../data/models/models.csv','a') as file:
        model = model.__class__.__name__
        prep_model_name = 'PCA'
        mean_acu = cross_validade.sum() / len(cross_validade)
        obs = f'complet_image,size:{img_width}x{img_height},{metric}'
        file.write(f'{model};{prep_model_name};{file_name};{mean_acu},{obs}\n')
        print(f'{model};{prep_model_name};{file_name};{mean_acu},{obs}\n')