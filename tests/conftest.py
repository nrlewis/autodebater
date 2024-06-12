"""
Confest conifguration.

Keep all fixutres here.
"""

from unittest.mock import Mock, create_autospec

import pytest

# from autodebater.dialogue import DialogueMessage
from autodebater.participants import Debater, Judge


def pytest_collection_modifyitems(config, items):  # pylint: disable=unused-argument
    for item in items:
        if "tests/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture
def judge_mock_llm_wrapper_factory(mocker):
    # Mock the LLMWrapperFactory.create_llm_wrapper method
    mock_llm_wrapper = mocker.patch(
        "autodebater.llm.LLMWrapperFactory.create_llm_wrapper"
    )

    # Create a mock instance of OpenAILLMWrapper
    mock_instance = Mock()
    mock_instance.generate_text_from_messages.return_value = (
        "70 The arguments for the motion were well-structured"
        + " and supported by evidence."
    )

    # Set the return value of the factory method to the mock instance
    mock_llm_wrapper.return_value = mock_instance

    return mock_llm_wrapper


@pytest.fixture
def mock_llm_wrapper_factory(mocker):
    # Mock the LLMWrapperFactory.create_llm_wrapper method
    mock_llm_wrapper = mocker.patch(
        "autodebater.llm.LLMWrapperFactory.create_llm_wrapper"
    )

    # Create a mock instance of OpenAILLMWrapper
    mock_instance = Mock()
    mock_instance.generate_text_from_messages.return_value = "Mocked response text"

    # Set the return value of the factory method to the mock instance
    mock_llm_wrapper.return_value = mock_instance

    return mock_llm_wrapper


# @pytest.fixture
# def patch_debate(mocker):
#     mock_debate = mocker.patch("autodebater.debate.SimpleDebate")
#
#     debate = Mock()
#     debate.debate.side_effect = [
#         DialogueMessage("mod", "moderater", "please begin", "123")
#         DialogueMessage("debater1", "debater", "I am for", "123")
#         DialogueMessage("", "moderater", "please begin", "123")
#         DialogueMessage("mod", "moderater", "please begin", "123")
#     ]
#     mock_debate.return_value = debate
#     return debate


@pytest.fixture
def mock_debater1():
    debater = create_autospec(Debater, instance=True)
    debater.name = "Debater1"
    debater.role = "debater"
    debater.stance = "for"
    debater.respond.side_effect = [
        "Argument 1 from Debater1",
        "Argument 2 from Debater1",
    ]
    return debater


@pytest.fixture
def mock_debater2():
    debater = create_autospec(Debater, instance=True)
    debater.name = "Debater1"
    debater.role = "debater"
    debater.stance = "against"
    debater.respond.side_effect = [
        "Argument 1 from Debater2",
        "Argument 2 from Debater2",
    ]
    return debater


@pytest.fixture
def mock_judge():
    judge = create_autospec(Judge, instance=True)
    judge.name = "Judge1"
    judge.role = "judge"
    judge.respond.side_effect = [
        "70 The arguments for the motion were well-structured"
        + " and supported by evidence.",
        "60 The arguments against the motion were convincing but had minor flaws.",
    ]
    return judge


@pytest.fixture
def mock_judge_with_bad_return():
    judge = create_autospec(Judge, instance=True)
    judge.name = "ErrorFormat-Judge"
    judge.role = "judge"
    judge.respond.side_effect = [
        "70  The arguments for the motion were well-structured "
        + "and supported by evidence.",
    ]
    return judge
