"""
pytest for the llm module
"""

from autodebater.llm import LLMWrapperFactory, OpenAILLMWrapper


def test_openai_llm_wrapper():
    openai_llm = OpenAILLMWrapper()
    assert openai_llm is not None


def test_llm_wrapper_factory():
    openai_llm = LLMWrapperFactory.create_llm_wrapper("openai", model="gpt-4o")
    assert isinstance(openai_llm, OpenAILLMWrapper)
