"""Ollama LLM Provider — Local LLM."""

import logging

import httpx

from src.application.interfaces.llm import ILLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(ILLMProvider):
    """Ollama local LLM provider."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    async def generate_plan(self, prompt: str) -> LLMResponse:
        """Reja generatsiya qilish."""
        system = (
            "Sen discipline coach'isan. Foydalanuvchiga reja tuzishda yordam ber. "
            "Javobni faqat JSON formatda ber."
        )
        return await self._call_api(prompt, system)

    async def analyze_progress(self, prompt: str) -> LLMResponse:
        """Progress tahlili."""
        system = (
            "Sen data analyst'san. Foydalanuvchining progressini tahlil qil. "
            "Aniq va foydali maslahatlar ber."
        )
        return await self._call_api(prompt, system)

    async def chat(self, prompt: str, system: str = "") -> LLMResponse:
        """Umumiy suhbat."""
        if not system:
            system = "Sen foydali AI yordamchisan."
        return await self._call_api(prompt, system)

    async def _call_api(self, prompt: str, system: str) -> LLMResponse:
        """Ollama API chaqiruvi."""
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=120)
            response.raise_for_status()

        data = response.json()
        content = data["message"]["content"]

        tokens_used = data.get("eval_count", 0) + data.get("prompt_eval_count", 0)

        logger.info(f"Ollama: {tokens_used} tokens (local, bepul)")

        return LLMResponse(
            content=content,
            model=self.model,
            tokens_used=tokens_used,
            cost_usd=0.0,
        )
