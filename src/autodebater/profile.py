"""
Persistent user profile / context store.

The profile is a plain markdown file at ~/.autodebater/profile.md (or the path
set by the AUTODEBATER_PROFILE env var).  Its contents are injected into every
participant's system prompt so the LLMs can give context-aware responses to
personal or domain-specific questions.
"""

import os
from pathlib import Path

DEFAULT_PROFILE_PATH = Path.home() / ".autodebater" / "profile.md"


class ProfileStore:
    def __init__(self, path: str | None = None):
        self.path = Path(
            path or os.environ.get("AUTODEBATER_PROFILE", str(DEFAULT_PROFILE_PATH))
        )

    def load(self) -> str | None:
        """Return profile text, or None if the file is absent or empty."""
        if self.path.exists():
            content = self.path.read_text(encoding="utf-8").strip()
            return content if content else None
        return None

    def save(self, content: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(content, encoding="utf-8")

    def exists(self) -> bool:
        return self.path.exists() and self.path.stat().st_size > 0
