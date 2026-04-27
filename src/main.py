from __future__ import annotations

from src.dependencies import get_robot_routine


def main() -> None:
	robot_routine = get_robot_routine()
	robot_routine.start_loop()


if __name__ == "__main__":
	main()

