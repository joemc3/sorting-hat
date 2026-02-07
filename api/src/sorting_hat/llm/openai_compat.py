from openai import AsyncOpenAI

from sorting_hat.llm.provider import LLMMessage, LLMProvider, LLMResponse


class OpenAICompatProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str | None = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def complete(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        tokens = response.usage.total_tokens if response.usage else 0
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used=tokens,
        )
