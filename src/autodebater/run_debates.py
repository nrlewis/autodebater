"""
CLI entry point for debates
"""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.table import Table

from autodebater.debate_runners import (BasicJudgedDebateRunner, BasicSimpleDebateRunner,
                                        ExpertPanelRunner, RunnerConfig)
from autodebater.dialogue import DialogueMessage
from autodebater.persistence import DebateExporter
from autodebater.profile import ProfileStore

app = typer.Typer()


def msg2table(msg: DialogueMessage):
    table = Table("name", "role", "message")
    table.add_row(msg.name, msg.role, msg.message)
    return table


def _load_context(context_file: Optional[str], no_profile: bool) -> Optional[str]:
    """Return context text from --context-file, or auto-load profile, or None."""
    if context_file:
        return Path(context_file).read_text(encoding="utf-8").strip()
    if not no_profile:
        return ProfileStore().load()
    return None


@app.command()
def judged_debate(
    motion: str,
    epochs: int = 2,
    llm: str = "openai",
    debater_prompt: Optional[str] = typer.Option(None, "--debater-prompt", help="Override debater system prompt"),
    judge_prompt: Optional[str] = typer.Option(None, "--judge-prompt", help="Override judge system prompt"),
    model: Optional[str] = typer.Option(None, "--model", help="Override the model name"),
    temperature: Optional[float] = typer.Option(None, "--temperature", help="Override the model temperature"),
    save: bool = typer.Option(False, "--save/--no-save", help="Persist debate to SQLite"),
    output_file: Optional[str] = typer.Option(None, "--output-file", help="Export debate to file (json or md)"),
    use_tools: bool = typer.Option(False, "--use-tools/--no-use-tools", help="Enable LangChain tool use for debaters"),
    context_file: Optional[str] = typer.Option(None, "--context-file", help="Path to a text/markdown file injected as context"),
    no_profile: bool = typer.Option(False, "--no-profile", help="Skip auto-loading the persistent profile"),
):
    """Start a new judged debate with the given motion and epochs."""
    runner_kwargs = {"context": _load_context(context_file, no_profile)}
    if debater_prompt:
        runner_kwargs["debater_prompt"] = debater_prompt
    if judge_prompt:
        runner_kwargs["judge_prompt"] = judge_prompt
    if model:
        runner_kwargs["model"] = model
    if temperature is not None:
        runner_kwargs["temperature"] = temperature
    if use_tools:
        runner_kwargs["use_tools"] = True

    debate_runner = BasicJudgedDebateRunner(motion=motion, epochs=epochs, llm=llm, **runner_kwargs)

    typer.echo(f"Starting debate on: {motion}")

    table = Table("name", "role", "stance", "judgement", "message", show_lines=True)
    with Live(table, auto_refresh=False, vertical_overflow="visible") as live:
        for msg in debate_runner.run_debate():
            table.add_row(
                msg.name,
                msg.role,
                msg.stance,
                str(msg.judgement),
                Markdown(msg.message),
            )
            live.update(table, refresh=True)

    table = Table("Judge Name", "score", "judgement")
    with Live(table, auto_refresh=False, vertical_overflow="visible") as live:
        for msg in debate_runner.get_judgements():
            table.add_row(msg[0], str(msg[1]), Markdown(msg[2]))
            live.update(table, refresh=True)

    history = debate_runner.debate.dialogue_history
    if save:
        from autodebater.persistence import DebateStore
        store = DebateStore()
        store.save(history, motion)
        typer.echo(f"Debate saved (id={debate_runner.debate.debate_id})")

    if output_file:
        fmt = "md" if output_file.endswith(".md") else "json"
        DebateExporter.export_file(history, output_file, fmt)
        typer.echo(f"Debate exported to {output_file}")


@app.command()
def simple_debate(
    motion: str,
    epochs: int = 2,
    llm: str = "openai",
    debater_prompt: Optional[str] = typer.Option(None, "--debater-prompt", help="Override debater system prompt"),
    model: Optional[str] = typer.Option(None, "--model", help="Override the model name"),
    temperature: Optional[float] = typer.Option(None, "--temperature", help="Override the model temperature"),
    save: bool = typer.Option(False, "--save/--no-save", help="Persist debate to SQLite"),
    output_file: Optional[str] = typer.Option(None, "--output-file", help="Export debate to file (json or md)"),
    use_tools: bool = typer.Option(False, "--use-tools/--no-use-tools", help="Enable LangChain tool use for debaters"),
    context_file: Optional[str] = typer.Option(None, "--context-file", help="Path to a text/markdown file injected as context"),
    no_profile: bool = typer.Option(False, "--no-profile", help="Skip auto-loading the persistent profile"),
):
    """Start a new simple debate with the given motion and epochs."""
    runner_kwargs = {"context": _load_context(context_file, no_profile)}
    if debater_prompt:
        runner_kwargs["debater_prompt"] = debater_prompt
    if model:
        runner_kwargs["model"] = model
    if temperature is not None:
        runner_kwargs["temperature"] = temperature
    if use_tools:
        runner_kwargs["use_tools"] = True

    debate_runner = BasicSimpleDebateRunner(motion=motion, epochs=epochs, llm=llm, **runner_kwargs)

    typer.echo(f"Starting debate on: {motion}")
    console = Console()

    for msg in debate_runner.run_debate():
        table = msg2table(msg)
        console.print(table)

    history = debate_runner.debate.dialogue_history
    if save:
        from autodebater.persistence import DebateStore
        store = DebateStore()
        store.save(history, motion)
        typer.echo(f"Debate saved (id={debate_runner.debate.debate_id})")

    if output_file:
        fmt = "md" if output_file.endswith(".md") else "json"
        DebateExporter.export_file(history, output_file, fmt)
        typer.echo(f"Debate exported to {output_file}")


@app.command()
def panel_debate(
    motion: str,
    epochs: int = 3,
    llm: str = "openai",
    model: Optional[str] = typer.Option(None, "--model"),
    temperature: Optional[float] = typer.Option(None, "--temperature"),
    domains: Optional[List[str]] = typer.Option(None, "--domain", help="Domain to include (repeat for multiple)"),
    save: bool = typer.Option(False, "--save/--no-save"),
    output_file: Optional[str] = typer.Option(None, "--output-file"),
    use_tools: bool = typer.Option(True, "--use-tools/--no-use-tools",
                                   help="Enable web search tools for participants (default: on)"),
    context_file: Optional[str] = typer.Option(None, "--context-file", help="Path to a text/markdown file injected as context"),
    no_profile: bool = typer.Option(False, "--no-profile", help="Skip auto-loading the persistent profile"),
):
    """Start an expert panel discussion aimed at finding a nuanced answer."""
    config = RunnerConfig(
        motion=motion, epochs=epochs, llm=llm,
        model=model, temperature=temperature,
        domains=domains or None,
        use_tools=use_tools,
        context=_load_context(context_file, no_profile),
    )
    runner = ExpertPanelRunner(config)
    typer.echo(f"Starting expert panel on: {motion}")

    table = Table("name", "domain/role", "convergence", "message", show_lines=True)
    with Live(table, auto_refresh=False, vertical_overflow="visible") as live:
        for msg in runner.run_debate():
            domain_or_role = getattr(
                next((p for p in runner.debate.debaters if p.name == msg.name), None),
                "domain", msg.role
            )
            table.add_row(
                msg.name,
                domain_or_role,
                str(msg.judgement) if msg.judgement is not None else "",
                Markdown(msg.message),
            )
            live.update(table, refresh=True)

    history = runner.debate.dialogue_history
    if save:
        from autodebater.persistence import DebateStore
        DebateStore().save(history, motion)
        typer.echo(f"Panel saved (id={runner.debate.debate_id})")
    if output_file:
        fmt = "md" if output_file.endswith(".md") else "json"
        DebateExporter.export_file(history, output_file, fmt)
        typer.echo(f"Panel exported to {output_file}")


if __name__ == "__main__":
    app()
