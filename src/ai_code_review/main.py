"""Entry point for the AI code review application."""

import asyncio
from pathlib import Path

import click

from ai_code_review.code_explorer.git_diff_explorer import GitExplorer
from ai_code_review.lmstudio_provider import LMStudioProvider
from ai_code_review.ollama_provider import OllamaProvider
from ai_code_review.reviewer import Reviewer


@click.command()
@click.option(
    "--project-root",
    type=Path,
    help="Path to the project root directory containing code files.",
    default=Path(__file__).parent.parent.parent.resolve(),
    show_default=True,
)
@click.option(
    "--target-branch",
    default="main",
    type=str,
    help="The target branch to compare against (default: main).",
    show_default=True,
)
@click.option(
    "--llm-url",
    default="127.0.0.1",
    type=str,
    help="The URL of the LLM server (default: localhost).",
    show_default=True,
)
@click.option(
    "--llm-port",
    default=11434,
    type=int,
    help="The port of the LLM server (default: 11434 for Ollama, 1234 for LMStudio).",
    show_default=True,
)
@click.option(
    "--llm-model",
    default="gpt-oss:20b",
    type=str,
    help="The model to use for code review.",
    show_default=True,
)
@click.option(
    "--provider",
    default="ollama",
    type=click.Choice(["ollama", "lmstudio"]),
    help="The LLM provider to use (default: ollama).",
    show_default=True,
)
def main(
    project_root: Path,
    target_branch: str,
    llm_url: str,
    llm_port: int,
    llm_model: str,
    provider: str,
) -> None:
    """Run the AI code review application."""
    # Provider registry mapping
    providers = {
        "ollama": OllamaProvider,
        "lmstudio": LMStudioProvider,
    }

    git_explorer = GitExplorer(
        repo=project_root,
        base=target_branch,
    )

    provider_class = providers.get(provider)
    if not provider_class:
        raise ValueError(f"Unsupported provider: {provider}. Available providers: {list(providers.keys())}")

    llm_provider = provider_class(
        url=llm_url,
        port=llm_port,
        model=llm_model,
    )

    reviewer = Reviewer(
        code_explorer=git_explorer,
        llm_provider=llm_provider,
    )
    asyncio.run(reviewer.review())


if __name__ == "__main__":
    main()
