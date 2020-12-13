from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from datetime import datetime

class ADS_B(AlgorithmSensor):
    name = "ADS_B Base"

    def __init__(self,detectRoot):
        AlgorithmSensor.__init__(self, detectRoot)
        self.file_path = self.config['sensors']['ADS-B']['reader_path']
        self.file_prefix = self.config['sensors']['ADS-B']['reader_file_prefix']

    def getData(self,to_str=True):
        date_str = datetime.now().strftime('%#d_%#m_%Y').replace("_0","_")
        file_path = f'{self.file_path}/{self.file_prefix}_{date_str}.txt'
        with open(file_path, 'r') as f:
            lines = f.read().splitlines()
            last_adsb = lines[-1]
        adsb_header = self.config['sensors']['ADS-B']['ADS-B_header']
        dict_data = dict(zip(adsb_header,last_adsb.split(',')))
        return dict_data

    def getStatus(self):
        return self.detectData

    def detect(self):
        #get intruse position
        intruse_data = self.getData()
        my_position = vars(self.client.simGetGroundTruthKinematics().position)
        #calc distance
        x_distance = abs((float(intruse_data['x_position'])/100) - my_position['x_val'])
        y_distance = abs((float(intruse_data['y_position'])/100) - my_position['y_val'])
        z_distance = abs((float(intruse_data['geo_altitude'])/100) - my_position['z_val'])
        distanceMin = min([x_distance,y_distance,z_distance])
        #calc distance
        intruse_position = [float(intruse_data['x_position']) / 100,
                            float(intruse_data['y_position']) / 100,
                            float(intruse_data['geo_altitude']) / 100]
        my_position_vector = [my_position['x_val'], my_position['y_val'], my_position['z_val']]
        distance = self.cal_distance(intruse_position, my_position_vector)
        #send detect data
        self.detectData.updateData(distance=distance,otherPosition=intruse_position)

    def cal_distance(self,pos1,pos2,p=2):
        distance = ((pos1[0] - pos2[0])**p + (pos1[0] - pos2[0])**p + (pos1[0] - pos2[0])**p)**(1/p)
        return distance