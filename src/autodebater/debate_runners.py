"""
Module wraps the debate execution into a class
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generator, List, Optional

from autodebater.debate import ExpertPanelDebate, JudgedDebate, SimpleDebate
from autodebater.defaults import PANEL_JUDGE_PROMPT
from autodebater.dialogue import DialogueMessage
from autodebater.names import generate_name
from autodebater.participants import (BullshitDetector, Debater, DynamicExpertJudge,
                                      Judge, Moderator, PanelParticipant, ToolEnabledDebater)


@dataclass
class RunnerConfig:
    """Unified configuration for all debate runners."""
    motion: str
    epochs: int = 2
    llm: str = "openai"
    debater_prompt: Optional[str] = None
    judge_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    use_tools: bool = False
    domains: Optional[List[str]] = None  # expert panel only

    def model_params(self) -> dict:
        params = {}
        if self.model:
            params["model"] = self.model
        if self.temperature is not None:
            params["temperature"] = self.temperature
        return params


DEFAULT_PANEL_DOMAINS = [
    "Science & Technology",
    "Ethics & Philosophy",
    "Economics & Policy",
    "Social Sciences & Psychology",
]


class DebateRunner(ABC):

    @abstractmethod
    def run_debate(self) -> Generator[DialogueMessage, Any, None]:
        pass


class BasicJudgedDebateRunner(DebateRunner):
    """Execute a basic debate with two debaters and two judges."""

    def __init__(self, motion: str, epochs: int = 2, llm: str = "openai", **kwargs):
        config = RunnerConfig(
            motion=motion,
            epochs=epochs,
            llm=llm,
            debater_prompt=kwargs.get("debater_prompt"),
            judge_prompt=kwargs.get("judge_prompt"),
            model=kwargs.get("model"),
            temperature=kwargs.get("temperature"),
            use_tools=kwargs.get("use_tools", False),
        )
        self._build(config)

    @classmethod
    def from_config(cls, config: RunnerConfig) -> "BasicJudgedDebateRunner":
        instance = cls.__new__(cls)
        instance._build(config)
        return instance

    def _build(self, config: RunnerConfig):
        self.debate = JudgedDebate(motion=config.motion, epochs=config.epochs)
        mp = config.model_params()

        used_names: set = set()
        name1 = generate_name(used_names); used_names.add(name1)
        name2 = generate_name(used_names); used_names.add(name2)

        d1_kw = {"name": name1, "motion": config.motion, "stance": "for", "llm_provider": config.llm}
        d2_kw = {"name": name2, "motion": config.motion, "stance": "against", "llm_provider": config.llm}
        if config.debater_prompt:
            d1_kw["instruction_prompt"] = config.debater_prompt
            d2_kw["instruction_prompt"] = config.debater_prompt
        d1_kw.update(mp); d2_kw.update(mp)

        judge_name = generate_name(used_names); used_names.add(judge_name)
        bd_name = generate_name(used_names); used_names.add(bd_name)
        j_kw = {"name": judge_name, "motion": config.motion, "llm_provider": config.llm}
        bd_kw = {"name": bd_name, "motion": config.motion, "llm_provider": config.llm}
        if config.judge_prompt:
            bd_kw["instruction_prompt"] = config.judge_prompt
        j_kw.update(mp); bd_kw.update(mp)

        DebaterClass = ToolEnabledDebater if config.use_tools else Debater
        self.debate.add_debaters(DebaterClass(**d1_kw))
        self.debate.add_debaters(DebaterClass(**d2_kw))
        self.debate.add_judge(DynamicExpertJudge(**j_kw))
        self.debate.add_judge(BullshitDetector(**bd_kw))

        mod_name = generate_name(used_names)
        self.debate.add_moderator(Moderator(name=mod_name, motion=config.motion, llm_provider=config.llm, **mp))

    def run_debate(self):
        for msg in self.debate.debate():
            yield msg

    def get_judgements(self):
        judgements = []
        for judge in self.debate.judges:
            resp = judge.summarize_judgement()
            score, judgement = self.debate.parse_judgement(resp)
            judgements.append((judge.name, score, judgement))
        return judgements


class BasicSimpleDebateRunner(DebateRunner):
    """Execute a basic debate with two debaters, no judges."""

    def __init__(self, motion: str, epochs: int = 2, llm: str = "openai", **kwargs):
        config = RunnerConfig(
            motion=motion,
            epochs=epochs,
            llm=llm,
            debater_prompt=kwargs.get("debater_prompt"),
            model=kwargs.get("model"),
            temperature=kwargs.get("temperature"),
            use_tools=kwargs.get("use_tools", False),
        )
        self._build(config)

    @classmethod
    def from_config(cls, config: RunnerConfig) -> "BasicSimpleDebateRunner":
        instance = cls.__new__(cls)
        instance._build(config)
        return instance

    def _build(self, config: RunnerConfig):
        self.debate = SimpleDebate(motion=config.motion, epochs=config.epochs)
        mp = config.model_params()

        used_names: set = set()
        name1 = generate_name(used_names); used_names.add(name1)
        name2 = generate_name(used_names)

        d1_kw = {"name": name1, "motion": config.motion, "stance": "for", "llm_provider": config.llm}
        d2_kw = {"name": name2, "motion": config.motion, "stance": "against", "llm_provider": config.llm}
        if config.debater_prompt:
            d1_kw["instruction_prompt"] = config.debater_prompt
            d2_kw["instruction_prompt"] = config.debater_prompt
        d1_kw.update(mp); d2_kw.update(mp)

        DebaterClass = ToolEnabledDebater if config.use_tools else Debater
        self.debate.add_debaters(DebaterClass(**d1_kw))
        self.debate.add_debaters(DebaterClass(**d2_kw))

    def run_debate(self):
        for msg in self.debate.debate():
            yield msg


class ExpertPanelRunner(DebateRunner):
    """Expert panel discussion — no stances, goal is convergence toward a nuanced answer."""

    def __init__(self, config: RunnerConfig, domains: Optional[List[str]] = None):
        domains = domains or config.domains or DEFAULT_PANEL_DOMAINS
        self.debate = ExpertPanelDebate(motion=config.motion, epochs=config.epochs)
        mp = config.model_params()

        used_names: set = set()
        for domain in domains:
            name = generate_name(used_names); used_names.add(name)
            self.debate.add_debaters(
                PanelParticipant(name=name, motion=config.motion, domain=domain,
                                 llm_provider=config.llm, **mp)
            )

        judge_name = generate_name(used_names); used_names.add(judge_name)
        self.debate.add_judge(
            Judge(name=judge_name, motion=config.motion,
                  instruction_prompt=PANEL_JUDGE_PROMPT, llm_provider=config.llm, **mp)
        )

        mod_name = generate_name(used_names)
        self.debate.add_moderator(
            Moderator(name=mod_name, motion=config.motion, llm_provider=config.llm, **mp)
        )

    def run_debate(self):
        for msg in self.debate.debate():
            yield msg
