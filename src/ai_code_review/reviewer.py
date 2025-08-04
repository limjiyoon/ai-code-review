"""Orchestrate the code review process."""

from ai_code_review.code_explorer.base_explorer import BaseExplorer
from ai_code_review.ollama_provider import OllamaProvider
from ai_code_review.prompt_factory import PromptFactory


class Reviewer:
    """Orchestrate the code review process."""

    def __init__(
        self,
        code_explorer: BaseExplorer,
        llm_provider: OllamaProvider,
    ):
        self._code_explorer = code_explorer
        self._llm_provider = llm_provider

    async def review(self) -> str:
        """Review the code."""
        target_codes = self._code_explorer.explore()
        if not target_codes:
            return "No code to review."

        result = []
        async for chunk in self._llm_provider.stream_generate(
            prompt=target_codes,
            system_prompt=PromptFactory.general_review_prompt(),
        ):
            result.append(chunk)
            print(chunk, end="", flush=True)
        return "".join(result)
