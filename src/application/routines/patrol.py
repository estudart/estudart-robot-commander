from __future__ import annotations
import time

from src.infrastructure.robot_adapter import RobotAdapter


def routine_patrol(*, robot_adapter: RobotAdapter) -> None:
	robot_adapter.beep()
	robot_adapter.move_forward(steps=2)
	robot_adapter.turn_left(steps=1)
	robot_adapter.move_forward(steps=2)
	robot_adapter.turn_right(steps=1)
	robot_adapter.stop()

