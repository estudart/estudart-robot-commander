from __future__ import annotations

import time

from src.application.services.logging_service import LoggingService


class RobotAdapter:
	"""
	Hardware abstraction for the robot.

	For now this is a test/stub implementation that only prints/logs actions.
	Replace these methods later with GPIO / serial / ROS / etc.
	"""

	def __init__(self, *, logging_service: LoggingService) -> None:
		self._logging = logging_service
		self._connected = False

	def connect(self) -> None:
		if self._connected:
			self._logging.info("RobotAdapter.connect(): already connected")
			return
		self._connected = True
		self._logging.info("RobotAdapter.connect(): connected (stub)")

	def disconnect(self) -> None:
		if not self._connected:
			self._logging.info("RobotAdapter.disconnect(): already disconnected")
			return
		self._connected = False
		self._logging.info("RobotAdapter.disconnect(): disconnected (stub)")

	def stop(self) -> None:
		self._logging.info("RobotAdapter.stop(): STOP (stub)")

	def beep(self, duration_s: float = 0.2) -> None:
		self._logging.info(f"RobotAdapter.beep(): beep for {duration_s:.2f}s (stub)")
		time.sleep(max(0.0, float(duration_s)))

	def move_forward(self, duration_s: float = 1.0) -> None:
		self._logging.info(f"RobotAdapter.move_forward(): {duration_s:.2f}s (stub)")
		time.sleep(max(0.0, float(duration_s)))

	def move_backward(self, duration_s: float = 1.0) -> None:
		self._logging.info(f"RobotAdapter.move_backward(): {duration_s:.2f}s (stub)")
		time.sleep(max(0.0, float(duration_s)))

	def turn_left(self, duration_s: float = 0.5) -> None:
		self._logging.info(f"RobotAdapter.turn_left(): {duration_s:.2f}s (stub)")
		time.sleep(max(0.0, float(duration_s)))

	def turn_right(self, duration_s: float = 0.5) -> None:
		self._logging.info(f"RobotAdapter.turn_right(): {duration_s:.2f}s (stub)")
		time.sleep(max(0.0, float(duration_s)))

