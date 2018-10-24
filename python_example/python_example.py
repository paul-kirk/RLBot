import math
import time
from util import *
from states import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket



class PythonExample(BaseAgent):
    def initialize_agent(self):
        self.car = GameObject()
        self.ball = GameObject()
        self.start = time.time()

        self.state = TenderState()
        self.controller = shot_controller

    def get_output(self, game: GameTickPacket) -> SimpleControllerState:
        self.preprocess(game)
        self.game = game
        bp = self.get_ball_prediction_struct()

        ball_path = self.get_ball_prediction_struct() #next 6 seconds of ball's path
        # print('--------------')
        # print(ball_path.slices[1].physics.location.x)
        # print(ball_path.slices[1].game_seconds)
        # print(game.game_info.seconds_elapsed)
        # print(ball_touching_own_goal_line(self, self.ball.location.data[0], self.ball.location.data[1]))
        # print('--------------')
        return self.state.execute(self)

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

        self.ball.local_location = to_local(self.ball, self.car)
