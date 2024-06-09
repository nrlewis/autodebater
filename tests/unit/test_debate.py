"""
Unit test the debate logic.  Mock all the responses
"""

import unittest
from unittest.mock import create_autospec

from autodebater.debate import SimpleDebate
from autodebater.participants import Debater


class TestDebate(unittest.TestCase):
    """
    Set up the debate logic with mocks
    """

    def setUp(self):
        self.motion = "This house believes that AI will surpass human intelligence."
        self.debate = SimpleDebate(motion=self.motion, epochs=2)

        # Create mock debaters
        self.debater1 = create_autospec(Debater, instance=True)
        self.debater1.name = "Debater1"
        self.debater1.role = "debater"
        self.debater1.stance = "for"
        self.debater1.respond.side_effect = [
            "Argument 1 from Debater1",
            "Rebuttal 1 from Debater1",
        ]

        self.debater2 = create_autospec(Debater, instance=True)
        self.debater2.name = "Debater2"
        self.debater2.role = "debater"
        self.debater2.stance = "against"
        self.debater2.respond.side_effect = [
            "Argument 1 from Debater2",
            "Rebuttal 1 from Debater2",
        ]

        self.debate.add_debaters(self.debater1)
        self.debate.add_debaters(self.debater2)

    def test_debate_flow(self):
        debate_generator = self.debate.debate()

        # Check the first message from the moderator
        initial_message = next(debate_generator)
        self.assertEqual(initial_message.message, "Please begin")
        self.assertEqual(initial_message.name, "mod")
        self.assertEqual(initial_message.stance, "neutral")
        self.assertEqual(initial_message.role, "moderator")

        # Check the first round of responses
        first_response = next(debate_generator)
        self.debater1.respond.assert_called_once()
        self.assertEqual(first_response.message, "Argument 1 from Debater1")
        self.assertEqual(first_response.name, "Debater1")
        self.assertEqual(first_response.role, "debater")

        second_response = next(debate_generator)
        self.debater2.respond.assert_called_once()
        self.assertEqual(second_response.message, "Argument 1 from Debater2")
        self.assertEqual(second_response.name, "Debater2")
        self.assertEqual(second_response.role, "debater")

        # Check the second round of responses (rebuttals)
        third_response = next(debate_generator)
        self.assertEqual(self.debater1.respond.call_count, 2)
        self.assertEqual(third_response.message, "Rebuttal 1 from Debater1")
        self.assertEqual(third_response.name, "Debater1")
        self.assertEqual(third_response.role, "debater")

        fourth_response = next(debate_generator)
        self.assertEqual(self.debater2.respond.call_count, 2)
        self.assertEqual(fourth_response.message, "Rebuttal 1 from Debater2")
        self.assertEqual(fourth_response.name, "Debater2")
        self.assertEqual(fourth_response.role, "debater")

        with self.assertRaises(StopIteration):
            next(debate_generator)


if __name__ == "__main__":
    unittest.main()
