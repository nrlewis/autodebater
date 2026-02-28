"""Unit tests for the names module."""

from autodebater.names import generate_name


def test_generate_name_returns_string():
    name = generate_name()
    assert isinstance(name, str)
    assert len(name) > 0


def test_generate_name_avoids_used():
    used = {"Alice", "Bob"}
    for _ in range(50):
        name = generate_name(used)
        assert name not in used


def test_generate_name_no_collision_two_calls():
    used: set = set()
    name1 = generate_name(used)
    used.add(name1)
    name2 = generate_name(used)
    assert name1 != name2


def test_generate_name_fallback_when_exhausted():
    from autodebater.names import _NAMES
    used = set(_NAMES)
    name = generate_name(used)
    assert name.startswith("Participant")
