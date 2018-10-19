import math
import time

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

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

class BallChaseState: #simple example state
    def __init__(self):
        self.expired = False

    def execute(self, agent):
        target_location = agent.ball
        target_speed = velocity2D(agent.ball) + (distance2D(agent.ball, agent.car)/1.5)

        return agent.controller_set(target_location, target_speed)

class PythonExample(BaseAgent):
    def initialize_agent(self):
        self.car = GameObject()
        self.ball = GameObject()
        self.start = time.time()

        self.state = BallChaseState()

    def get_output(self, game: GameTickPacket) -> SimpleControllerState:
        self.controller_state = SimpleControllerState()
        self.preprocess(game)

        # self.controller_state.throttle = 1.0
        # self.controller_state.steer = 0.14
        # self.controller_state.boost = True

        return self.state.execute(self)

    def controller_set(self, target_object, target_speed): #note target location is an obj
        location = target_object.local_location
        controller_state = SimpleControllerState()
        angle_to_ball = math.atan2(location.data[1], location.data[0])
        current_speed = velocity2D(self.car)

            #to steer
        if angle_to_ball > 0.1:
            controller_state.steer = controller_state.yaw = 1
        elif angle_to_ball < -0.1:
            controller_state.steer = controller_state.yaw = -1
        else:
            controller_state.steer = controller_state.yaw = 0

            #adjust speed
        if target_speed > current_speed:
            controller_state.throttle = 1.0
            if target_speed > 1400 and self.start > 2.2 and current_speed < 2250:
                controller_state.boost = True
        elif target_speed < current_speed:
            controller_state.throttle = 0

            #techniquing
        time_diff = time.time() - self.start #time since last technique
        if time_diff > 2.2 and distance2D(target_object.location, self.car.location) > 1000 and abs(angle_to_ball) < 1.3:
            self.start = time.time()
        elif time_diff <= 0.1:
            controller_state.jump = True
            controller_state.pitch = -1
        elif time_diff >= 0.1 and time_diff <= 0.15:
            controller_state.jump = False
        elif time_diff > 0.15 and time_diff < 1:
            controller_state.jump = True
            controller_state.yaw = controller_state.steer
            controller_state.pitch = -1

        return controller_state


    def preprocess(self, game):
        self.car.location.data = [game.game_cars[self.index].physics.location.x, game.game_cars[self.index].physics.location.y, game.game_cars[self.index].physics.location.z]
        self.car.velocity.data = [game.game_cars[self.index].physics.velocity.x, game.game_cars[self.index].physics.velocity.y, game.game_cars[self.index].physics.velocity.z]
        self.car.rotation.data = [game.game_cars[self.index].physics.rotation.pitch, game.game_cars[self.index].physics.rotation.yaw, game.game_cars[self.index].physics.rotation.roll]
        self.car.rotational_velocity.data = [game.game_cars[self.index].physics.angular_velocity.x, game.game_cars[self.index].physics.angular_velocity.y, game.game_cars[self.index].physics.angular_velocity.z]
        self.car.matrix = rotator_to_matrix(self.car)
        self.car.boost = game.game_cars[self.index].boost

        self.ball.location.data = [game.game_ball.physics.location.x, game.game_ball.physics.location.y, game.game_ball.physics.location.z]
        self.ball.velocity.data = [game.game_ball.physics.velocity.x, game.game_ball.physics.velocity.y, game.game_ball.physics.velocity.z]
        self.ball.rotation.data = [game.game_ball.physics.rotation.pitch, game.game_ball.physics.rotation.yaw, game.game_ball.physics.rotation.roll]
        self.ball.rotational_velocity.data = [game.game_ball.physics.angular_velocity.x, game.game_ball.physics.angular_velocity.y, game.game_ball.physics.angular_velocity.z]

        self.ball.local_location.data = to_local(self.ball, self.car)


def to_local(target_object, our_object):
    x = (target_object.location - our_object.location) * our_object.matrix[0]
    y = (target_object.location - our_object.location) * our_object.matrix[1]
    z = (target_object.location - our_object.location) * our_object.matrix[2]
    return [x,y,z]

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

def velocity2D(target_object):
    return math.sqrt(target_object.velocity.data[0]**2 + target_object.velocity.data[1]**2)

def distance2D(target_object, our_object):
    if isinstance(target_object,Vector3D): #allows input if obj or a raw vector
        difference = target_object - our_object
    else:
        difference = target_object.location - our_object.location
    return math.sqrt(difference.data[0]**2 + difference.data[1]**2)
