import airsim
import time
import random

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
client.takeoffAsync().join()
print("Estavel")
#movendo por caminho
routePoints = [[0,-15,0,4],[15,-15,0,4],[15,-15,-15,4]]
path  = []
for point in routePoints:
    path.append(airsim.Vector3r(point[0],point[1],point[2]))
client.moveOnPathAsync(path,3)
print("Caminho enviado")

num_aleatorio = random.randint(0,10)
time.sleep(num_aleatorio)
routePoints = [[0,15,0,4],[-15,15,0,4],[-15,15,-15,4]]
path  = []
for point in routePoints:
    path.append(airsim.Vector3r(point[0],point[1],point[2]))
print("Trocando caminho")
client.moveOnPathAsync(path,3).join()
#Movendo por direção
'''
client.moveByVelocityZAsync(5,10,0,1).join()
pos = client.simGetGroundTruthKinematics()
while pos.position.y_val < 50:
    print(pos.position.y_val)
    pos = client.simGetGroundTruthKinematics()
    if pos.position.x_val > 10:
        print("Break!")
        break
client.moveByVelocityZAsync(10,0,0,1).join()
'''
'''
# Movendo por pontos

print("Estavel")
client.moveByVelocityAsync(0, -10, 0, 4)
print("Position",client.simGetGroundTruthKinematics())
print("Foi")
client.moveToPosition(10, -15, 0, 4).join()
print("Position",client.simGetGroundTruthKinematics())
print("Foi")
client.moveToPosition(20, -20, -20, 4).join()
print("Position",client.simGetGroundTruthKinematics())
print("Foi")
'''