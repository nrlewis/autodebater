""" Unit Test Debate runners with mocked debates"""

import unittest
from unittest.mock import MagicMock, create_autospec, patch

from autodebater.debate_runners import (BasicJudgedDebateRunner,
                                        BasicSimpleDebateRunner)
from autodebater.dialogue import DialogueMessage
from autodebater.participants import Judge


class TestBasicJudgedDebateRunner(unittest.TestCase):
    """patch and mock the Basic Judged Debate Runners"""

    @patch("autodebater.debate_runners.Moderator")
    @patch("autodebater.debate_runners.DynamicExpertJudge")
    @patch("autodebater.debate_runners.BullshitDetector")
    @patch("autodebater.debate_runners.Debater")
    def test_initialization(
        self, mock_debater, mock_bd, mock_dej, mock_mod
    ):  # pylint: disable=unused-argument
        motion = "This house believes AI will surpass human intelligence"
        runner = BasicJudgedDebateRunner(motion)

        self.assertEqual(runner.debate.motion, motion)
        self.assertEqual(runner.debate.epochs, 2)
        self.assertEqual(len(runner.debate.debaters), 2)
        self.assertEqual(len(runner.debate.judges), 2)

    @patch("autodebater.debate_runners.Moderator")
    @patch("autodebater.debate_runners.DynamicExpertJudge")
    @patch("autodebater.debate_runners.BullshitDetector")
    @patch("autodebater.debate_runners.Debater")
    def test_run_debate(
        self, mock_debater, mock_bd, mock_dej, mock_mod
    ):  # pylint: disable=unused-argument
        motion = "This house believes AI will surpass human intelligence"
        runner = BasicJudgedDebateRunner(motion)

        runner.debate.debate = MagicMock(
            return_value=iter(
                [
                    DialogueMessage(
                        name="mod",
                        role="moderator",
                        message="Please begin",
                        debate_id="123",
                    ),
                    DialogueMessage(
                        name="Debater1",
                        role="debater",
                        message="AI will surpass human intelligence",
                        debate_id="123",
                    ),
                ]
            )
        )

        messages = list(runner.run_debate())
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].message, "Please begin")
        self.assertEqual(messages[1].message, "AI will surpass human intelligence")

    @patch("autodebater.debate_runners.Moderator")
    @patch("autodebater.debate_runners.DynamicExpertJudge")
    @patch("autodebater.debate_runners.BullshitDetector")
    @patch("autodebater.debate_runners.Debater")
    def test_get_judgements(
        self, mock_debater, mock_bd, mock_dej, mock_mod
    ):  # pylint: disable=unused-argument
        motion = "This house believes AI will surpass human intelligence"
        runner = BasicJudgedDebateRunner(motion)

        mock_judge = create_autospec(Judge, instance=True)
        mock_judge.summarize_judgement.return_value = (
            "70 The arguments for the motion were "
            "well-structured and supported by evidence."
        )
        mock_judge.name = "Judge"
        runner.debate.judges = [mock_judge]

        judgements = runner.get_judgements()
        self.assertEqual(len(judgements), 1)
        self.assertEqual(
            judgements[0],
            (
                "Judge",
                70.0,
                (
                    "The arguments for the motion were "
                    "well-structured and supported by evidence."
                ),
            ),
        )


class TestBasicSimpleDebateRunner(unittest.TestCase):
    """patch and mock a Simple Debate Runner for unit testing"""

    @patch("autodebater.debate_runners.Debater")
    def test_initialization(
        self, mock_debater
    ):  # pylint: disable=unused-argument
        motion = "This house believes AI will surpass human intelligence"
        runner = BasicSimpleDebateRunner(motion)

        self.assertEqual(runner.debate.motion, motion)
        self.assertEqual(runner.debate.epochs, 2)
        self.assertEqual(len(runner.debate.debaters), 2)

    @patch("autodebater.debate_runners.Debater")
    def test_run_debate(
        self, mock_debater
    ):  # pylint: disable=unused-argument
        motion = "This house believes AI will surpass human intelligence"
        runner = BasicSimpleDebateRunner(motion)

        runner.debate.debate = MagicMock(
            return_value=iter(
                [
                    DialogueMessage(
                        name="mod",
                        role="moderator",
                        message="Please begin",
                        debate_id="123",
                    ),
                    DialogueMessage(
                        name="Debater1",
                        role="debater",
                        message="AI will surpass human intelligence",
                        debate_id="123",
                    ),
                ]
            )
        )

        messages = list(runner.run_debate())
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].message, "Please begin")
        self.assertEqual(messages[1].message, "AI will surpass human intelligence")
