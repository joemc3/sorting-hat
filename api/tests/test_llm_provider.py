from sorting_hat.llm.provider import LLMMessage, LLMProvider, LLMResponse
from sorting_hat.llm.openai_compat import OpenAICompatProvider


def test_llm_message_creation():
    msg = LLMMessage(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"


def test_llm_response_creation():
    resp = LLMResponse(content="Hi", model="gpt-4", tokens_used=10)
    assert resp.content == "Hi"
    assert resp.tokens_used == 10


def test_openai_compat_provider_is_llm_provider():
    provider = OpenAICompatProvider(api_key="test-key")
    assert isinstance(provider, LLMProvider)


def test_openai_compat_provider_custom_base_url():
    provider = OpenAICompatProvider(
        api_key="test-key", base_url="http://localhost:11434/v1"
    )
    assert provider.client.base_url.host == "localhost"
