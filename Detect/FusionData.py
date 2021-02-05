from Detect.DetectionData import  *
from abc import ABC, abstractmethod
import copy

class BaseFusionData(ABC):
    def __init__(self):
        self.detectionList = []

    def clearList(self):
        self.detectionList = []

    def addDetect(self,detect_data):
        self.detectionList.append(copy.deepcopy(detect_data))
        for detectItem in self.detectionList:
            print("\t-",detectItem.getDictData()['algoritmo'])

    def getFusion(self):
        dict_detect = {}
        for detect in self.detectionList:
            detect_data = detect.getDictData()
            for key in detect_data:
                if key in dict_detect:
                    dict_detect[key].append(detect_data[key])
                else:
                    dict_detect[key] = [detect_data[key]]
        for key in dict_detect:
            dict_detect[key] = self.fusionLogic(dict_detect[key])
        output_detect = DetectionData()
        output_detect.updateData(**dict_detect)
        return output_detect

    @abstractmethod
    def fusionLogic(self,list_data):
        pass

class FusionData_Mean(BaseFusionData):
    def fusionLogic(self,list_data):
        list_data_np = np.array(list_data)
        if np.issubdtype(list_data_np.dtype, np.number):  # check is numeric
            if len(list_data_np.shape) > 1:
                list_data_np = list_data_np.mean(axis=0)
            else:
                list_data_np = list_data_np.mean()
        else:
            list_data_np = list_data_np[0]
        if type(list_data_np) == np.ndarray:
            return tuple(list_data_np)
        else:
            return list_data_np

class FusionData_MeanWeighted(BaseFusionData):
    def fusionLogic(self,list_data):
        dict_weigh = {}
        list_data_np = np.array(list_data)
        if np.issubdtype(list_data_np.dtype, np.number):  # check is numeric
            if len(list_data_np.shape) > 1:
                list_data_np = list_data_np.mean(axis=0)
            else:
                list_data_np = list_data_np.mean()
        else:
            list_data_np = list_data_np[0]
        if type(list_data_np) == np.ndarray:
            return tuple(list_data_np)
        else:
            return list_data_np