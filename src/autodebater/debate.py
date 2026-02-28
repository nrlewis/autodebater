"""
This is the main class for executing the debate.
It consists of an DialogueNotifier, which
will register different particpants, and notify them
of updates.  It will also execute the main loop
for a debate
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Generator

from autodebater.dialogue import DialogueHistory, DialogueMessage
from autodebater.errors import JudgementParseError
from autodebater.participants import Debater, Judge, Moderator
from autodebater.scoring import geometric_mean

logger = logging.getLogger(__name__)


class Debate(ABC):
    """
    Core Debate function, handles the logic to pass
    messages dependening on the debate type.
    """

    def __init__(self, motion: str, epochs: int = 10):
        self.debaters = []
        self.motion = motion
        self.debate_id = str(hash(motion))
        self.dialogue_history = DialogueHistory()
        self.epochs = epochs

    def add_debaters(self, debater: Debater):
        self.debaters.append(debater)

    @abstractmethod
    def debate(self) -> Generator[DialogueMessage, Any, None]:
        pass


class SimpleDebate(Debate):
    """
    A Simple Debate is between two debaters only,
    passing messages from one debater to the next
    """

    def debate(self):
        steps = self.epochs * len(self.debaters)

        msg = DialogueMessage("mod", "moderator", "Please begin", self.debate_id)
        yield msg
        self.dialogue_history.add_message(msg)
        i = 0
        while i < steps:
            speaker = self.debaters[i % len(self.debaters)]
            response = speaker.respond([msg])
            msg = DialogueMessage(
                speaker.name, speaker.role, response, self.debate_id, speaker.stance
            )
            self.dialogue_history.add_message(msg)
            yield msg
            i += 1


class JudgedDebate(Debate):
    """
    A JudgedDebate contains at least one judge, who listens to
    each message and performs a score reflecting which side of the
    debate they're leaning towards.
    """

    def __init__(self, motion: str, epochs: int = 10):
        self.judges = []
        self.moderator: Moderator = None
        self.running_score = 50
        self.scores = []
        super().__init__(motion, epochs)

    def add_judge(self, judge: Judge):
        self.judges.append(judge)

    def add_moderator(self, moderator: Moderator):
        self.moderator = moderator

    def parse_judgement(self, judgement):
        match = re.match(r"^(\d+(?:\.\d+)?)\s+(.+)$", judgement.strip(), re.DOTALL)
        if not match:
            raise JudgementParseError(
                f"Could not parse judgement (expected '<score> <justification>'): {judgement!r}"
            )
        score = float(match.group(1))
        justification = match.group(2)
        if not 0 <= score <= 100:
            raise JudgementParseError(
                f"Score {score} is out of range [0, 100]"
            )
        return score, justification

    def debate(self):
        steps = self.epochs * len(self.debaters)

        i = 0
        if self.moderator is not None:
            opening_text = self.moderator.opening_statement()
            mod_name = self.moderator.name
        else:
            first_debater_name = self.debaters[i].name
            opening_text = f"{first_debater_name} - please begin"
            mod_name = "mod"

        msg = DialogueMessage(
            name=mod_name,
            role="moderator",
            message=opening_text,
            debate_id=self.debate_id,
        )
        self.dialogue_history.add_message(msg)
        yield msg

        epoch = 0
        while i < steps:
            speaker = self.debaters[i % len(self.debaters)]
            response = speaker.respond([msg])
            msg = DialogueMessage(
                name=speaker.name,
                role=speaker.role,
                message=response,
                debate_id=self.debate_id,
                stance=speaker.stance,
            )
            self.dialogue_history.add_message(msg)
            yield msg

            for judge in self.judges:
                judgement = judge.respond([msg])
                judge_msg = DialogueMessage(
                    judge.name, judge.role, judgement, self.debate_id
                )

                try:
                    score, _ = self.parse_judgement(judgement)
                    judge_msg.judgement = score
                    self.scores.append(score)
                except JudgementParseError:
                    logger.warning(
                        "Judge %s returned malformed output; retrying once.", judge.name
                    )
                    correction = DialogueMessage(
                        "mod",
                        "moderator",
                        "Your response must start with a number 0-100 followed by a space and your justification.",
                        self.debate_id,
                    )
                    judgement = judge.respond([correction])
                    judge_msg.message = judgement
                    try:
                        score, _ = self.parse_judgement(judgement)
                        judge_msg.judgement = score
                        self.scores.append(score)
                    except JudgementParseError as e:
                        logger.exception(e)
                        raise

                self.dialogue_history.add_message(judge_msg)
                self.running_score = geometric_mean(self.scores)
                yield judge_msg

            moderator_message = DialogueMessage(
                "mod",
                "moderator",
                f"Current Score is {self.running_score}",
                self.debate_id,
            )
            yield moderator_message
            i += 1

            # After each full epoch (all debaters have spoken), yield moderator question
            if self.moderator is not None and (i % len(self.debaters) == 0):
                epoch += 1
                if epoch < self.epochs:
                    question_text = self.moderator.generate_question(self.dialogue_history)
                    q_msg = DialogueMessage(
                        name=self.moderator.name,
                        role="moderator",
                        message=question_text,
                        debate_id=self.debate_id,
                    )
                    self.dialogue_history.add_message(q_msg)
                    msg = q_msg
                    yield q_msg

        if self.moderator is not None:
            closing_text = self.moderator.closing_statement(self.dialogue_history)
            closing_msg = DialogueMessage(
                name=self.moderator.name,
                role="moderator",
                message=closing_text,
                debate_id=self.debate_id,
            )
            self.dialogue_history.add_message(closing_msg)
            yield closing_msg
