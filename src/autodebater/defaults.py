"""
Loads all defaults from the defaults.yaml file
and converts them to constants
"""

import os

from yaml import safe_load

DEFAULTS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "defaults.yaml")
)

defaults = safe_load(open(DEFAULTS_PATH, encoding="utf-8").read())

# Extract values from the YAML content
LLM_PROVIDER = defaults["llm_provider"]
OPENAI_MODEL_PARAMS = defaults["openai_model_params"]
AZURE_OPENAI_MODEL_PARAMS = defaults["azure_openai_model_params"]
ANTHROPIC_MODEL_PARAMS = defaults["anthropic_model_params"]
SYSTEM_PROMPTS = defaults["system_prompts"]

# Optional: Define specific prompts for convenience
DEBATER_PROMPT = SYSTEM_PROMPTS["debater"]
JUDGE_INSTRUCTION = SYSTEM_PROMPTS["judge_instruction"]
JUDGE_SUMMARY = SYSTEM_PROMPTS["judge_summary"]

EXPERT_JUDGE_PROMPT = SYSTEM_PROMPTS["expert_judge"] + "\n" + JUDGE_INSTRUCTION
BULLSHIT_DETECTOR_PROMPT = (
    SYSTEM_PROMPTS["bullshit_detector"] + "\n" + JUDGE_INSTRUCTION
)

PANEL_PARTICIPANT_PROMPT = SYSTEM_PROMPTS["panel_participant"]
# Panel judge uses its own convergence rubric (0=diverged, 100=synthesised), not FOR/AGAINST.
PANEL_JUDGE_PROMPT = SYSTEM_PROMPTS["panel_judge"]

MODERATOR_SYSTEM_PROMPT = SYSTEM_PROMPTS["moderator_system"]
MODERATOR_OPENING_PROMPT = SYSTEM_PROMPTS["moderator_opening"]
MODERATOR_QUESTION_PROMPT = SYSTEM_PROMPTS["moderator_question"]
MODERATOR_CLOSING_PROMPT = SYSTEM_PROMPTS["moderator_closing"]
DYNAMIC_EXPERT_JUDGE_PROMPT = SYSTEM_PROMPTS["dynamic_expert_judge"] + "\n" + JUDGE_INSTRUCTION

PANEL_MODERATOR_SYSTEM_PROMPT = SYSTEM_PROMPTS["panel_moderator_system"]
PANEL_MODERATOR_OPENING_PROMPT = SYSTEM_PROMPTS["panel_moderator_opening"]
PANEL_MODERATOR_QUESTION_PROMPT = SYSTEM_PROMPTS["panel_moderator_question"]
PANEL_MODERATOR_CLOSING_PROMPT = SYSTEM_PROMPTS["panel_moderator_closing"]
