"""LLM provider interface. The demo path must run on NVIDIA Nemotron via
Meterless (sponsor requirement); the local provider exists for offline
development and tests only."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, system: str, user: str, max_tokens: int = 800) -> LLMResponse:
        """Single reasoning call. Raises on transport/model failure."""
        raise NotImplementedError
