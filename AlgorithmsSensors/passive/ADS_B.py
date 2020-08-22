import airsim  # pip install airsim
from AlgorithmsSensors.AlgorithmSensor import AlgorithmSensor
from AlgorithmsSensors.IMU import InertialSensors
from Control.DetectionData import DetectionData
import time

class ADS_B(AlgorithmSensor):
    name = "ADS_B Base"

    def __init__(self,detectRoot,
                 file_path='E:/Trabalho/Unreal_Projects/share_data/',
                 file_name='log_voo_13_8_2020.txt'):
        print('Start',self.name)
        AlgorithmSensor.__init__(self, detectRoot)
        self.file_path = file_path
        self.file_name = file_name

    def run(self):
        while True:
            self.detect()
            time.sleep(0.5)

    def getData(self,to_str=True):
        file_adsb = open(f'{self.file_path}{self.file_name}', 'r')
        data_adsb = file_adsb.readlines()
        file_adsb.close()
        last_adsb = data_adsb[-1]
        adsb_header = ["icao24","callsign","origin_country","time_position","x_position","y_position",
             "barometric_altitude","on_ground","velocidade","heading","vertical_rate",
             "geo_altitude","squawk","spi","position_source"]
        dict_data = dict(zip(adsb_header,last_adsb.split(',')))
        return dict_data

    def detect(self,min_distance=300):
        #get intruse position
        intruse_data = self.getData()
        intruse_position = (intruse_data['x_position'], intruse_data['y_position'], intruse_data['geo_altitude'])
        my_position = vars(self.client.simGetGroundTruthKinematics().position)
        #calc distance
        x_distance = abs(float(intruse_data['x_position']) - my_position['x_val'])
        y_distance = abs(float(intruse_data['y_position']) - my_position['y_val'])
        z_distance = abs(float(intruse_data['geo_altitude']) - my_position['z_val'])

        distanceMin = min([x_distance,y_distance,z_distance])
        #send detect data
        self.detectData = DetectionData(distance=distanceMin,otherPosition=intruse_position)

