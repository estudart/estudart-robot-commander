from __future__ import annotations

import pyttsx3


class SpeakingAdapter:
	"""Infrastructure adapter around text-to-speech (pyttsx3)."""

	def __init__(self) -> None:
		self._engine = pyttsx3.init()
		self._start_config()

	def is_available(self) -> bool:
		return True

	def _start_config(self) -> None:
		# Tune defaults once at startup.
		self._engine.setProperty("rate", 150)
		self._engine.setProperty("volume", 0.9)

	def text_to_voice(self, text: str) -> None:
		self._engine.say(str(text))
		self._engine.runAndWait()
