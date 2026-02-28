"""
Test module for the participants module.
"""

from unittest.mock import MagicMock, patch

import pytest

from autodebater.defaults import EXPERT_JUDGE_PROMPT, LLM_PROVIDER
from autodebater.dialogue import DialogueMessage
from autodebater.participants import Debater, DynamicExpertJudge, Judge, Moderator


def test_participant_initialization(mock_llm_wrapper_factory):
    # Create a Debater instance
    name = "Debater1"
    role_prompt = (
        "You are a debater arguing for the position "
        + "that charcoal bbq is better than gas."
    )
    llm_provider = "openai"
    model_params = {"model": "gpt-4o", "param2": "value2"}

    debater = Debater(name, role_prompt, "for", llm_provider=llm_provider, **model_params)

    # Verify that the LLMWrapperFactory.create_llm_wrapper was called correctly
    mock_llm_wrapper_factory.assert_called_once_with(
        llm_provider,
        **model_params,
    )

    # Verify that the instance variables are set correctly
    assert debater.name == name
    assert debater.system_prompt is not None
    assert debater.llm_provider == llm_provider
    assert debater.model_params == model_params


def test_debater_respond(mock_llm_wrapper_factory):  # pylint: disable=unused-argument
    # Create a Debater instance
    name = "Debater1"
    role_prompt = "You are a debater arguing for the position."
    llm_provider = "openai"
    model_params = {"model": "gpt-4o", "param2": "value2"}

    debater = Debater(name, role_prompt, "for", llm_provider=llm_provider, **model_params)

    # Define the most recent chats
    most_recent_chats = [
        DialogueMessage(
            name=name,
            debate_id="unittest",
            role="debater",
            message="this topic is awesome",
        )
    ]

    # Call the respond method
    response = debater.respond(most_recent_chats)

    assert response == "Mocked response text"


def test_judge_initialization(judge_mock_llm_wrapper_factory):
    # Create a Judge instance
    name = "Judge1"
    motion = "AI will surpass human intelligence"
    role_prompt = EXPERT_JUDGE_PROMPT.format(motion=motion)
    llm_provider = LLM_PROVIDER
    model_params = {"model": "gpt-4o"}

    judge = Judge(name, motion, role_prompt, llm_provider, **model_params)

    # Verify that the LLMWrapperFactory.create_llm_wrapper was called correctly
    judge_mock_llm_wrapper_factory.assert_called_once_with(llm_provider, **model_params)

    # Verify that the instance variables are set correctly
    assert judge.name == name
    assert judge.system_prompt == role_prompt
    assert judge.llm_provider == llm_provider
    assert judge.model_params == model_params


def test_judge_respond(judge_mock_llm_wrapper_factory):
    # Create a Judge instance
    name = "Judge1"
    motion = "AI will surpass human intelligence"
    role_prompt = EXPERT_JUDGE_PROMPT.format(motion=motion)
    llm_provider = LLM_PROVIDER
    model_params = {"model": "gpt-4o"}

    judge = Judge(name, motion, role_prompt, llm_provider, **model_params)

    # Define the most recent chats
    most_recent_chats = [
        DialogueMessage(
            name="Debater1",
            debate_id="unittest",
            role="debater",
            message="AI will surpass human intelligence.",
        )
    ]

    # Call the respond method
    response = judge.respond(most_recent_chats)

    # Verify the response
    assert (
        response
        == "70 The arguments for the motion were "
        + "well-structured and supported by evidence."
    )
    judge_mock_llm_wrapper_factory.return_value.generate_text_from_messages.assert_called_once()  # pylint: disable=line-too-long


def test_judge_summarize(judge_mock_llm_wrapper_factory):
    # Create a Judge instance
    name = "Judge1"
    motion = "AI will surpass human intelligence"
    role_prompt = EXPERT_JUDGE_PROMPT.format(motion=motion)
    llm_provider = LLM_PROVIDER
    model_params = {"model": "gpt-4o"}

    judge = Judge(name, motion, role_prompt, llm_provider, **model_params)

    # Define the most recent chats
    # Call the respond method
    response = judge.summarize_judgement()

    # Verify the response
    assert (
        response
        == "70 The arguments for the motion were "
        + "well-structured and supported by evidence."
    )
    judge_mock_llm_wrapper_factory.return_value.generate_text_from_messages.assert_called_once()  # pylint: disable=line-too-long


def test_dynamic_expert_judge_discovers_expertise(mocker):
    """DynamicExpertJudge lazily discovers expertise on first respond() call."""
    mock_llm = MagicMock()
    # First call: expertise discovery; second call: actual judging
    mock_llm.generate_text_from_messages.side_effect = [
        "machine learning and AI ethics",
        "70 Strong argument for the motion.",
    ]
    mocker.patch(
        "autodebater.participants.LLMWrapperFactory.create_llm_wrapper",
        return_value=mock_llm,
    )

    from autodebater.dialogue import DialogueMessage
    motion = "AI will surpass human intelligence"
    judge = DynamicExpertJudge(name="ExpertJudge", motion=motion, llm_provider="openai")

    # Expertise NOT yet discovered — construction is free of LLM calls
    assert judge.expertise is None

    # Trigger first respond() — this discovers expertise then judges
    msg = DialogueMessage(name="Debater1", role="debater", message="AI is advancing.", debate_id="1")
    response = judge.respond([msg])

    assert judge.expertise == "machine learning and AI ethics"
    assert "machine learning and AI ethics" in judge.system_prompt
    assert response == "70 Strong argument for the motion."


def test_moderator_opening(mocker):
    """Moderator.opening_statement calls LLM and returns the text."""
    mock_llm = MagicMock()
    mock_llm.generate_text_from_messages.return_value = "Welcome to this debate."
    mocker.patch(
        "autodebater.participants.LLMWrapperFactory.create_llm_wrapper",
        return_value=mock_llm,
    )
    from autodebater.dialogue import DialogueHistory
    motion = "AI will surpass human intelligence"
    mod = Moderator(name="Mod", motion=motion, llm_provider="openai")
    result = mod.opening_statement()
    assert result == "Welcome to this debate."


if __name__ == "__main__":
    pytest.main()
