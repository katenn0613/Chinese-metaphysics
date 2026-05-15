from metaphysics_app.ai.client import (
    NullLLMClient,
    OpenAICompatibleClient,
    build_default_llm_client,
)
from metaphysics_app.ai.service import FortuneAIService, consultation_session_from_payload
from metaphysics_app.utils.serialization import to_jsonable


def test_default_llm_client_stays_offline_without_explicit_model(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    client = build_default_llm_client()

    assert isinstance(client, NullLLMClient)


def test_default_llm_client_uses_openai_compatible_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")

    client = build_default_llm_client()

    assert isinstance(client, OpenAICompatibleClient)
    assert client.model == "test-model"
    assert client.base_url == "https://example.test/v1"


def test_consultation_session_round_trips_from_payload():
    session = FortuneAIService().ask_about_chart("这个盘怎么理解？")

    restored = consultation_session_from_payload(to_jsonable(session))

    assert restored.title == session.title
    assert [message.role for message in restored.messages] == ["user", "assistant"]
    assert restored.messages[0].content == "这个盘怎么理解？"
