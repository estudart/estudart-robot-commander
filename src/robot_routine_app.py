from __future__ import annotations

from src.presentation.dependencies import get_robot_routine


if __name__ == "__main__":
	robot_routine = get_robot_routine()
	robot_routine.start_loop()

