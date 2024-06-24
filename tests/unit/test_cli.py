""" Test the CLI """

import unittest
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from autodebater.dialogue import DialogueMessage
from autodebater.run_debates import app

runner = CliRunner()


class TestRunDebatesCLI(unittest.TestCase):
    """CLI test using CliRunner"""

    @patch("autodebater.run_debates.BasicJudgedDebateRunner")
    @patch("autodebater.run_debates.Live")
    def test_judged_debate(
        self, mock_live, mock_basic_judged_debate_runner
    ):  # pylint: disable=unused-argument
        mock_runner = MagicMock()
        mock_runner.run_debate.return_value = iter(
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
        mock_runner.get_judgements.return_value = [
            (
                "Judge1",
                70,
                "The arguments for the motion were supported by evidence.",
            )
        ]
        mock_basic_judged_debate_runner.return_value = mock_runner

        result = runner.invoke(
            app,
            [
                "judged-debate",
                "AI will surpass human intelligence",
            ],
        )

        mock_basic_judged_debate_runner.assert_called_once_with(
            motion="AI will surpass human intelligence", epochs=2, llm="openai"
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "AI will surpass human intelligence",
            result.output,
        )

    @patch("autodebater.run_debates.BasicSimpleDebateRunner")
    @patch("autodebater.run_debates.Console")
    def test_simple_debate(
        self, mock_console, mock_basic_simple_debate_runner
    ):  # pylint: disable=unused-argument
        mock_runner = MagicMock()
        mock_runner.run_debate.return_value = iter(
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
        mock_basic_simple_debate_runner.return_value = mock_runner

        result = runner.invoke(
            app,
            [
                "simple-debate",
                "This house believes AI will surpass human intelligence",
            ],
        )

        mock_basic_simple_debate_runner.assert_called_once_with(
            motion="This house believes AI will surpass human intelligence",
            epochs=2,
            llm="openai",
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "This house believes AI will surpass human intelligence",
            result.output,
        )
