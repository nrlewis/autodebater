"""
pytest for the llm module
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from autodebater.llm import (
    AnthropicLLMWrapper,
    AzureOpenAILLMWrapper,
    LLMWrapperFactory,
    OpenAILLMWrapper,
)


def test_openai_llm_wrapper():
    openai_llm = OpenAILLMWrapper()
    assert openai_llm is not None


def test_llm_wrapper_factory():
    openai_llm = LLMWrapperFactory.create_llm_wrapper("openai", model="gpt-4o")
    assert isinstance(openai_llm, OpenAILLMWrapper)


def test_azure_llm_wrapper_factory(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    monkeypatch.setenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
    with patch("autodebater.llm.AzureChatOpenAI") as mock_chat:
        mock_chat.return_value = MagicMock()
        openai_llm = LLMWrapperFactory.create_llm_wrapper("azure")
        assert isinstance(openai_llm, AzureOpenAILLMWrapper)


def test_anthropic_llm_wrapper_missing_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is not set"):
        AnthropicLLMWrapper()


def test_anthropic_llm_wrapper_factory(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("autodebater.llm.ChatAnthropic") as mock_chat:
        mock_chat.return_value = MagicMock()
        wrapper = LLMWrapperFactory.create_llm_wrapper("anthropic", model="claude-opus-4-6")
        assert isinstance(wrapper, AnthropicLLMWrapper)


def test_anthropic_llm_wrapper_generate(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("autodebater.llm.ChatAnthropic") as mock_chat:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="Mocked Anthropic response")
        mock_chat.return_value = mock_instance
        wrapper = AnthropicLLMWrapper(model="claude-opus-4-6")
        result = wrapper.generate_text_from_messages([("user", "Hello")])
        assert result == "Mocked Anthropic response"
