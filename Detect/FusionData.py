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
            self.dict_detect[key] = self.fusionLogic(self.dict_detect[key])
        output_detect = DetectionData()
        output_detect.updateData(**self.dict_detect)
        return output_detect

    def cleanMean(self,list):
        if len(list.shape) < 2:
            list = [x for x in list if np.isfinite(x) and (not np.isnan(x))] #list[np.isfinite(list)]
            if len(list) == 0:
                return np.inf
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
        list_data_np = np.array(list_data)
        if np.issubdtype(list_data_np.dtype, np.number):  # check is numeric
            if len(list_data_np.shape) > 1:
                list_data_np = self.cleanMean(list_data_np)
            else:
                list_data_np = self.cleanMean(list_data_np)
        else:
            list_data_np = list_data_np[0]
        if type(list_data_np) == np.ndarray:
            return tuple(list_data_np)
        else:
            return list_data_np

class FusionData_MeanWeighted(BaseFusionData):
    def fusionLogic(self,list_data):
        list_data_np = np.array(list_data)
        if np.issubdtype(list_data_np.dtype, np.number):
            path_algorithm = 'algorithm_metric.yml'
            with open(path_algorithm, 'r') as file_config:
                config_algorithm = yaml.full_load(file_config)
            # buscando peso a partir do arquivo de configuração e nomes dos algoritmos
            list_name = [algorithm_name for algorithm_name in self.dict_detect['algoritmo']]
            list_weight = [config_algorithm[algorithm_name] for algorithm_name in list_name]
            #retirando infinitos
            list_data_np,list_weight = self.check_invalid(list_data_np,list_weight)
            # normalizando o peso
            list_weight = np.array([weigth/sum(list_weight) for weigth in list_weight])
            # calculando media ponderada
            list_data_np = np.nansum([list_data_np[cont] * list_weight[cont] for cont in range(len(list_weight))],axis=0)
        if type(list_data_np) == np.ndarray:
            return tuple(list_data_np)
        else:
            return list_data_np

    def check_invalid(self,list_data,list_weight):
        list_weight_aux = []
        list_data_aux = []
        for cont in range(len(list_data)):
            data = list_data[cont]
            if isinstance(data, numbers.Number):
                if np.isfinite(data) and (not np.isnan(data)):
                    list_data_aux.append(list_data[cont])
                    list_weight_aux.append(list_weight[cont])
            elif all(np.isfinite(data)) and (not all(np.isnan(data))):
                list_data_aux.append(list_data[cont])
                list_weight_aux.append(list_weight[cont])
        return list_data_aux,list_weight_aux