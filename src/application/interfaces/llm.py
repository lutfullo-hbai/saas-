"""LLM Provider interface — Domain Layer."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM javobi."""

    content: str
    model: str
    tokens_used: int
    cost_usd: float


class ILLMProvider(ABC):
    """LLM provider abstraktsiyasi.

    Har qanday LLM (Claude, Ollama, GPT) uchun umumiy interfeys.
    """

    @abstractmethod
    async def generate_plan(self, prompt: str) -> LLMResponse:
        """Reja generatsiya qilish."""
        ...

    @abstractmethod
    async def analyze_progress(self, prompt: str) -> LLMResponse:
        """Progress tahlili."""
        ...

    @abstractmethod
    async def chat(self, prompt: str, system: str = "") -> LLMResponse:
        """Umumiy suhbat."""
        ...
