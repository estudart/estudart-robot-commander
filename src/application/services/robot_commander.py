from __future__ import annotations

import json
from datetime import datetime, timezone
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
		robot_state_key: str = "robot:state",
	) -> None:
		self._redis_adapter = redis_adapter
		self._logging = logging_service
		self._command_channel = command_channel
		self._robot_state_key = robot_state_key

	def handle_commands(self, payload: str | dict[str, Any]) -> None:
		"""
		Publish robot commands to the command channel.

		Supports:
		- JSON movement payloads (dict with type=movement or direction present)
		- JSON command payloads (dict with command="stop")
		"""
		if isinstance(payload, dict):
			command_type = str(payload.get("type", "")).strip().lower()
			if command_type == "movement" or "direction" in payload:
				direction = str(payload.get("direction", "")).strip().lower()
				steps = int(payload.get("steps", 1))
				speed = float(payload.get("speed", 0.5))

				self._logging.info(f"Movement command: direction={direction!r} steps={steps} speed={speed:.2f}")

			message = json.dumps(
				{
					"type": "movement",
					"direction": direction,
					"steps": steps,
					"speed": speed,
					"ts": datetime.now(timezone.utc).isoformat(),
				}
			)
			self._redis_adapter.set_key(key=self._robot_state_key, value=message)
			return

			self._logging.info(f"Unknown command: {command_type!r}")

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
						self._logging.error("Invalid JSON payload received; expected a JSON object with 'channel'.")
						continue

					channel = str(payload.get("channel", "")).strip()
					if channel == self._command_channel:
						self.handle_commands(payload)
						continue
					else:
						self._logging.error(f"Unknown channel: {channel!r}")
						continue

				# Plain text payloads are not accepted: require explicit channel.
				self._logging.error(
					"Plain text payload received; expected JSON with 'channel' "
					f"({self._command_channel!r}."
				)
		except WebSocketDisconnect:
			return