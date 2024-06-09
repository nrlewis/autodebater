"""
Custom Exceptions
"""


class LLMParsingError(Exception):
    pass


class JudgementParseError(LLMParsingError):
    pass
