"""
Module wrapps the debate execution into a class
"""

from abc import ABC, abstractmethod
from typing import Any, Generator

from autodebater.debate import JudgedDebate, SimpleDebate
from autodebater.dialogue import DialogueMessage
from autodebater.names import generate_name
from autodebater.participants import (BullshitDetector, Debater, DynamicExpertJudge,
                                      Judge, Moderator, ToolEnabledDebater)


class DebateRunner(ABC):

    @abstractmethod
    def run_debate(self) -> Generator[DialogueMessage, Any, None]:
        pass


class BasicJudgedDebateRunner(DebateRunner):
    """
    Execute a basic debate with two debaters, and two judges
    """

    def __init__(self, motion: str, epochs: int = 2, llm: str = "openai", **kwargs):
        self.debate = JudgedDebate(motion=motion, epochs=epochs)

        used_names: set = set()
        name1 = generate_name(used_names)
        used_names.add(name1)
        name2 = generate_name(used_names)
        used_names.add(name2)

        debater_prompt = kwargs.get("debater_prompt", None)
        judge_prompt = kwargs.get("judge_prompt", None)
        model_params = {}
        if "model" in kwargs:
            model_params["model"] = kwargs["model"]
        if "temperature" in kwargs:
            model_params["temperature"] = kwargs["temperature"]

        debater1_kwargs = {"name": name1, "motion": motion, "stance": "for", "llm_provider": llm}
        debater2_kwargs = {"name": name2, "motion": motion, "stance": "against", "llm_provider": llm}
        judge_kwargs = {"name": generate_name(used_names), "motion": motion, "llm_provider": llm}
        used_names.add(judge_kwargs["name"])
        bd_kwargs = {"name": generate_name(used_names), "motion": motion, "llm_provider": llm}

        if debater_prompt:
            debater1_kwargs["instruction_prompt"] = debater_prompt
            debater2_kwargs["instruction_prompt"] = debater_prompt
        if judge_prompt:
            judge_kwargs["instruction_prompt"] = judge_prompt
            bd_kwargs["instruction_prompt"] = judge_prompt
        debater1_kwargs.update(model_params)
        debater2_kwargs.update(model_params)
        judge_kwargs.update(model_params)
        bd_kwargs.update(model_params)

        DebaterClass = ToolEnabledDebater if kwargs.get("use_tools") else Debater
        debater1 = DebaterClass(**debater1_kwargs)
        debater2 = DebaterClass(**debater2_kwargs)
        judge = DynamicExpertJudge(**judge_kwargs)
        bullshit_detector = BullshitDetector(**bd_kwargs)

        moderator_name = generate_name(used_names)
        moderator = Moderator(name=moderator_name, motion=motion, llm_provider=llm, **model_params)

        # Add debaters to the debate
        self.debate.add_debaters(debater1)
        self.debate.add_debaters(debater2)
        self.debate.add_judge(judge)
        self.debate.add_judge(bullshit_detector)
        self.debate.add_moderator(moderator)
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

    def __init__(self, motion: str, epochs: int = 2, llm: str = "openai", **kwargs):
        self.debate = SimpleDebate(motion=motion, epochs=epochs)

        used_names: set = set()
        name1 = generate_name(used_names)
        used_names.add(name1)
        name2 = generate_name(used_names)

        debater_prompt = kwargs.get("debater_prompt", None)
        model_params = {}
        if "model" in kwargs:
            model_params["model"] = kwargs["model"]
        if "temperature" in kwargs:
            model_params["temperature"] = kwargs["temperature"]

        debater1_kwargs = {"name": name1, "motion": motion, "stance": "for", "llm_provider": llm}
        debater2_kwargs = {"name": name2, "motion": motion, "stance": "against", "llm_provider": llm}
        if debater_prompt:
            debater1_kwargs["instruction_prompt"] = debater_prompt
            debater2_kwargs["instruction_prompt"] = debater_prompt
        debater1_kwargs.update(model_params)
        debater2_kwargs.update(model_params)

        DebaterClass = ToolEnabledDebater if kwargs.get("use_tools") else Debater
        debater1 = DebaterClass(**debater1_kwargs)
        debater2 = DebaterClass(**debater2_kwargs)

        # Add debaters to the debate
        self.debate.add_debaters(debater1)
        self.debate.add_debaters(debater2)
        super().__init__()

    def run_debate(self):
        for msg in self.debate.debate():
            yield msg
