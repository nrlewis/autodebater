"""
CLI entry point for debates
"""

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.table import Table

from autodebater.debate_runners import BasicJudgedDebateRunner, BasicSimpleDebateRunner
from autodebater.dialogue import DialogueMessage

app = typer.Typer()


def msg2table(msg: DialogueMessage):
    table = Table("name", "role", "message")
    table.add_row(msg.name, msg.role, msg.message)
    return table


@app.command()
def judged_debate(motion: str, epochs: int = 2, llm: str = "openai"):
    """Start a new debate with the given motion and epochs."""
    debate_runner = BasicJudgedDebateRunner(motion=motion, epochs=epochs, llm=llm)

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


@app.command()
def simple_debate(motion: str, epochs: int = 2, llm: str = "openai"):
    """Start a new debate with the given motion and epochs."""
    debate_runner = BasicSimpleDebateRunner(motion=motion, epochs=epochs, llm=llm)

    typer.echo(f"Starting debate on: {motion}")
    console = Console()

    for msg in debate_runner.run_debate():
        table = msg2table(msg)
        console.print(table)


if __name__ == "__main__":
    app()
