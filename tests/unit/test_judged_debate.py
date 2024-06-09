"""
This is a test module to cycle through the judged debate with mocks
"""

import pytest

from autodebater.debate import JudgedDebate
from autodebater.errors import JudgementParseError


def test_judged_debate_initialization():
    debate = JudgedDebate(motion="AI will surpass human intelligence", epochs=2)
    assert debate.motion == "AI will surpass human intelligence"
    assert debate.epochs == 2
    assert not debate.debaters
    assert not debate.judges
    assert debate.running_score == 50
    assert not debate.scores


def test_add_debater(mock_debater1):
    debate = JudgedDebate(motion="AI will surpass human intelligence")
    debate.add_debaters(mock_debater1)
    assert mock_debater1 in debate.debaters


def test_add_judge(mock_judge):
    debate = JudgedDebate(motion="AI will surpass human intelligence")
    debate.add_judge(mock_judge)
    assert mock_judge in debate.judges


def test_parse_judgement():
    debate = JudgedDebate(motion="AI will surpass human intelligence")
    judgement = (
        "70 The arguments for the motion were "
        + "well-structured and supported by evidence."
    )
    score, justification = debate.parse_judgement(judgement)
    assert score == 70
    assert justification == (
        "The arguments for the motion were"
        + " well-structured and supported by evidence."
    )


def test_debate_flow(mock_debater1, mock_debater2, mock_judge):

    debate = JudgedDebate(motion="AI will surpass human intelligence", epochs=1)
    debate.add_debaters(mock_debater1)
    debate.add_debaters(mock_debater2)
    debate.add_judge(mock_judge)

    debate_generator = debate.debate()

    # Check the first message from the moderator
    initial_message = next(debate_generator)
    assert initial_message.message == "Debater1 - please begin"
    assert initial_message.name == "mod"
    assert initial_message.role == "moderator"

    # Check the first round of responses
    first_response = next(debate_generator)
    mock_debater1.respond.assert_called_once()
    assert first_response.message == "Argument 1 from Debater1"
    assert first_response.name == mock_debater1.name
    assert first_response.role == mock_debater1.role

    # Check the first judgement
    first_judgement = next(debate_generator)
    mock_judge.respond.assert_called_once()
    assert (
        first_judgement.message
        == "70 The arguments for the motion were well-structured and "
        + "supported by evidence."
    )
    assert first_judgement.name == mock_judge.name
    assert first_judgement.role == mock_judge.role

    current_score = next(debate_generator)
    assert current_score.message == "Current Score is 70.0"
    assert current_score.name == "mod"
    assert current_score.role == "moderator"
    assert debate.scores == [70]
    assert debate.running_score == 70.0
    # Check the second round of responses
    second_response = next(debate_generator)
    assert second_response.message == "Argument 1 from Debater2"
    assert second_response.name == mock_debater2.name
    assert second_response.role == mock_debater2.role

    # Check the second judgement
    second_judgement = next(debate_generator)
    assert (
        second_judgement.message
        == "60 The arguments against the motion were convincing but "
        + "had minor flaws."
    )
    assert second_judgement.name == mock_judge.name
    assert second_judgement.role == mock_judge.role
    assert debate.scores == [70.0, 60.0]
    assert 65 > debate.running_score > 64


def test_debate_flow_with_error(
    mock_debater1, mock_debater2, mock_judge_with_bad_return
):

    debate = JudgedDebate(motion="AI will surpass human intelligence", epochs=1)
    debate.add_debaters(mock_debater1)
    debate.add_debaters(mock_debater2)
    debate.add_judge(mock_judge_with_bad_return)

    with pytest.raises(JudgementParseError):
        debate.parse_judgement("034\\tasdbase")

    with pytest.raises(JudgementParseError):
        debate.parse_judgement("notabs")


if __name__ == "__main__":
    pytest.main()
