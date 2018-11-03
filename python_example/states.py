import math
import time
from util import *
from rlbot.agents.base_agent import SimpleControllerState

class BallChaseState: # Chase state paired with chase_controller
    def __init__(self):
        self.expired = False

    def execute(self, agent):
        target_location = agent.ball
        target_speed = velocity2D(agent.ball) + (distance2D(agent.ball, agent.car)/1.5)

        return agent.controller(agent, target_location, target_speed)

def chase_controller(agent, target_object, target_speed): #note target location is an obj
    location = toLocal(target_object, agent.car)
    controller_state = SimpleControllerState()
    angle_to_ball = math.atan2(location.data[1], location.data[0])
    current_speed = velocity2D(agent.car)
    ball_path = agent.get_ball_prediction_struct() #next 6 seconds of ball's path
    print(bal_path[1])

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
        if target_speed > 1400 and agent.start > 2.2 and current_speed < 2250:
            controller_state.boost = True
    elif target_speed < current_speed:
        controller_state.throttle = 0

        #techniquing
    time_diff = time.time() - agent.start #time since last technique
    if time_diff > 2.2 and distance2D(target_object.location, agent.car.location) > 1000 and abs(angle_to_ball) < 1.3:
        agent.start = time.time()
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



class TakeShotState: #Shooting state paired with shot_controller
    def __init__(self):
        self.expired = False

    def execute(self, agent):
        agent.controller = shot_controller
        left_post = Vector3D([sign(agent.team)*GOAL_WIDTH/2,-sign(agent.team)*FIELD_LENGTH/2,100])
        right_post = Vector3D([-sign(agent.team)*GOAL_WIDTH/2,-sign(agent.team)*FIELD_LENGTH/2,100])

        ball_left = angle2D(agent.ball.location,left_post)
        ball_right = angle2D(agent.ball.location,right_post)

        our_left = angle2D(agent.car.location,left_post)
        our_right = angle2D( agent.car.location,right_post)

        target_speed = 1399

        if our_left <= ball_left and our_right >= ball_right:
            target_location = toLocation(agent.ball)
        elif our_left > ball_left and our_right >= ball_right: #ball is too far right
            target_location = toLocation([agent.ball.location.data[0],agent.ball.location.data[1]+sign(agent.team)*160,agent.ball.location.data[2]])
        elif our_right < ball_right and our_left <= ball_left: #ball is too far left
            target_location = toLocation([agent.ball.location.data[0],agent.ball.location.data[1]+sign(agent.team)*160,agent.ball.location.data[2]])
        else:
            target_location = toLocation([0,sign(agent.team)*FIELD_LENGTH/2,100])

        return agent.controller(agent,target_location, target_speed)

def shot_controller(agent, target_object, target_speed): #note target location is an obj
    local_goal_location = toLocal([0, FIELD_LENGTH/2, 100], agent.car)
    goal_angle = math.atan2(local_goal_location.data[1], local_goal_location.data[0])

    location = toLocal(target_object, agent.car)
    controller_state = SimpleControllerState()
    angle_to_target = math.atan2(location.data[1], location.data[0])
    current_speed = velocity2D(agent.car)

        #to steer
    if angle_to_target > 0.1:
        controller_state.steer = controller_state.yaw = 1
    elif angle_to_target < -0.1:
        controller_state.steer = controller_state.yaw = -1
    else:
        controller_state.steer = controller_state.yaw = 0

        #adjust speed
    if target_speed > current_speed:
        controller_state.throttle = 1.0
        if target_speed > 1400 and agent.start > 2.2 and current_speed < 2250:
            controller_state.boost = True
    elif target_speed < current_speed:
        controller_state.throttle = 0

        #techniquing
    time_diff = time.time() - agent.start #time since last technique
    if time_diff > 2.2 and distance2D(target_object, agent.car) > 270:
        agent.start = time.time()
    elif time_diff <= 0.1:
        controller_state.jump = True
        controller_state.pitch = -1
    elif time_diff >= 0.1 and time_diff <= 0.15:
        controller_state.jump = False
        controller_state.pitch = -1
    elif time_diff > 0.15 and time_diff < 1:
        controller_state.jump = True
        controller_state.yaw = math.sin(goal_angle)
        controller_state.pitch = -abs(math.cos(goal_angle))

    return controller_state

class TameState: # does nothing
        def __init__(self):
            self.expired = False
        def execute(self, agent):
            controller_state = SimpleControllerState()
            controller_state.throttle = 0
            return controller_state

class TenderState: # tending goal
    def __init__(self):
        self.expired = False

    def execute(self, agent):
        agent.controller = tender_controller
        # target_location = agent.ball
        # target_speed = velocity2D(agent.ball) + (distance2D(agent.ball, agent.car)/1.5)

        return agent.controller(agent)

def tender_controller(agent):

    # location = toLocal(target_object, agent.car)
    controller_state = SimpleControllerState()
    # angle_to_ball = math.atan2(location.data[1], location.data[0])
    # current_speed = velocity2D(agent.car)
    ball_path = agent.get_ball_prediction_struct()
    on_goal = None
    for i in ball_path.slices:
        if ball_touching_own_goal_line(agent, i.physics.location.x, i.physics.location.y):
            on_goal = [i.physics.location.x, i.physics.location.y]
            break
    if on_goal:
        go_to_spot(agent, on_goal[0], on_goal[1], controller_state)
    else:
        go_to_and_face(agent, -GOAL_WIDTH/2 + 240, sign(agent.team)*FIELD_LENGTH/2, GOAL_WIDTH/2, sign(agent.team)*FIELD_LENGTH/2, controller_state)

    return controller_state
