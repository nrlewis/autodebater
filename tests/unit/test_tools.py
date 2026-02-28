"""Unit tests for the tools module and ToolEnabledDebater."""

from unittest.mock import MagicMock, patch

import pytest

from autodebater.dialogue import DialogueMessage


def test_get_default_tools_returns_list():
    """get_default_tools returns a list (possibly empty if deps unavailable)."""
    from autodebater.tools import get_default_tools
    tools = get_default_tools()
    assert isinstance(tools, list)


def test_tool_enabled_debater_no_tools(mocker):
    """ToolEnabledDebater with empty tools list falls back to normal Debater respond."""
    mock_llm = MagicMock()
    mock_llm.generate_text_from_messages.return_value = "Standard response."
    mocker.patch(
        "autodebater.participants.LLMWrapperFactory.create_llm_wrapper",
        return_value=mock_llm,
    )

    from autodebater.participants import ToolEnabledDebater
    debater = ToolEnabledDebater(
        name="Alice",
        motion="AI will surpass human intelligence",
        stance="for",
        llm_provider="openai",
        tools=[],  # No tools
    )

    msg = DialogueMessage(name="mod", role="moderator", message="Please begin", debate_id="1")
    result = debater.respond([msg])
    assert result == "Standard response."


def test_tool_enabled_debater_with_tool_call(mocker):
    """ToolEnabledDebater with tools executes tool calls and returns final answer."""
    mock_llm_instance = MagicMock()
    mocker.patch(
        "autodebater.participants.LLMWrapperFactory.create_llm_wrapper",
        return_value=mock_llm_instance,
    )

    from langchain_core.messages import AIMessage

    # First invocation: AI requests a tool call
    ai_with_tool = AIMessage(content="", tool_calls=[
        {"name": "mock_tool", "args": {"query": "AI"}, "id": "call_1"}
    ])
    # Second invocation: AI gives final answer
    ai_final = AIMessage(content="AI is advancing rapidly.")
    mock_llm_instance.llm = MagicMock()
    mock_llm_instance.llm.bind_tools.return_value = mock_llm_instance.llm
    mock_llm_instance.llm.invoke.side_effect = [ai_with_tool, ai_final]

    # A mock tool
    mock_tool = MagicMock()
    mock_tool.name = "mock_tool"
    mock_tool.run.return_value = "Wikipedia result about AI"

    from autodebater.participants import ToolEnabledDebater
    debater = ToolEnabledDebater(
        name="Alice",
        motion="AI will surpass human intelligence",
        stance="for",
        llm_provider="openai",
        tools=[mock_tool],
    )

    msg = DialogueMessage(name="mod", role="moderator", message="Please begin", debate_id="1")
    result = debater.respond([msg])

    assert result == "AI is advancing rapidly."
    mock_tool.run.assert_called_once()
