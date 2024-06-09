"""
Integration test using openai backend.  Requires
OPENAI_API_KEY to be set
"""

import json
import logging
import os

import pytest

from autodebater.dialogue import DialogueMessage
from autodebater.participants import Debater

logger = logging.getLogger(__name__)


@pytest.mark.skip
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
def test_openai_integration():
    # Create a Debater instance with actual OpenAI integration
    logger.info("Creating a Debater instance with OpenAI integration")
    name = "Debater1"
    role_prompt = (
        "You are a debater arguing "
        + "FOR the motion that charcoals bbq is better than gas."
    )
    llm_provider = "openai"
    model_params = {"model": "gpt-4o", "param2": "value2"}

    debater = Debater(name, role_prompt, llm_provider, **model_params)

    # Define the most recent chats
    most_recent_chats = [
        DialogueMessage(
            name="joe",
            role="debater",
            debate_id="integration_test",
            message="charcoal bbqs suck",
        )
    ]

    # Call the respond method
    response = debater.respond(most_recent_chats)
    # Verify the response is a non-empty string (as an example)
    assert isinstance(response, str)
    assert len(response) > 0
    assert "bbq" in response.lower()


@pytest.mark.skip
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
def test_openai_121_conversation():
    def role_prompt(name, position, motion):
        prompt = f"""Your name is {name}.
                    You are debating the user {position} the motion that {motion}

                     You will receive your opponents dialogue in the following format:
                     <USER_NAME> (USER_ROLE): <USER_MESSAGE>\n\n
                     Below is an example\n\n
                     james (debater): I think that the sky is falling

                     Response with only text, do not mimic the format you are receiving.
                     """
        return prompt

    motion = "you like green eggs and ham"
    d1_name = "Sam I Am"
    d1_role = role_prompt(d1_name, "for", motion)
    sam_i_am = Debater(d1_name, d1_role, "openai")

    d1_name = "joe"
    d1_role = role_prompt(d1_name, "against", motion)
    joe = Debater(d1_name, d1_role, "openai")

    debaters = [sam_i_am, joe]
    dialogue = []
    history = []
    i = 0
    while i < 6:
        debater = debaters[i % len(debaters)]
        response = debater.respond(dialogue)
        message = DialogueMessage(debater.name, debater.role, response, "integration")
        history.append(message)
        dialogue = [message]
        i += 1

    # this test is just assure that passing messages with openai doesn't fail.
    # the content is unpredictable, so if we got this far, we're good
    logging.info("DIALOGUE:\n%s", json.dumps([d.to_dict() for d in history], indent=2))
    assert True
