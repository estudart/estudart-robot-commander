from __future__ import annotations

import json
import threading
import time
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
		robot_state_key: str = "robot:state"
	) -> None:
		self._robot = robot_adapter
		self._redis = redis_adapter
		self._logging = logging_service
		self._alert_channel = alert_channel
		self._thread_lock = threading.Lock()
		self.running = False
		self._robot_state_key = robot_state_key

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
				steps = int(data.get("steps", 1))
				speed = float(data.get("speed", 0.5))
				self._logging.info(f"Movement: {direction!r} steps={steps} speed={speed:.2f}")

				with self._thread_lock:
					if direction == "forward":
						self._robot.move_forward(steps, speed)
					elif direction == "backward":
						self._robot.move_backward(steps, speed)
					elif direction == "left":
						self._robot.turn_left(steps, speed)
					elif direction == "right":
						self._robot.turn_right(steps, speed)
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
		while True:
			current_state = self._redis.get_key(self._robot_state_key)
			if not self.running:
				return
			try:
				self._handle_command(str(current_state))
			except Exception as exc:  # keep loop alive on test/stub
				self._logging.error("Error while handling robot command", exc=exc)
			time.sleep(0.3)

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
		self._redis.set_key(self._robot_state_key, "stop")
		self._robot.connect()

		self._logging.info(
			f"RobotWorker started. Alerts={self._alert_channel!r}."
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

