import airsim
import numpy as np
import cv2

#Start Airsim
client = airsim.MultirotorClient()

#Start Drone
print("Start drone")
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
client.takeoffAsync().join()

#Move drone
print("Move drone")
lateral = 10
frente = 10
cima = -10
velocidade = 5
client.moveToPositionAsync(lateral, frente, cima, velocidade).join()

#get image
print("Get Image RGB")
response = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
response = response[0]
img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
img_rgba = img1d.reshape(response.height, response.width, 3)
print(f"Image size:{response.width}{response.height}")
cv2.imshow("RGB", img_rgba)
cv2.waitKey()

print("Get Depth Vis")
response = client.simGetImages([airsim.ImageRequest(0, airsim.ImageType.DepthVis, True, False)])
print("Image depth ok")
response = response[0]
depth_img_in_meters = airsim.list_to_2d_float_array(response.image_data_float, response.width, response.height)
depth_img_in_meters = depth_img_in_meters.reshape(response.height, response.width, 1)
print(f"Image size:{response.width}{response.height}")
#img1d = airsim.list_to_2d_float_array(response.image_data_float, response.width, response.height)
cv2.imshow("Detph", depth_img_in_meters)
cv2.waitKey()

print("Get Depth Planeer")
response = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthPlanner, True, False)])
print("Image depth ok")
response = response[0]
print(f"len:{len(img1d)}, shape:{img1d.shape}")
depth_img_in_meters = airsim.list_to_2d_float_array(response.image_data_float, response.width, response.height)
depth_img_in_meters = depth_img_in_meters.reshape(response.height, response.width, 1)
#img1d = airsim.list_to_2d_float_array(response.image_data_float, response.width, response.height)
cv2.imshow("Detph", depth_img_in_meters)
cv2.waitKey()

#Off Drone
client.armDisarm(False)
client.reset()
print("Finish")