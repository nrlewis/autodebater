"""
Unit test the dialogue conversions
"""

from autodebater.dialogue import DialogueConverter, DialogueMessage


def test_debate_convert_small():
    msg = DialogueMessage(
        name="suess",
        role="moderator",
        message="sam I am, start the discussion",
        debate_id="12345",
    )

    expected = (
        "user",
        "suess (moderator - NEUTRAL): sam I am, start the discussion",
    )

    ddc = DialogueConverter()
    converted = ddc.convert_message(msg)

    assert expected == converted
