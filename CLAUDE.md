# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```sh
# Install dependencies
poetry install

# Run unit tests (excludes integration tests)
poetry run pytest -m 'not integration' -vv
# or via make
make test

# Run a single test file
PYTHONPATH=src poetry run pytest tests/unit/test_debate.py -vv

# Run integration tests (requires live API keys)
make integration

# Lint
make lint  # runs: poetry run pylint src tests

# Coverage report
make coverage

# Build the package
poetry build  # or: make dist

# Quick end-to-end check (requires OPENAI_API_KEY)
make quick_check
```

Commits follow Angular convention (`feat`, `fix`, `build`, `chore`, `ci`, `docs`, `perf`, `style`, `refactor`, `test`). Versioning is managed by `python-semantic-release` — do not bump versions manually.

Code is formatted with **black** (enforced via pre-commit). Run `pre-commit install` once after cloning.

## Architecture

The library orchestrates LLM debates through three layers:

### 1. LLM Layer (`llm.py`)
`LLMWrapper` (ABC) → `OpenAILLMWrapper` / `AzureOpenAILLMWrapper`, selected via `LLMWrapperFactory`. Both use `langchain-openai` under the hood. The factory key is the `llm_provider` string (`"openai"` or `"azure"`).

### 2. Participants Layer (`participants.py`)
`Participant` (ABC) holds a `chat_history` list of `(role, content)` tuples that grows as the debate progresses. Each participant owns its own `LLMWrapper` instance.
- `Debater` — argues for or against a motion; its `stance` is embedded in the system prompt.
- `Judge` — scores each round (0–100) and can produce a `summarize_judgement()` at the end.
- `BullshitDetector` — a `Judge` subclass with a logical-fallacy-focused system prompt.

All prompts originate from `defaults.yaml` and are loaded into constants in `defaults.py`.

### 3. Debate Layer (`debate.py` + `debate_runners.py`)
`Debate` (ABC) manages `DialogueHistory` and iterates over debaters for `epochs` rounds, **yielding** `DialogueMessage` objects (generator pattern).
- `SimpleDebate` — two debaters, round-robin message passing.
- `JudgedDebate` — same as simple, but after each debater turn all judges score that message, and a running geometric-mean score is tracked.

`DebateRunner` subclasses (`BasicJudgedDebateRunner`, `BasicSimpleDebateRunner`) wire up the default set of participants and expose `run_debate()` and (for judged) `get_judgements()`.

### 4. Dialogue Layer (`dialogue.py`)
- `DialogueMessage` — dataclass representing one message (name, role, stance, judgement score, message text, debate_id).
- `DialogueHistory` — simple list accumulator.
- `DialogueConverter` — translates `DialogueMessage` objects into `(role, content)` tuples for the LLM; judge messages are stripped out so debaters never see judge scores.

### 5. CLI (`run_debates.py`)
Typer app with two commands (`judged-debate`, `simple-debate`). Renders output as Rich live tables. Entry point configured in `pyproject.toml` as `autodebater = "autodebater.run_debates:app"`.

## Key Configuration

- **`src/autodebater/defaults.yaml`** — default LLM provider, model params, and all system prompts. Edit this to change debater/judge behavior without touching Python.
- **`src/autodebater/defaults.py`** — loads `defaults.yaml` and exposes constants (`DEBATER_PROMPT`, `EXPERT_JUDGE_PROMPT`, `BULLSHIT_DETECTOR_PROMPT`, `JUDGE_SUMMARY`, `LLM_PROVIDER`, `OPENAI_MODEL_PARAMS`).
- Test markers: `integration` tests require live API keys and are excluded from `make test`.

## Adding a New LLM Backend

1. Subclass `LLMWrapper` in `llm.py`, implementing `generate_text_from_messages`.
2. Register the new class in `LLMWrapperFactory.llms` dict with a string key.
3. Pass that key as `llm_provider` when constructing participants or via the `--llm` CLI flag.
