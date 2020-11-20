import math

def calc_plane_position(angle,radius,collision_point):
    plane_angle = abs(90 - angle)
    plane_x =  math.sin(math.radians(angle))/math.sin(90) * radius
    plane_y = math.sin(math.radians(plane_angle))/math.sin(90) * radius
    plane_position = [collision_point[0] - plane_x,collision_point[1] - plane_y, collision_point[2]-30]
    plane_rotator = [0,plane_angle,0]
    return plane_position,plane_rotator

