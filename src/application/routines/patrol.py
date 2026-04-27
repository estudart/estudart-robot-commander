from __future__ import annotations
import time

from src.infrastructure.robot_adapter import RobotAdapter


def routine_patrol(*, robot_adapter: RobotAdapter) -> None:
	robot_adapter.beep(0.1)
	robot_adapter.move_forward(1.0)
	robot_adapter.turn_left(0.6)
	robot_adapter.move_forward(1.0)
	robot_adapter.turn_right(0.6)
	robot_adapter.stop()

