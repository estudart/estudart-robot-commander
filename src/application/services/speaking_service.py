from __future__ import annotations
import time

from src.application.services.logging_service import LoggingService
from src.infrastructure.speaking_adapter import SpeakingAdapter


class SpeakingService:
	"""Application-level text-to-speech service with logging."""

	def __init__(
		self,
		*,
		speaking_adapter: SpeakingAdapter,
		logging_service: LoggingService,
	) -> None:
		self._adapter = speaking_adapter
		self._logging = logging_service

	def text_to_voice(self, text: str) -> None:
		if not self._adapter.is_available():
			self._logging.info(f"[TTS disabled] {text}")
			return
		try:
			self._adapter.text_to_voice(text)
		except Exception as exc:
			self._logging.error("TTS failed; continuing without speech", exc=exc)

