"""
CLI entry point for debates
"""

import typer
from rich.console import Console
from rich.live import Live
from rich.table import Table

from autodebater.debate_runners import (BasicJudgedDebateRunner,
                                        BasicSimpleDebateRunner)
from autodebater.dialogue import DialogueMessage

app = typer.Typer()


def msg2table(msg: DialogueMessage):
    table = Table("name", "role", "message")
    table.add_row(msg.name, msg.role, msg.message)
    return table


@app.command()
def judged_debate(motion: str, epochs: int = 2):
    """Start a new debate with the given motion and epochs."""
    debate_runner = BasicJudgedDebateRunner(motion=motion, epochs=epochs)

    typer.echo(f"Starting debate on: {motion}")
    console = Console()

    table = Table("name", "role", "message")
    with Live(table, refresh_per_second=4):
        for msg in debate_runner.run_debate():
            table.add_row(msg.name, msg.role, msg.message)
        # console.print(table)

        # typer.echo(f"{msg.timestamp} - {msg.name} ({msg.role}): {msg.message}")


@app.command()
def simple_debate(motion: str, epochs: int = 2):
    """Start a new debate with the given motion and epochs."""
    debate_runner = BasicSimpleDebateRunner(motion=motion, epochs=epochs)

    typer.echo(f"Starting debate on: {motion}")
    console = Console()

    for msg in debate_runner.run_debate():
        table = msg2table(msg)
        console.print(table)


if __name__ == "__main__":
    app()
