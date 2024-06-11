"""
Test module for the participants module.
"""

import pytest

from autodebater.defaults import EXPERT_JUDGE_PROMPT, LLM_PROVIDER
from autodebater.dialogue import DialogueMessage
from autodebater.participants import Debater, Judge


def test_participant_initialization(mock_llm_wrapper_factory):
    # Create a Debater instance
    name = "Debater1"
    role_prompt = (
        "You are a debater arguing for the position "
        + "that charcoal bbq is better than gas."
    )
    llm_provider = "openai"
    model_params = {"model": "gpt-4o", "param2": "value2"}

    debater = Debater(name, role_prompt, llm_provider, **model_params)

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

    debater = Debater(name, role_prompt, llm_provider, **model_params)

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


if __name__ == "__main__":
    pytest.main()
