from __future__ import annotations

import argparse
import asyncio
import itertools
import json
from urllib.parse import urlencode
from typing import Iterable


def _parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Connect to /v1/ws/publish and send commands every N seconds."
	)
	parser.add_argument("--host", default="127.0.0.1")
	parser.add_argument("--port", type=int, default=8000)
	parser.add_argument("--path", default="/v1/ws/publish")
	parser.add_argument("--command-channel", default="robot-command")
	parser.add_argument("--alert-channel", default="threat")
	parser.add_argument(
		"--mode",
		choices=["command", "alert"],
		default="command",
		help="Send only command messages or only alert messages (single channel per run).",
	)
	parser.add_argument("--interval", type=float, default=10.0)
	parser.add_argument(
		"--commands",
		default="stop",
		help="Comma-separated commands to cycle through.",
	)
	return parser.parse_args()


def _split_commands(raw: str) -> list[str]:
	return [c.strip() for c in raw.split(",") if c.strip()]


async def _run(
	url: str,
	*,
	interval_s: float,
	commands: Iterable[str],
	command_channel: str,
	alert_channel: str,
	mode: str,
) -> None:
	# Dependency note: `pip install websockets`
	import websockets  # type: ignore

	async with websockets.connect(url) as ws:
		for cmd in itertools.cycle(commands):
			# Send JSON payload with explicit channel.
			c = str(cmd).strip().lower()
			# IMPORTANT: the server requires an explicit channel on every message.
			# This test sends to a single channel per run (mode).
			channel = alert_channel if mode == "alert" else command_channel
			payload = json.dumps({"channel": channel, "command": c})
			await ws.send(payload)
			print(f"sent: {payload} -> {url}")
			await asyncio.sleep(interval_s)


def main() -> None:
	args = _parse_args()
	commands = _split_commands(args.commands)
	if not commands:
		raise SystemExit("No commands provided.")

	url = f"ws://{args.host}:{args.port}{args.path}"
	asyncio.run(
		_run(
			url,
			interval_s=float(args.interval),
			commands=commands,
			command_channel=args.command_channel,
			alert_channel=args.alert_channel,
			mode=args.mode,
		)
	)


if __name__ == "__main__":
	main()

