"""Claude LLM Provider — Anthropic API."""

import logging

import httpx

from src.application.interfaces.llm import ILLMProvider, LLMResponse

logger = logging.getLogger(__name__)

# Narxlar (Claude 3.5 Sonnet)
INPUT_COST_PER_1K = 0.003
OUTPUT_COST_PER_1K = 0.015


class ClaudeProvider(ILLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"

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
        """Anthropic API chaqiruvi."""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url, json=payload, headers=headers, timeout=60
            )
            response.raise_for_status()

        data = response.json()
        content = data["content"][0]["text"]
        tokens_used = data["usage"]["input_tokens"] + data["usage"]["output_tokens"]

        cost = self._calculate_cost(
            input_tokens=data["usage"]["input_tokens"],
            output_tokens=data["usage"]["output_tokens"],
        )

        logger.info(
            f"Claude API: {tokens_used} tokens, ${cost:.4f}"
        )

        return LLMResponse(
            content=content,
            model=self.model,
            tokens_used=tokens_used,
            cost_usd=cost,
        )

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Xarajatni hisoblash."""
        input_cost = (input_tokens / 1000) * INPUT_COST_PER_1K
        output_cost = (output_tokens / 1000) * OUTPUT_COST_PER_1K
        return input_cost + output_cost
