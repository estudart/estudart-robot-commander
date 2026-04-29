from __future__ import annotations

import json
import threading
from typing import Any

from src.application.routines.patrol import routine_patrol
from src.application.services.logging_service import LoggingService
from src.infrastructure.redis_adapter import RedisAdapter
from src.infrastructure.robot_adapter import RobotAdapter


class RobotWorker:
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
		alert_channel: str = "threat",
		command_channel: str = "robot-command",
	) -> None:
		self._robot = robot_adapter
		self._redis = redis_adapter
		self._logging = logging_service
		self._alert_channel = alert_channel
		self._command_channel = command_channel
		self._thread_lock = threading.Lock()
		self.running = False

	def _handle_command(self, payload: str) -> None:
		raw = str(payload).strip()
		if not raw:
			return

		# JSON movement messages from the WebSocket API
		if raw.startswith("{") and raw.endswith("}"):
			try:
				data = json.loads(raw)
			except json.JSONDecodeError:
				data = None

			if isinstance(data, dict) and str(data.get("type", "")).strip() == "movement":
				direction = str(data.get("direction", "")).strip().lower()
				duration_s = float(data.get("duration_s", 0.5))
				self._logging.info(f"Movement: {direction!r} duration_s={duration_s:.2f}")

				with self._thread_lock:
					if direction == "forward":
						self._robot.move_forward(duration_s)
					if direction == "backward":
						self._robot.move_backward(duration_s)
					elif direction == "left":
						self._robot.turn_left(duration_s)
					elif direction == "right":
						self._robot.turn_right(duration_s)
					elif direction in {"stop", "halt"}:
						self._robot.stop()
					else:
						self._logging.warning(f"Unknown movement direction: {direction!r}")
				return

		cmd = raw.lower()

		if cmd in {"stop", "halt"}:
			with self._thread_lock:
				self._robot.stop()
			return

		self._logging.warning(f"Unknown command: {cmd!r}.")

	def _handle_alert(self, alert: str) -> None:
		evt = str(alert).strip().lower()
		if not evt:
			return

		if evt in {"knife", "gun"}:
			with self._thread_lock:
				self._logging.info("Patrol routine triggered...")
				routine_patrol(robot_adapter=self._robot)
			return

		self._logging.warning(f"Unknown alert: {evt!r}.")

	def _consume_commands(self) -> None:
		for message in self._redis.consume(self._command_channel):
			if not self.running:
				return
			try:
				self._handle_command(str(message))
			except Exception as exc:  # keep loop alive on test/stub
				self._logging.error("Error while handling robot command", exc=exc)

	def _consume_alerts(self) -> None:
		for message in self._redis.consume(self._alert_channel):
			if not self.running:
				return
			try:
				self._handle_alert(str(message))
			except Exception as exc:  # keep loop alive on test/stub
				self._logging.error("Error while handling robot alert", exc=exc)

	def start_loop(self) -> None:
		self.running = True
		self._robot.connect()

		self._logging.info(
			f"RobotWorker started. Commands={self._command_channel!r} Alerts={self._alert_channel!r}."
		)
		self._logging.info("Waiting for Redis events.")

		threading.Thread(target=self._consume_commands, daemon=True).start()
		threading.Thread(target=self._consume_alerts, daemon=True).start()

		try:
			while self.running:
				threading.Event().wait(0.5)
		except KeyboardInterrupt:
			self._logging.info("KeyboardInterrupt received; stopping.")
		finally:
			self.running = False
			self._robot.stop()
			self._robot.disconnect()

