import math

def calc_plane_position(angle,collision_point,time_to_colision,velocity):
    radius = (time_to_colision+1) * velocity
    plane_angle = abs(180 + angle)
    #plane_x =  math.sin(math.radians(angle))/math.sin(90) * radius
    #plane_y = math.sin(math.radians(plane_angle))/math.sin(90) * radius
    plane_x = math.cos(math.radians(plane_angle)) * radius
    plane_y = math.sin(math.radians(plane_angle)) *  radius
    plane_position = [collision_point[0] - plane_x,collision_point[1] - plane_y, collision_point[2]-30]
    plane_rotator = [0,plane_angle,0]
    return plane_position,plane_rotator

