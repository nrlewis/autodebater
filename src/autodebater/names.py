"""
Utility for generating unique participant names for debates.
"""

import random

_NAMES = [
    "Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Henry",
    "Iris", "Jack", "Karen", "Leo", "Maya", "Nora", "Oscar", "Paula",
    "Quinn", "Rita", "Sam", "Tara", "Uma", "Victor", "Wendy", "Xavier",
    "Yara", "Zoe",
]


def generate_name(used: set = None) -> str:
    """Return a random name not already in *used*."""
    if used is None:
        used = set()
    available = [n for n in _NAMES if n not in used]
    if not available:
        # Fall back to a numbered name if all are exhausted
        i = 1
        while f"Participant{i}" in used:
            i += 1
        return f"Participant{i}"
    return random.choice(available)
