# AutoDebater

[![Coverage Status](https://coveralls.io/repos/github/nrlewis/autodebater/badge.svg?branch=main)](https://coveralls.io/github/nrlewis/autodebater?branch=main)
![GitHub Release](https://img.shields.io/github/v/release/nrlewis/autodebater)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/nrlewis/autodebater/cicd.yaml)
![GitHub License](https://img.shields.io/github/license/nrlewis/autodebater)

AutoDebater is a Python library and CLI for engaging Large Language Models (LLMs) in structured debates. It allows for the creation and management of debates between LLMs, including the ability to judge and score the arguments presented.

> **Note:** This project is a work in progress. Contributions and feedback are welcome!

## Features

- **Library and CLI**: Engage with LLMs in debates programmatically or via the command line.
- **Multiple Roles**: Support for debaters and judges, with configurable prompts and behaviors.
- **Extensible**: Designed to be extended with different LLM backends.

## Installation

### Pip

You can install AutoDebater using pip:

```sh
pip install autodebater
```

### Poetry for Development

AutoDebater uses Poetry for dependency management. You can install it with the following steps:

1. Install Poetry if you haven't already:

   ```sh
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Add to your project

   ```sh
   git clone https://github.com/nrlewis/autodebater.git
   cd autodebater
   ```

3. Install dependencies:

   ```sh
   poetry install
   ```

## Setup

Before using AutoDebater, you need to set your keys:

### OpenAI

If using OpenAI:

```sh
export OPENAI_API_KEY="your_openai_api_key"
```

### Azure OpenAI

If using Azure, you must set several environment variables:

```sh
export AZURE_OPENAI_API_KEY="your_azure_api_key"
export AZURE_OPENAI_ENDPOINT="your_azure_api_endpoint"
export AZURE_OPENAI_API_VERSION="you_azure_api_version"
export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="your_azure_model_deployment_name"
```

## Usage

### CLI

You can use the CLI to start a debate. For example:

```
 Usage: autodebater [OPTIONS] COMMAND [ARGS]...

Options:
 --install-completion          Install completion for the current shell.                                                                                                                                            │
 --show-completion             Show completion for the current shell, to copy it or customize the installation.                                                                                                     │
 --help                        Show this message and exit.                                                                                                                                                          │

Commands:
 judged-debate   Start a new debate with the given motion and epochs.                                                                                                                                               │
 simple-debate   Start a new debate with the given motion and epochs.                                                                                                                                               │
```

### Example Usage

#### Full CLI

```sh
autodebater judged-debate "AI will surpass human intelligence" --epochs 2
```

#### With Poetry

```sh
poetry run autodebater judged-debate "AI will surpass human intelligence" --epochs 2
```

## Debates

There are two types of debates, Simple and Judged.

### Simple Debate

A simple debate is just two debaters debating each other. One debater is FOR the motion passed, and the other is AGAINST the motion.

The debate will run as many epochs as passed in the CLI (default 2).

### Judged Debate

A simple debate with judges listening. One judge is prompted to be an expert on the topic, and the other is a Bullshit Detector, prompted to sniff out logical fallacies.

The debate will run for the number of epochs passed in the CLI (default 2). While the debate goes on, the judges will keep an internal score and their interpretation of the debate as a whole.
After the epochs are completed, the judges will summarize their interpretations of the entire debate.

### Scoring

The score is set such that a score closer to zero means the judges are AGAINST the motion, and a score closer to 100 means they are FOR the motion.
There is a running score showing the geometric mean of the score.

## Architecture

The library orchestrates LLM debates through four layers:

### LLM Layer

`LLMWrapper` (ABC) → `OpenAILLMWrapper` / `AzureOpenAILLMWrapper`, selected via `LLMWrapperFactory`. Both use `langchain-openai` under the hood. The factory key is the `llm_provider` string (`"openai"` or `"azure"`), passed via the `--llm` CLI flag or the `llm_provider` constructor argument.

### Participants Layer

`Participant` (ABC) holds a `chat_history` list of `(role, content)` tuples that grows as the debate progresses. Each participant owns its own `LLMWrapper` instance.

- **Debater** — argues for or against a motion; its stance is embedded in the system prompt.
- **Judge** — scores each round (0–100) and produces a `summarize_judgement()` at the end.
- **BullshitDetector** — a `Judge` subclass with a logical-fallacy-focused system prompt.

### Debate Layer

`Debate` (ABC) manages `DialogueHistory` and iterates over debaters for `epochs` rounds, **yielding** `DialogueMessage` objects (generator pattern).

- **SimpleDebate** — two debaters, round-robin message passing.
- **JudgedDebate** — after each debater turn all judges score that message; a running geometric-mean score is tracked.

`DebateRunner` subclasses (`BasicJudgedDebateRunner`, `BasicSimpleDebateRunner`) wire up the default set of participants and expose `run_debate()` and (for judged) `get_judgements()`.

### Dialogue Layer

- **DialogueMessage** — dataclass representing one message (name, role, stance, judgement score, message text, debate_id).
- **DialogueHistory** — simple list accumulator.
- **DialogueConverter** — translates `DialogueMessage` objects into `(role, content)` tuples for the LLM; judge messages are stripped out so debaters never see judge scores.

### Library

You can also use AutoDebater as a library:

```python
from autodebater.debate import JudgedDebate
from autodebater.participants import Debater, Judge

debate = JudgedDebate(motion="AI will surpass human intelligence", epochs=2)
debate.add_debaters(Debater(name="Debater1", motion="AI will surpass human intelligence", stance="for"))
debate.add_debaters(Debater(name="Debater2", motion="AI will surpass human intelligence", stance="against"))
debate.add_judge(Judge(name="Judge1", motion="AI will surpass human intelligence"))

for message in debate.debate():
    print(message)
```

## Configuration

### Modifying Prompts

The prompts used by AutoDebater can be modified by editing the `src/autodebater/defaults.yaml` file. This allows you to customize the behavior and responses of the debaters and judges to better fit your specific use case.

### pyproject.toml

This file contains the configuration for Poetry, including dependencies and build settings.

### Adding Participants

You can increase or decrease the number of participants: debaters and judges.

## TODOs

1. ~~Extend LLMWrapper for Azure OpenAI~~ (done) — extend for Claude
2. AutoGenerate Names
3. Insert Moderator for a moderated debate
4. Allow prompt configuration from CLI
5. Dynamically set judge expertise based on topic of motion rather than "you are an expert on this motion"
6. Prompt judegs to consider their expertise more than debate structure
7. Review scoring mechanism and alignment with prompt strategy
8. Configure with backend for saving debates
9. Configure with Langchain actions, allowing debaters to pull information from external sources

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Write tests for your changes.
4. Ensure all tests pass.
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Changelog

See the [CHANGELOG](./CHANGELOG.md) file for a detailed list of changes and updates.

## Contact

For any questions or issues, please open an issue on GitHub.
