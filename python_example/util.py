import math

GOAL_WIDTH = 1900
FIELD_LENGTH = 10280
FEILD_WIDTH = 8240

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
