"""Unit tests for the persistence module."""

import json
import os
import tempfile

import pytest

from autodebater.dialogue import DialogueHistory, DialogueMessage
from autodebater.persistence import DebateExporter, DebateStore


@pytest.fixture
def sample_history():
    h = DialogueHistory()
    h.add_message(DialogueMessage(name="mod", role="moderator", message="Please begin", debate_id="test-id"))
    h.add_message(DialogueMessage(name="Alice", role="debater", message="AI will surpass humans.", debate_id="test-id", stance="for"))
    h.add_message(DialogueMessage(name="Bob", role="debater", message="AI will not surpass humans.", debate_id="test-id", stance="against"))
    h.add_message(DialogueMessage(name="Judge1", role="judge", message="60 Balanced debate.", debate_id="test-id", judgement=60.0))
    return h


@pytest.fixture
def store(tmp_path):
    db_file = str(tmp_path / "test_debates.db")
    return DebateStore(db_path=db_file)


def test_save_and_load(store, sample_history):
    store.save(sample_history, "AI will surpass human intelligence")
    loaded = store.load("test-id")
    assert len(loaded) == len(sample_history.messages)
    assert loaded[0].name == "mod"
    assert loaded[1].stance == "for"
    assert loaded[3].judgement == 60.0


def test_list_debates(store, sample_history):
    store.save(sample_history, "Test motion")
    debates = store.list_debates()
    assert len(debates) == 1
    assert debates[0]["motion"] == "Test motion"
    assert debates[0]["debate_id"] == "test-id"


def test_save_overwrites(store, sample_history):
    store.save(sample_history, "Test motion")
    store.save(sample_history, "Test motion updated")
    debates = store.list_debates()
    assert len(debates) == 1
    loaded = store.load("test-id")
    assert len(loaded) == len(sample_history.messages)


def test_to_json(sample_history):
    result = DebateExporter.to_json(sample_history)
    data = json.loads(result)
    assert len(data) == len(sample_history.messages)
    assert data[0]["name"] == "mod"


def test_to_markdown(sample_history):
    result = DebateExporter.to_markdown(sample_history)
    assert "# Debate Transcript" in result
    assert "Alice" in result
    assert "for" in result


def test_export_file_json(tmp_path, sample_history):
    path = str(tmp_path / "debate.json")
    DebateExporter.export_file(sample_history, path, fmt="json")
    assert os.path.exists(path)
    with open(path) as f:
        data = json.load(f)
    assert len(data) == len(sample_history.messages)


def test_export_file_md(tmp_path, sample_history):
    path = str(tmp_path / "debate.md")
    DebateExporter.export_file(sample_history, path, fmt="md")
    assert os.path.exists(path)
    content = open(path).read()
    assert "# Debate Transcript" in content
