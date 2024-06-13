````markdown
# AutoDebater

[![Coverage Status](https://coveralls.io/repos/github/nrlewis/autodebater/badge.svg?branch=main)](https://coveralls.io/github/nrlewis/autodebater?branch=main)
![GitHub Release](https://img.shields.io/github/v/release/nrlewis/autodebater)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/nrlewis/autodebater/pylint.yml)
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
````

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

Before using AutoDebater, you need to set your OpenAI API key:

```sh
export OPENAI_API_KEY="your_openai_api_key"
```

## Usage

### CLI

You can use the CLI to start a debate. For example:

```sh
poetry run autodebater judged_debate "AI will surpass human intelligence" --epochs 2
```

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

The prompts used by AutoDebater can be modified by editing the `defaults.yaml` file. This allows you to customize the behavior and responses of the debaters and judges to better fit your specific use case.

### pyproject.toml

This file contains the configuration for Poetry, including dependencies and build settings.

### .pylintrc

The Pylint configuration file is set up to follow the Google Python style guide and includes several custom rules and settings.

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

```

```
