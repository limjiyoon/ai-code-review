"""Base Explorer Class.

This module defines the interface for code explorers that retrieve code snippets using various methods.
"""

from abc import ABC, abstractmethod


class BaseExplorer(ABC):
    """Base class for code explorers.

    This class defines the interface for code explorers which retrieve code file/snippets from various sources.
    """

    @abstractmethod
    def explore(self) -> str:
        """Explore the code source and return the code snippets."""
        pass
