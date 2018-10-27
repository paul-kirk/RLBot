import math
import time
GOAL_WIDTH = 1900
FIELD_LENGTH = 10280
FIELD_WIDTH = 8240

class Vector3D:
    def __init__(self, data):
        self.data = data
    def __sub__(self, other_vector):
        return Vector3D([self.data[0] - other_vector.data[0], self.data[1] - other_vector.data[1], self.data[2] - other_vector.data[2]])
    def __mul__(self, other_vector):
        return (self.data[0] * other_vector.data[0] + self.data[1] * other_vector.data[1] + self.data[2] * other_vector.data[2])

class GameObject:
    def __init__(self):
        self.location = Vector3D([0,0,0])
        self.velocity = Vector3D([0,0,0])
        self.rotation = Vector3D([0,0,0])
        self.rotational_velocity = Vector3D([0,0,0])

        self.local_location = Vector3D([0,0,0])
        self.boost = 0

def rotator_to_matrix(our_object):
    r = our_object.rotation.data
    CR = math.cos(r[2])
    SR = math.sin(r[2])
    CP = math.cos(r[0])
    SP = math.sin(r[0])
    CY = math.cos(r[1])
    SY = math.sin(r[1])

    matrix = []
    matrix.append(Vector3D([CP*CY, CP*SY, SP]))
    matrix.append(Vector3D([CY*SP*SR-CR*SY, SY*SP*SR+CR*CY, -CP * SR]))
    matrix.append(Vector3D([-CR*CY*SP-SR*SY, -CR*SY*SP+SR*CY, CP*CR]))
    return matrix

def sign(x):
    if x <= 0:
        return -1
    else:
        return 1

def to_local(target, our_obj):
    x = (toLocation(target) - our_obj.location) * our_obj.matrix[0]
    y = (toLocation(target) - our_obj.location) * our_obj.matrix[1]
    z = (toLocation(target) - our_obj.location) * our_obj.matrix[2]
    return Vector3D([x,y,z])

def toLocal(target, obj):
    if isinstance(target, GameObject):
        return target.local_location
    else:
        return to_local(target, obj)

def toLocation(target):
    if isinstance(target, Vector3D):
        return target
    elif isinstance(target, list):
        return(Vector3D(target))
    else:
        return target.location

def velocity2D(target_object):
    return math.sqrt(target_object.velocity.data[0]**2 + target_object.velocity.data[1]**2)

def angle2D(obj1, obj2):
    difference = toLocation(obj1) - toLocation(obj2)
    return math.atan2(difference.data[1], difference.data[0])

def distance2D(obj1, obj2):
    difference = toLocation(obj1) - toLocation(obj2)
    return math.sqrt(difference.data[0]**2 + difference.data[1]**2)

# def aim(agent, target_x, target_y):
#     powerslide_angle = math.radians(170)
#     angle_between_bot_and_target = math.atan2(target_y - agent.bot_pos.y,
#                                             target_x - agent.bot_pos.x)
#
#     angle_front_to_target = angle_between_bot_and_target - agent.bot_yaw
#
#     # Correct the values
#     if angle_front_to_target < -math.pi:
#         angle_front_to_target += 2 * math.pi
#     if angle_front_to_target > math.pi:
#         angle_front_to_target -= 2 * math.pi
#
#     if angle_front_to_target < math.radians(-10):
#         # If the target is more than 10 degrees right from the centre, steer left
#         agent.controller.steer = -1
#     elif angle_front_to_target > math.radians(10):
#         # If the target is more than 10 degrees left from the centre, steer right
#         agent.controller.steer = 1
#     else:
#         # If the target is less than 10 degrees from the centre, steer straight
#         agent.controller.steer = 0
#
#     agent.controller.handbrake = abs(math.degrees(angle_front_to_target)) < powerslide_angle
#
# def be_at_spot(agent, x, y, arrival_time, controller):
#     distance = math.hypot((agent.car.location.data[0] - x), (agent.car.location.data[1] - y))
#     time_remaining = arrival_time - agent.game.game_info.seconds_elapsed
#     speed = math.hypot(agent.car.velocity.data[0], agent.car.velocity.data[1])
#     aim(agent, x, y)
#
#     if speed > distance/time:
#         controller.throttle = 0
#     else:
#         controller.throttle = 1


def aim(agent, target_x, target_y, controller):
    # print('aim')
    powerslide_angle = math.radians(170)
    angle_between_bot_and_target = math.atan2(target_y - agent.car.location.data[1],
                                            target_x - agent.car.location.data[0])

    angle_front_to_target = angle_between_bot_and_target - agent.car.rotation.data[1]

    # Correct the values
    if angle_front_to_target < -math.pi:
        angle_front_to_target += 2 * math.pi
    if angle_front_to_target > math.pi:
        angle_front_to_target -= 2 * math.pi

    if angle_front_to_target < math.radians(-10):
        # If the target is more than 10 degrees right from the centre, steer left
        controller.steer = -1
    elif angle_front_to_target > math.radians(10):
        # If the target is more than 10 degrees left from the centre, steer right
        controller.steer = 1
    else:
        # If the target is less than 10 degrees from the centre, steer straight
        controller.steer = 0

    controller.handbrake = abs(math.degrees(angle_front_to_target)) < powerslide_angle

def be_at_spot_on_time(agent, x, y, arrival_time, controller):
    distance = math.hypot((agent.car.location.data[0] - x), (agent.car.location.data[1] - y))
    time_remaining = arrival_time - agent.game.game_info.seconds_elapsed
    speed = math.hypot(agent.car.velocity.data[0], agent.car.velocity.data[1])
    aim(agent, x, y, controller)

    if speed > distance/time:
        controller.throttle = -1
    else:
        controller.throttle = 1

def go_to_spot(agent, x, y, controller):
    x_match = abs(x - agent.car.location.data[0]) < 80
    y_match = abs(y - agent.car.location.data[1]) < 80
    net_vel = math.hypot(agent.car.velocity.data[0], agent.car.velocity.data[1])
    local_spot = toLocal([x, y, 0], agent.car)
    if x_match and y_match and net_vel < 500:
        controller.throttle = 0
    elif local_spot.data[0] > 0:
        aim(agent, x, y, controller)
        controller.throttle = 1
    elif local_spot.data[0] < 0:
        controller.throttle = -1

def face_direction_of(agent, x, y, controller):
    local_spot = toLocal([x, y, 0], agent.car)
    angle_to_target = math.atan2(local_spot.data[1], local_spot.data[0])
    if angle_to_target > 0.1 or angle_to_target < -0.1:
        controller.jump = True
        aim(agent, x, y, controller)
        
def ball_touching_own_goal_line(agent, x, y):
    if (x < -GOAL_WIDTH/2) or (x > GOAL_WIDTH/2):
        return False
    elif agent.team == 0 and y > -FIELD_LENGTH/2:
        return False
    elif agent.team == 1 and y < FIELD_LENGTH/2:
        return False
    else:
        return True
