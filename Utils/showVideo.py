from threading import Thread
import numpy as np
import airsim
import cv2

class Video(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.cliente = airsim.MultirotorClient()

    def run(self):
        while True:
            response = self.cliente.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
            response = response[0]
            # get numpy array
            img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
            # reshape array to 4 channel image array H X W X 4
            img_rgba = img1d.reshape(response.height, response.width, 4)
            cv2.putText(img_rgba, "FPS : " , (100, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);
            cv2.imshow("Video",img_rgba)
            cv2.waitKey(1)


