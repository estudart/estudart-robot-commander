from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from src.application.services.logging_service import LoggingService
from src.infrastructure.robot_adapter import RobotAdapter


class RobotCommander:
	"""
	WebSocket command handler.

	This is intentionally simple for now and does NOT use Redis:
	- If a message is plain text, we treat it as a command and execute it immediately.
	- If a message is JSON, we support:
	  - {"channel": "movement", "direction": "...", "duration_s": 0.5} -> call RobotAdapter (stub)
	  - {"command": "..."} -> same as plain text
	"""

	def __init__(
		self,
		*,
		robot_adapter: RobotAdapter,
		logging_service: LoggingService,
	) -> None:
		self._robot = robot_adapter
		self._logging = logging_service

	def _handle_plain_command(self, command: str) -> None:
		cmd = command.strip().lower()
		self._logging.info(f"Command received: {cmd!r}")

		if cmd in {"stop", "halt"}:
			self._robot.stop()
			return
		if cmd in {"beep"}:
			self._robot.beep(0.2)
			return
		if cmd in {"forward", "move_forward"}:
			self._robot.move_forward(1.0)
			return
		if cmd in {"left", "turn_left"}:
			self._robot.turn_left(0.5)
			return
		if cmd in {"right", "turn_right"}:
			self._robot.turn_right(0.5)
			return

		self._logging.warning(
			f"Unknown command: {cmd!r}. Try 'forward', 'left', 'right', 'beep', 'stop'."
		)

	def _handle_movement(self, payload: dict[str, Any]) -> None:
		direction = str(payload.get("direction", "")).strip().lower()
		duration_s = float(payload.get("duration_s", 0.5))

		self._logging.info(f"Movement command: direction={direction!r} duration_s={duration_s:.2f}")

		if direction == "forward":
			self._robot.move_forward(duration_s)
		elif direction == "left":
			self._robot.turn_left(duration_s)
		elif direction == "right":
			self._robot.turn_right(duration_s)
		elif direction == "stop":
			self._robot.stop()
		else:
			self._logging.warning(f"Unknown movement direction: {direction!r}")

	async def handle_socket(self, websocket: WebSocket) -> None:
		try:
			while True:
				text = await websocket.receive_text()
				if text is None:
					continue
				raw = str(text).strip()
				if not raw:
					continue

				# JSON payload support
				if raw.startswith("{") and raw.endswith("}"):
					try:
						payload = json.loads(raw)
					except json.JSONDecodeError:
						self._handle_plain_command(raw)
						continue

					command = payload.get("command")
					if isinstance(command, str) and command.strip():
						self._handle_plain_command(command)
						continue

					channel = str(payload.get("channel", "")).strip()
					if channel == "movement":
						self._handle_movement(payload)
						continue

					self._logging.warning("Unknown JSON payload; expected movement or command.")
					continue

				# Plain text -> execute immediately
				self._handle_plain_command(raw)
		except WebSocketDisconnect:
			return