# Rocket League Bot

## Description

A build of the AI bot in the popular game Rocket League coded in Python.

## Features

```
on_goal = None
  for i in ball_path.slices:
      if ball_touching_own_goal_line(agent, i.physics.location.x, i.physics.location.y):
          on_goal = [i.physics.location.x, i.physics.location.y]
          break
  if on_goal:
      go_to_spot(agent, on_goal[0], on_goal[1], controller_state)
  else:
      go_to_and_face(agent, -GOAL_WIDTH/2 + 240, sign(agent.team)*FIELD_LENGTH/2, GOAL_WIDTH/2, sign(agent.team)*FIELD_LENGTH/2, controller_state)
  ```
This snippet controls part of the goal tender. If the ball is on goal, the car will move to stop the ball. Otherwise, the car will position itself for optimal goal coverage should a shot be placed on goal.
