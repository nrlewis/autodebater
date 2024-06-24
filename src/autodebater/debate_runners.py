"""
Module wrapps the debate execution into a class
"""

from abc import ABC, abstractmethod
from typing import Any, Generator

from autodebater.debate import JudgedDebate, SimpleDebate
from autodebater.dialogue import DialogueMessage
from autodebater.participants import BullshitDetector, Debater, Judge


class DebateRunner(ABC):

    @abstractmethod
    def run_debate(self) -> Generator[DialogueMessage, Any, None]:
        pass


class BasicJudgedDebateRunner(DebateRunner):
    """
    Execute a basic debate with two debaters, and two judges
    """

    def __init__(self, motion: str, epochs: int = 2, llm: str = "openai"):
        self.debate = JudgedDebate(motion=motion, epochs=epochs)

        debater1 = Debater(
            name="Debater1", motion=motion, stance="for", llm_provider=llm
        )
        debater2 = Debater(
            name="Debater2", motion=motion, stance="against", llm_provider=llm
        )
        judge = Judge(name="Judge", motion=motion, llm_provider=llm)
        bullshit_detector = BullshitDetector(
            name="BullshitDetector", motion=motion, llm_provider=llm
        )
        # Add debaters to the debate
        self.debate.add_debaters(debater1)
        self.debate.add_debaters(debater2)
        self.debate.add_judge(judge)
        self.debate.add_judge(bullshit_detector)
        super().__init__()

    def run_debate(self):
        for msg in self.debate.debate():
            yield msg

    def get_judgements(self):
        judgements = []
        for judge in self.debate.judges:
            resp = judge.summarize_judgement()
            score, judgement = self.debate.parse_judgement(resp)
            msg = (judge.name, score, judgement)
            judgements.append(msg)

        return judgements


class BasicSimpleDebateRunner(DebateRunner):
    """
    Execute a Basic Debate with two debaters
    """

    def __init__(self, motion: str, epochs: int = 2, llm: str = "openai"):
        self.debate = SimpleDebate(motion=motion, epochs=epochs)

        debater1 = Debater(
            name="Debater1", motion=motion, stance="for", llm_provider=llm
        )
        debater2 = Debater(
            name="Debater2", motion=motion, stance="against", llm_provider=llm
        )

        # Add debaters to the debate
        self.debate.add_debaters(debater1)
        self.debate.add_debaters(debater2)
        super().__init__()

    def run_debate(self):
        for msg in self.debate.debate():
            yield msg
