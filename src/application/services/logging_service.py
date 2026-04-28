from __future__ import annotations

import logging
from typing import Optional


class LoggingService:
	"""Small wrapper around Python logging for consistent app output."""

	def __init__(self, name: str = "RobotCommander", level: int = logging.INFO) -> None:
		self._logger = logging.getLogger(name)
		self._logger.setLevel(level)

		if not self._logger.handlers:
			handler = logging.StreamHandler()
			formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
			handler.setFormatter(formatter)
			self._logger.addHandler(handler)

		# Avoid duplicate logs if root logger is configured elsewhere.
		self._logger.propagate = False

	def debug(self, message: str) -> None:
		self._logger.debug(message)

	def info(self, message: str) -> None:
		self._logger.info(message)

	def warning(self, message: str) -> None:
		self._logger.warning(message)

	def error(self, message: str, exc: Optional[BaseException] = None) -> None:
		if exc is not None:
			self._logger.error(f"{message} ({exc})")
		else:
			self._logger.error(message)

