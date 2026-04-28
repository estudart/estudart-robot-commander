from __future__ import annotations

from src.presentation.dependencies import get_robot_worker


def main() -> None:
	robot_worker = get_robot_worker()
	robot_worker.start_loop()


if __name__ == "__main__":
	main()

