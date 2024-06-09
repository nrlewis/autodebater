"""
Module for wrappring LLM function calls.
Containts an LLM Abstract class with inheritance
for the different LLM python sdk implemtnations like openai or
anthropic
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import List, Tuple

# from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from autodebater.defaults import OPENAI_MODEL_PARAMS

logger = logging.getLogger(__name__)


class LLMWrapper(ABC):
    """
    Abstract class for wrapping LLM function calls
    """

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def generate_text_from_messages(
        self, messages: List[Tuple[str, str]], *args, **kwargs
    ) -> str:
        pass


class OpenAILLMWrapper(LLMWrapper):
    """
    OpenAI LLM Wrapper
    Uses langchain for extendability
    """

    def __init__(self, **model_params):

        self.model_params = model_params
        if len(self.model_params) == 0:
            self.model_params = OPENAI_MODEL_PARAMS
            logger.info("Setting OpenAI model params to %s", self.model_params)

        if os.getenv("OPENAI_API_KEY", None) is None:
            raise ValueError("OPENAI_API_KEY is not set")

        # assumes key is set as env var
        self.llm = ChatOpenAI(**self.model_params)
        super().__init__()

    def generate_text_from_messages(self, messages: List[Tuple[str, str]]) -> str:

        ai_msg = self.llm.invoke(messages)
        return ai_msg.content


class LLMWrapperFactory:
    """LLM Wrapper Factory Design"""

    llms = {"openai": OpenAILLMWrapper}

    @staticmethod
    def create_llm_wrapper(llm_type: str, **model_params):
        """
        Factory method for creating LLMWrapper objects
        """
        return LLMWrapperFactory.llms[llm_type](**model_params)
