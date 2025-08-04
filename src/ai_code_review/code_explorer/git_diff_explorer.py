"""Git Explorer class to explore git differences and retrieve code files."""

from pathlib import Path

from ai_code_review.code_explorer.base_explorer import BaseExplorer
from ai_code_review.git_cli import (
    diff_patch,
)


class GitExplorer(BaseExplorer):
    """Explores git differences and retrieves code files."""

    def __init__(
        self,
        repo: str | Path,
        base: str = "main",
    ):
        self._repo = Path(repo)
        self._base = base

    def explore(self) -> str:
        """Explores the git repository and returns the diff patch."""
        return diff_patch(str(self._repo), self._base)
