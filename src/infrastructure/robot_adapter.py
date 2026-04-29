from __future__ import annotations

from src.application.services.logging_service import LoggingService


class RobotAdapter:
	"""
	Hardware abstraction for the robot.

	For now this is a test/stub implementation that only prints/logs actions.
	Replace these methods later with GPIO / serial / ROS / etc.

	All movement methods share the same signature: (steps, speed).
	  steps — number of steps to execute (default 1)
	  speed — normalised speed 0.0–1.0 (default 0.5)
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

	def beep(self, steps: int = 1, speed: float = 0.5) -> None:
		self._logging.info(f"RobotAdapter.beep(): steps={steps} speed={speed:.2f} (stub)")

	def move_forward(self, steps: int = 1, speed: float = 0.5) -> None:
		self._logging.info(f"RobotAdapter.move_forward(): steps={steps} speed={speed:.2f} (stub)")

	def move_backward(self, steps: int = 1, speed: float = 0.5) -> None:
		self._logging.info(f"RobotAdapter.move_backward(): steps={steps} speed={speed:.2f} (stub)")

	def turn_left(self, steps: int = 1, speed: float = 0.5) -> None:
		self._logging.info(f"RobotAdapter.turn_left(): steps={steps} speed={speed:.2f} (stub)")

	def turn_right(self, steps: int = 1, speed: float = 0.5) -> None:
		self._logging.info(f"RobotAdapter.turn_right(): steps={steps} speed={speed:.2f} (stub)")

