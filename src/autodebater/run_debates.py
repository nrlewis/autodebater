"""
CLI entry point for debates
"""

import typer

from autodebater.debate import JudgedDebate, SimpleDebate
from autodebater.participants import BullshitDetector, Debater, Judge

app = typer.Typer()


@app.command()
def judged_debate(motion: str, epochs: int = 2):
    """Start a new debate with the given motion and epochs."""
    debate = JudgedDebate(motion=motion, epochs=epochs)

    debater1 = Debater(name="Debater1", motion=motion, stance="for")
    debater2 = Debater(name="Debater2", motion=motion, stance="against")
    judge = Judge(name="Judge", motion=motion)
    bullshit_detector = BullshitDetector(name="BullshitDetector", motion=motion)
    # Add debaters to the debate
    debate.add_debaters(debater1)
    debate.add_debaters(debater2)
    debate.add_judge(judge)
    debate.add_judge(bullshit_detector)

    typer.echo(f"Starting debate on: {motion}")
    for msg in debate.debate():
        typer.echo(f"{msg.timestamp} - {msg.name} ({msg.role}): {msg.message}")


@app.command()
def simple_debate(motion: str, epochs: int = 2):
    """Start a new debate with the given motion and epochs."""
    debate = SimpleDebate(motion=motion, epochs=epochs)

    debater1 = Debater(name="Debater1", motion=motion, stance="for")
    debater2 = Debater(name="Debater2", motion=motion, stance="against")

    # Add debaters to the debate
    debate.add_debaters(debater1)
    debate.add_debaters(debater2)

    typer.echo(f"Starting debate on: {motion}")
    for msg in debate.debate():
        typer.echo(f"{msg.timestamp} - {msg.name} ({msg.role}): {msg.message}")


if __name__ == "__main__":
    app()
