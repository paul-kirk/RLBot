from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math
import time


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class TutorialBot(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()

        # Contants
        self.DODGE_TIME = 0.2
        self.DISTANCE_TO_DODGE = 500
        self.DISTANCE_FROM_BALL_TO_BOOST = 1500  # The minimum distance the ball needs to be away from the bot for the bot to boost
        # The angle (from the front of the bot to the ball) at which the bot should start to powerslide.
        self.POWERSLIDE_ANGLE = math.radians(170)

        # Game values
        self.bot_pos = None
        self.bot_yaw = None

        # Dodging
        self.should_dodge = False
        self.on_second_jump = False
        self.next_dodge_time = 0

    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.atan2(target_y - self.bot_pos.y,
                                                target_x - self.bot_pos.x)

        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw

        # Correct the values
        if angle_front_to_target < -math.pi:
            angle_front_to_target += 2 * math.pi
        if angle_front_to_target > math.pi:
            angle_front_to_target -= 2 * math.pi

        if angle_front_to_target < math.radians(-10):
            # If the target is more than 10 degrees right from the centre, steer left
            self.controller.steer = -1
        elif angle_front_to_target > math.radians(10):
            # If the target is more than 10 degrees left from the centre, steer right
            self.controller.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.controller.steer = 0

        self.controller.handbrake = abs(math.degrees(angle_front_to_target)) < self.POWERSLIDE_ANGLE

    def check_for_dodge(self):
        if self.should_dodge and time.time() > self.next_dodge_time:
            self.controller.jump = True
            self.controller.pitch = -1

            if self.on_second_jump:
                self.on_second_jump = False
                self.should_dodge = False
            else:
                self.on_second_jump = True
                self.next_dodge_time = time.time() + self.DODGE_TIME

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location
        ball_pos = packet.game_ball.physics.location

        # Boost when ball is far enough away
        self.controller.boost = distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) > self.DISTANCE_FROM_BALL_TO_BOOST

        # Blue has their goal at -5000 (Y axis) and orange has their goal at 5000 (Y axis). This means that:
        # - Blue is behind the ball if the ball's Y axis is greater than blue's Y axis
        # - Orange is behind the ball if the ball's Y axis is smaller than orange's Y axis
        self.controller.throttle = 1

        if (self.index == 0 and self.bot_pos.y < ball_pos.y) or (self.index == 1 and self.bot_pos.y > ball_pos.y):
            self.aim(ball_pos.x, ball_pos.y)
            if distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) < self.DISTANCE_TO_DODGE:
                self.should_dodge = True
        else:
            if self.team == 0:
                # Blue team's goal is located at (0, -5000)
                self.aim(0, -5000)
            else:
                # Orange team's goal is located at (0, 5000)
                self.aim(0, 5000)

        # Boost on kickoff
        if ball_pos.x == 0 and ball_pos.x == 0:
            self.aim(ball_pos.x, ball_pos.x)
            self.controller.boost = True

        # This sets self.jump to be active for only 1 frame
        self.controller.jump = 0

        self.check_for_dodge()

        return self.controller