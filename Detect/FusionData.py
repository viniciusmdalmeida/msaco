from Detect.DetectionData import  *
class FusionData:
    def __init__(self):
        self.detectionList = []

    def clearList(self):
        self.detectionList = []

    def addDetect(self,detect_data):
        self.detectionList.append(detect_data)

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
            dict_detect[key] = dict_detect[key][0]
        detect_data = DetectionData()
        output_detect = detect_data.updateData(**dict_detect)
        return output_detect
    '''
    def fusionLogic(self,list_data,key):
        if key == 'distance':
            return sum(list_data)/len(list_data)
        else:
            return_data = []
            for item in 
    '''
