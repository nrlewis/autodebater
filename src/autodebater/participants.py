"""
This module contains all of the different members with roles within an debate.
Each member extends the Abstract class Participant
Participant:  Initializes to an LLMWrapper with model parameters
Debater - the agent participating in a debate
Judge - an audience member within the debate that judges in realtime the
    each debator's respone and gauges which side they are more
    confident about
# TODO:
Moderator - an member which can set the question for the debate

The difference between the participants is as follows:
- All Participants have a unique system message
- Debators need to read the entire chat history, with appropriate
   indexing on user versus assistant prompting
- Judges read the entire chat history as part of its prompt.
"""

import logging
from abc import ABC

from autodebater.defaults import (BULLSHIT_DETECTOR_PROMPT, DEBATER_PROMPT,
                                  EXPERT_JUDGE_PROMPT, JUDGE_SUMMARY,
                                  LLM_PROVIDER)
from autodebater.dialogue import DialogueConverter, DialogueMessage
from autodebater.llm import LLMWrapperFactory

logger = logging.getLogger(__name__)


class Participant(ABC):
    """
    Abstract class for each participant.  initialization
    sets the model to be used, and the system prompt
    message for each model.
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        role: str,
        llm_provider: str,
        **model_params,
    ):

        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.llm_provider = llm_provider
        self.model_params = model_params

        self.llm = LLMWrapperFactory.create_llm_wrapper(
            llm_provider, **self.model_params
        )
        self.message_converter = DialogueConverter()
        system_msg = ("system", self.system_prompt)
        self.chat_history = [system_msg]

    def _update_chat_history(self, messages):
        self.chat_history.extend(messages)

    def respond(self, most_recent_chats: list[DialogueMessage]):
        """This method  updates the chat history the ongoing dialogue."""
        converted_chats = self.message_converter.convert_messages(most_recent_chats)
        self._update_chat_history(converted_chats)
        response = self.llm.generate_text_from_messages(self.chat_history)
        self._update_chat_history([("assistant", response)])
        return response


class Debater(Participant):
    """
    The Debater class sets the appropriate prompts for the llm,
    and controls the message passing to and from the llm.
    """

    def __init__(
        self,
        name: str,
        motion: str,
        stance: str,
        instruction_prompt: str = DEBATER_PROMPT,
        llm_provider: str = LLM_PROVIDER,
        **model_params,
    ):
        self.stance = stance
        system_prompt = instruction_prompt.format(motion=motion, stance=stance)
        super().__init__(name, system_prompt, "debater", llm_provider, **model_params)


class Judge(Participant):
    """
    Judges return only a score after listening to the debate
    """

    def __init__(
        self,
        name: str,
        motion: str,
        instruction_prompt: str = EXPERT_JUDGE_PROMPT,
        llm_provider: str = LLM_PROVIDER,
        **model_params,
    ):
        system_prompt = instruction_prompt.format(motion=motion)
        super().__init__(name, system_prompt, "judge", llm_provider, **model_params)

    def summarize_judgement(self):
        """
        Instructs the LLM to produce a summary and judgement of this judge's position
        """
        prompt = ("user", JUDGE_SUMMARY)
        self._update_chat_history([prompt])
        response = self.llm.generate_text_from_messages(self.chat_history)
        self._update_chat_history([("assistant", response)])
        return response


class BullshitDetector(Judge):
    """
    Specific type of judge encapsulated in a class
    Throws a pylint error for useless parent, however the parent here sets
    a default prompt, so ignoring the error
    """

    def __init__(  # pylint: disable=useless-parent-delegation
        self,
        name: str,
        motion: str,
        instruction_prompt: str = BULLSHIT_DETECTOR_PROMPT,
        llm_provider: str = LLM_PROVIDER,
        **model_params,
    ):
        super().__init__(name, motion, instruction_prompt, llm_provider, **model_params)
