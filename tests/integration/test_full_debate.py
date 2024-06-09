"""
Integration test for a full debate
"""

import logging

import pytest

from autodebater.debate import JudgedDebate, SimpleDebate
from autodebater.participants import BullshitDetector, Debater, Judge

logger = logging.getLogger(__name__)


@pytest.mark.skip
def test_simple_debate():

    motion = "Cats are better than dogs."
    debate = SimpleDebate(motion=motion, epochs=1)

    debater1 = Debater(name="Debater1", motion=motion, stance="for")
    debater2 = Debater(name="Debater2", motion=motion, stance="against")

    # Add debaters to the debate
    debate.add_debaters(debater1)
    debate.add_debaters(debater2)
    debate = SimpleDebate(motion=motion, epochs=2)
    debate.add_debaters(debater1)
    debate.add_debaters(debater2)

    for msg in debate.debate():
        logger.debug(msg)

    assert True


def test_judged_debate():

    motion = "The earth is round"
    debate = JudgedDebate(motion=motion, epochs=2)

    debater1 = Debater(name="Debater1", motion=motion, stance="for")
    debater2 = Debater(name="Debater2", motion=motion, stance="against")
    judge1 = Judge(name="Judge1", motion=motion)
    judge2 = BullshitDetector(name="BullshitDetector", motion=motion)

    # Add debaters to the debate
    debate.add_debaters(debater1)
    debate.add_debaters(debater2)
    debate.add_judge(judge1)
    debate.add_judge(judge2)

    for msg in debate.debate():
        logger.info(msg)

    assert True
