from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from src.application.services.logging_service import LoggingService
from src.infrastructure.redis_adapter import RedisAdapter


class RobotCommander:
	"""
	WebSocket command handler.

	This service receives commands over WebSocket and dispatches them to Redis.

	- Plain text payloads are published as-is to the command channel.
	- JSON payloads:
	  - {"channel": "movement", "direction": "...", "duration_s": 0.5}
	    -> published as JSON to the command channel
	  - {"command": "..."} -> published to the command channel
	"""

	def __init__(
		self,
		*,
		redis_adapter: RedisAdapter,
		logging_service: LoggingService,
		command_channel: str = "robot-command",
		alert_channel: str = "threat",
	) -> None:
		self._redis_adapter = redis_adapter
		self._logging = logging_service
		self._command_channel = command_channel
		self._alert_channel = alert_channel

	def _handle_plain_command(self, command: str) -> None:
		cmd = command.strip().lower()

		# Route alert events to the alert channel (worker alert thread).
		if cmd in {"knife", "gun"}:
			self._logging.info(f"Alert received: {cmd!r}")
			self._redis_adapter.publish(channel=self._alert_channel, message=cmd)
			return

		self._logging.info(f"Command received: {cmd!r}")
		# Otherwise publish as a robot command.
		self._redis_adapter.publish(channel=self._command_channel, message=cmd)

	def _handle_movement(self, payload: dict[str, Any]) -> None:
		direction = str(payload.get("direction", "")).strip().lower()
		duration_s = float(payload.get("duration_s", 0.5))

		self._logging.info(f"Movement command: direction={direction!r} duration_s={duration_s:.2f}")

		message = json.dumps(
			{
				"type": "movement",
				"direction": direction,
				"duration_s": duration_s,
			}
		)
		self._redis_adapter.publish(channel=self._command_channel, message=message)

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