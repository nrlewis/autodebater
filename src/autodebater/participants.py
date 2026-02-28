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
                                  DYNAMIC_EXPERT_JUDGE_PROMPT, EXPERT_JUDGE_PROMPT,
                                  JUDGE_SUMMARY, LLM_PROVIDER,
                                  MODERATOR_CLOSING_PROMPT, MODERATOR_OPENING_PROMPT,
                                  MODERATOR_QUESTION_PROMPT, MODERATOR_SYSTEM_PROMPT,
                                  PANEL_PARTICIPANT_PROMPT)
from autodebater.dialogue import DialogueConverter, DialogueHistory, DialogueMessage
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


class Moderator(Participant):
    """
    Moderator frames the debate, asks follow-up questions, and provides a closing summary.
    """

    def __init__(
        self,
        name: str,
        motion: str,
        llm_provider: str = LLM_PROVIDER,
        **model_params,
    ):
        self.motion = motion
        system_prompt = MODERATOR_SYSTEM_PROMPT.format(motion=motion)
        super().__init__(name, system_prompt, "moderator", llm_provider, **model_params)

    def opening_statement(self) -> str:
        prompt = MODERATOR_OPENING_PROMPT.format(motion=self.motion)
        self._update_chat_history([("user", prompt)])
        response = self.llm.generate_text_from_messages(self.chat_history)
        self._update_chat_history([("assistant", response)])
        return response

    def generate_question(self, history: DialogueHistory) -> str:
        converted = self.message_converter.convert_messages(history.get_history())
        self._update_chat_history(converted)
        self._update_chat_history([("user", MODERATOR_QUESTION_PROMPT)])
        response = self.llm.generate_text_from_messages(self.chat_history)
        self._update_chat_history([("assistant", response)])
        return response

    def closing_statement(self, history: DialogueHistory) -> str:
        converted = self.message_converter.convert_messages(history.get_history())
        self._update_chat_history(converted)
        self._update_chat_history([("user", MODERATOR_CLOSING_PROMPT)])
        response = self.llm.generate_text_from_messages(self.chat_history)
        self._update_chat_history([("assistant", response)])
        return response


class DynamicExpertJudge(Judge):
    """
    A Judge that lazily discovers its domain of expertise on the first respond() call.
    Construction never makes LLM calls — expertise is deferred until actually needed.
    """

    def __init__(
        self,
        name: str,
        motion: str,
        llm_provider: str = LLM_PROVIDER,
        **model_params,
    ):
        self._expertise = None
        self._motion = motion
        # Start with the base expert judge prompt; upgraded after expertise discovery.
        super().__init__(name, motion, llm_provider=llm_provider, **model_params)

    def _discover_expertise(self):
        expertise_prompt = [
            ("system", "You are a domain expert."),
            (
                "user",
                f"What is your primary domain of expertise most relevant to the motion: "
                f"'{self._motion}'? Answer in one short phrase (e.g. 'machine learning and AI ethics').",
            ),
        ]
        self._expertise = self.llm.generate_text_from_messages(expertise_prompt).strip()
        logger.info("DynamicExpertJudge '%s' expertise: %s", self.name, self._expertise)
        new_system = DYNAMIC_EXPERT_JUDGE_PROMPT.format(
            motion=self._motion, expertise=self._expertise
        )
        self.chat_history[0] = ("system", new_system)
        self.system_prompt = new_system

    @property
    def expertise(self):
        return self._expertise

    def respond(self, most_recent_chats: list):
        if self._expertise is None:
            self._discover_expertise()
        return super().respond(most_recent_chats)


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


class ToolEnabledDebater(Debater):
    """
    A Debater that can use LangChain tools (e.g. Wikipedia, DuckDuckGo) to support arguments.
    Uses a ReAct-style agent loop via langchain.
    """

    def __init__(
        self,
        name: str,
        motion: str,
        stance: str,
        instruction_prompt: str = DEBATER_PROMPT,
        llm_provider: str = LLM_PROVIDER,
        tools: list = None,
        **model_params,
    ):
        super().__init__(name, motion, stance, instruction_prompt, llm_provider, **model_params)
        if tools is None:
            from autodebater.tools import get_default_tools
            tools = get_default_tools()
        self.tools = tools
        if self.tools:
            try:
                self.llm.llm = self.llm.llm.bind_tools(self.tools)
            except Exception as exc:  # pragma: no cover
                logger.warning("Could not bind tools to LLM: %s", exc)

    def respond(self, most_recent_chats: list):
        """Respond using a tool-augmented ReAct loop."""
        converted_chats = self.message_converter.convert_messages(most_recent_chats)
        self._update_chat_history(converted_chats)

        if not self.tools:
            response = self.llm.generate_text_from_messages(self.chat_history)
            self._update_chat_history([("assistant", response)])
            return response

        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

        # Build langchain messages from chat history tuples
        lc_messages = []
        for role, content in self.chat_history:
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role in ("user", "human"):
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))

        max_iterations = 5
        for _ in range(max_iterations):
            ai_msg = self.llm.llm.invoke(lc_messages)
            lc_messages.append(ai_msg)

            if not getattr(ai_msg, "tool_calls", None):
                # Final answer
                final_text = ai_msg.content
                self._update_chat_history([("assistant", final_text)])
                return final_text

            # Execute tool calls
            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                matched = next((t for t in self.tools if t.name == tool_name), None)
                if matched:
                    try:
                        tool_result = matched.run(tool_args)
                    except Exception as exc:  # pragma: no cover
                        tool_result = f"Tool error: {exc}"
                else:
                    tool_result = f"Tool '{tool_name}' not found."
                lc_messages.append(
                    ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
                )

        # Fallback: return the last AI content
        final_text = lc_messages[-1].content if lc_messages else ""
        self._update_chat_history([("assistant", final_text)])
        return final_text


class PanelParticipant(Participant):
    """
    Expert panel participant with a specific domain lens.
    Has no stance — goal is to contribute domain expertise toward a nuanced synthesis.
    """

    def __init__(
        self,
        name: str,
        motion: str,
        domain: str,
        llm_provider: str = LLM_PROVIDER,
        **model_params,
    ):
        self.domain = domain
        system_prompt = PANEL_PARTICIPANT_PROMPT.format(motion=motion, domain=domain)
        super().__init__(name, system_prompt, "panelist", llm_provider, **model_params)
