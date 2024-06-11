"""
This module contains relevant classes for the diagloue -

Dialogue History contains all instance of diaglogue that are being
passed back and forth between Participants

A DialogueMessage is the message format for what is being passed arround
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple


@dataclass
class DialogueMessage:
    name: str
    role: str
    message: str
    debate_id: str
    stance: str = "neutral"
    judgement: float | None = None  # default
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "name": self.name,
            "role": self.role,
            "stance": self.stance,
            "judgement": self.judgement,
            "message": self.message,
            "debate_id": self.debate_id,
        }


class DialogueHistory:
    def __init__(self):
        self.messages = []

    def add_message(self, message: DialogueMessage):
        self.messages.append(message)

    def get_history(self):
        return self.messages


class DialogueConverter(object):
    """
    Dialogue Convert class is responsible for converting Dialogue Message format
    to Participant specific formats.

    We want the debater or judge to consider this a conversation,
    so each message to them contains their opponents position,
    and we want the judges to also consider the debater's position as well
    """

    def __init__(self):
        self.role_conversion = {"debater": "user", "moderator": "user"}

    def convert_message(self, message: DialogueMessage) -> Tuple:
        """
        Convert the chat history to the format required by the LLM
        The messages are in the form:
        {"role":"debater", "name":"joe",  "message":"I disagree"}
        convert this list into the relevant format for OpenAI:
        ("human", "joe (debater - FOR): I disagree")
        """
        # ignore judges
        if message.role == "judge":
            return ()

        content = (
            f"{message.name} ({message.role} - {message.stance.upper()}): "
            + f"{message.message}"
        )
        return (self.role_conversion[message.role], content)

    def convert_messages(
        self, messages: List[DialogueMessage]
    ) -> List[Tuple[str, str]]:

        converted_messages = []
        for message in messages:
            converted = self.convert_message(message)
            if len(converted) > 0:
                converted_messages.append(converted)

        return converted_messages
