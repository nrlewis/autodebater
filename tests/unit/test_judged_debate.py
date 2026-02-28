"""
This is a test module to cycle through the judged debate with mocks
"""

from unittest.mock import create_autospec

import pytest

from autodebater.debate import JudgedDebate
from autodebater.errors import JudgementParseError
from autodebater.participants import Moderator


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


def test_add_judge(mock_judge1):
    debate = JudgedDebate(motion="AI will surpass human intelligence")
    debate.add_judge(mock_judge1)
    assert mock_judge1 in debate.judges


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


def test_debate_flow(mock_debater1, mock_debater2, mock_judge1):

    debate = JudgedDebate(motion="AI will surpass human intelligence", epochs=1)
    debate.add_debaters(mock_debater1)
    debate.add_debaters(mock_debater2)
    debate.add_judge(mock_judge1)

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
    mock_judge1.respond.assert_called_once()
    assert (
        first_judgement.message
        == "70 The arguments for the motion were well-structured and "
        + "supported by evidence."
    )
    assert first_judgement.name == mock_judge1.name
    assert first_judgement.role == mock_judge1.role

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
    assert second_judgement.name == mock_judge1.name
    assert second_judgement.role == mock_judge1.role
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


def test_debate_retry_on_bad_judge_output(mock_debater1):
    """Judge fails on first response but succeeds on retry — debate continues."""
    from unittest.mock import create_autospec
    from autodebater.participants import Judge

    debate = JudgedDebate(motion="AI will surpass human intelligence", epochs=1)
    debate.add_debaters(mock_debater1)

    retry_judge = create_autospec(Judge, instance=True)
    retry_judge.name = "RetryJudge"
    retry_judge.role = "judge"
    # First call returns bad format; second call (retry) returns good format
    retry_judge.respond.side_effect = [
        "bad output with no leading score",
        "75 After correction, here is my score.",
    ]
    debate.add_judge(retry_judge)

    msgs = list(debate.debate())
    # Should not raise; judge should have been called twice
    assert retry_judge.respond.call_count == 2
    judge_msgs = [m for m in msgs if m.role == "judge"]
    assert judge_msgs[0].judgement == 75.0


def test_debate_retry_exhausted_raises(mock_debater1):
    """Judge fails on both attempts — JudgementParseError is raised from debate()."""
    from unittest.mock import create_autospec
    from autodebater.participants import Judge

    debate = JudgedDebate(motion="AI will surpass human intelligence", epochs=1)
    debate.add_debaters(mock_debater1)

    bad_judge = create_autospec(Judge, instance=True)
    bad_judge.name = "BadJudge"
    bad_judge.role = "judge"
    bad_judge.respond.side_effect = [
        "still bad",
        "also bad",
    ]
    debate.add_judge(bad_judge)

    with pytest.raises(JudgementParseError):
        list(debate.debate())


def test_judged_debate_with_moderator(mock_debater1, mock_judge1):
    """When a Moderator is added, opening/question/closing messages are yielded."""
    mock_mod = create_autospec(Moderator, instance=True)
    mock_mod.name = "Moderator"
    mock_mod.role = "moderator"
    mock_mod.opening_statement.return_value = "Welcome to this debate."
    mock_mod.generate_question.return_value = "Can you elaborate on that point?"
    mock_mod.closing_statement.return_value = "Thank you all for participating."

    debate = JudgedDebate(motion="AI will surpass human intelligence", epochs=1)
    debate.add_debaters(mock_debater1)
    debate.add_judge(mock_judge1)
    debate.add_moderator(mock_mod)

    msgs = list(debate.debate())

    # First message should be moderator opening
    assert msgs[0].message == "Welcome to this debate."
    assert msgs[0].role == "moderator"
    assert msgs[0].name == "Moderator"

    # Last message should be moderator closing
    assert msgs[-1].message == "Thank you all for participating."
    assert msgs[-1].role == "moderator"

    mock_mod.opening_statement.assert_called_once()
    mock_mod.closing_statement.assert_called_once()


if __name__ == "__main__":
    pytest.main()
