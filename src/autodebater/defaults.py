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
SYSTEM_PROMPTS = defaults["system_prompts"]

# Optional: Define specific prompts for convenience
DEBATER_PROMPT = SYSTEM_PROMPTS["debater"]
JUDGE_INSTRUCTION = SYSTEM_PROMPTS["judge_instruction"]
JUDGE_SUMMARY = SYSTEM_PROMPTS["judge_summary"]

EXPERT_JUDGE_PROMPT = SYSTEM_PROMPTS["expert_judge"] + "\n" + JUDGE_INSTRUCTION
BULLSHIT_DETECTOR_PROMPT = (
    SYSTEM_PROMPTS["bullshit_detector"] + "\n" + JUDGE_INSTRUCTION
)
