from __pycache__/util import *

class TenderState: # tending goal
    def __init__(self):
        self.expired = False

    def execute(self, agent):
        # target_location = agent.ball
        # target_speed = velocity2D(agent.ball) + (distance2D(agent.ball, agent.car)/1.5)

        return agent.controller(agent, target_location, target_speed)

def tender_controller(agent, target_object, target_speed): #note target location is an obj
    location = toLocal(target_object, agent.car)
    controller_state = SimpleControllerState()
    angle_to_ball = math.atan2(location.data[1], location.data[0])
    current_speed = velocity2D(agent.car)
    ball_path = agent.get_ball_prediction_struct() #next 6 seconds of ball's path

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
