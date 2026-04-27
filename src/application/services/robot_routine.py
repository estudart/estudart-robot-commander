from __future__ import annotations

import threading
from typing import Optional

from src.application.routines.patrol import routine_patrol
from src.application.services.logging_service import LoggingService
from src.infrastructure.redis_adapter import RedisAdapter
from src.infrastructure.robot_adapter import RobotAdapter


class RobotRoutine:
	"""
	Simple loop for a Raspberry Pi robot controller.

	Listens for Redis commands and runs routines. This intentionally keeps the
	robot logic behind `RobotAdapter` so hardware can be swapped later.
	"""

	def __init__(
		self,
		*,
		robot_adapter: RobotAdapter,
		redis_adapter: RedisAdapter,
		logging_service: LoggingService,
		command_channel: str = "threat",
	) -> None:
		self._robot = robot_adapter
		self._redis = redis_adapter
		self._logging = logging_service
		self._command_channel = command_channel
		self.running = False

	def _handle_command(self, command: str) -> None:
		cmd = command.strip().lower()
		self._logging.info(f"Command received: {cmd!r}")

		if cmd in {"stop", "halt"}:
			self._robot.stop()
			return

		if cmd in {"knife", "gun"}:
			routine_patrol(robot_adapter=self._robot)
			return

		self._logging.warning(f"Unknown command: {cmd!r}. Try 'patrol' or 'stop'.")

	def _consume_commands(self) -> None:
		for message in self._redis.consume(self._command_channel):
			if not self.running:
				return
			try:
				self._handle_command(str(message))
			except Exception as exc:  # keep loop alive on test/stub
				self._logging.error("Error while handling robot command", exc=exc)

	def start_loop(self) -> None:
		self.running = True
		self._robot.connect()

		self._logging.info(
			f"RobotRoutine started. Listening on Redis channel {self._command_channel!r}."
		)
		self._logging.info("Try: publish 'knife' or 'gun'.")

		threading.Thread(target=self._consume_commands, daemon=True).start()

		try:
			# Keep main thread alive; actual work happens in the consumer thread.
			while self.running:
				threading.Event().wait(0.5)
		except KeyboardInterrupt:
			self._logging.info("KeyboardInterrupt received; stopping.")
		finally:
			self.running = False
			self._robot.stop()
			self._robot.disconnect()

