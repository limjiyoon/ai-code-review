"""Base LLM Provider interface."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class BaseLLMProvider(ABC):
    """Base class for LLM providers.

    This class defines the interface for LLM providers that generate streaming responses.
    """

    @abstractmethod
    def stream_generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response from the LLM model.

        Args:
            prompt (str): The prompt to send to the model.
            system_prompt (str | None): An optional system prompt for the model.

        Returns:
            AsyncIterator[str]: The streamed response from the LLM server.

        """
        pass
