from abc import ABC, abstractmethod
import copy
import yaml
from Detect.DetectionData import  *
import numbers

class BaseFusionData(ABC):
    def __init__(self):
        self.detectionList = []

    def clearList(self):
        self.detectionList = []

    def addDetect(self,detect_data):
        self.detectionList.append(copy.deepcopy(detect_data))

    def getFusion(self):
        self.dict_detect = {}
        for detect in self.detectionList:
            detect_data = detect.getDictData().copy()
            for key in detect_data:
                if key in self.dict_detect:
                    self.dict_detect[key].append(detect_data[key])
                else:
                    self.dict_detect[key] = [detect_data[key]]
        for key in self.dict_detect:
            #TODO: Trocar isso pq ta feio
            if  key != 'algoritmo':
                self.dict_detect[key] = self.fusionLogic(self.dict_detect[key])
            else:
                self.dict_detect[key] = self.dict_detect[key]
        output_detect = DetectionData()
        output_detect.updateData(**self.dict_detect)
        return output_detect

    def cleanMean(self,list):
        if len(list.shape) < 2:
            list = [x for x in list if np.isfinite(x) and (not np.isnan(x))] #list[np.isfinite(list)]
            if len(list) == 0:
                return None
            return sum(list)/len(list)
        else:
            output_list = []
            for colun in range(list.shape[1]):
                colun_data = [x for x in list[:,colun] if np.isfinite(x) and (not np.isnan(x))] #list[np.isfinite(list[:,colun])]
                if len(colun_data) == 0:
                    output_list.append(np.inf)
                else:
                    output_list.append(sum(colun_data)/len(colun_data))
            return output_list
    @abstractmethod
    def fusionLogic(self,list_data):
        pass

class FusionData_Mean(BaseFusionData):
    def fusionLogic(self,list_data):
        list_data_np = np.array([x for x in list_data if not x is None])
        if np.issubdtype(list_data_np.dtype, np.number):  # check is numeric
            list_data_np = self.cleanMean(list_data_np)
        else:
            list_data_np = list_data_np[0]
        if type(list_data_np) == np.ndarray:
            return tuple(list_data_np)
        else:
            return list_data_np

class FusionData_MeanWeighted(BaseFusionData):
    def fusionLogic(self,list_data):
        #remove None
        list_valid = [x != None for x in list_data]
        list_data_np = np.array([x for x in list_data if  not x is None])
        if np.issubdtype(list_data_np.dtype, np.number):
            path_algorithm = 'algorithm_metric.yml'
            with open(path_algorithm, 'r') as file_config:
                config_algorithm = yaml.full_load(file_config)
            # buscando peso a partir do arquivo de configuração e nomes dos algoritmos
            list_name = [algorithm_name for algorithm_name in self.dict_detect['algoritmo']]
            list_weight = np.array([config_algorithm[algorithm_name] for algorithm_name in list_name])[list_valid]
            #retirando infinitos e calculando a media
            list_data_np = self.cleanMean(list_data_np,list_weight)
            # normalizando o peso
            #list_weight = np.array([weigth/sum(list_weight) for weigth in list_weight])
            # calculando media ponderada
            #list_data_np = np.sum([list_data_np[cont] * list_weight[cont] for cont in range(len(list_weight))],axis=0)
        if type(list_data_np) == np.ndarray and len(list_data_np)>0:
            return tuple(list_data_np)
        else:
            return list_data_np

    def cleanMean(self,list_data,list_weight):
        output_list = []
        if len(list_data.shape) < 2:
            list_valid = [np.isfinite(x) and (not np.isnan(x)) for x in list_data]
            list_data = np.array(list_data[list_valid])
            list_weight = list_weight[list_valid]
            #normalizando peso
            list_weight = np.array([weigth / sum(list_weight) for weigth in list_weight])
            if len(list_data) <= 0:
                return None
            output_list = sum(list_data*list_weight)
        else:
            for colun in range(list_data.shape[1]):
                list_valid = [np.isfinite(x) and (not np.isnan(x)) for x in list_data[:, colun]]
                list_data_norm = np.array(list_data[:, colun][list_valid])
                list_weight_norm = list_weight[list_valid]
                # normalizando peso
                list_weight_norm = np.array([weigth / sum(list_weight_norm) for weigth in list_weight_norm])
                if len(list_data_norm) <= 0:
                    output_list.append(np.inf)
                else:
                    output_list.append(sum(list_data_norm*list_weight_norm))
        return output_list