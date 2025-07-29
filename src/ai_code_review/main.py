"""Entry point for the AI code review application."""

import asyncio
from pathlib import Path

import click

from ai_code_review.code_explorer.project_files_explorer import ProjectFileExplorer
from ai_code_review.ollama_provider import OllamaProvider
from ai_code_review.reviewer import Reviewer


@click.command()
@click.option(
    "--project-root",
    type=Path,
    help="Path to the project root directory containing code files.",
    default=Path(__file__).parent.parent.resolve(),
    show_default=True,
)
@click.option(
    "--ollama-url",
    default="127.0.0.1",
    type=str,
    help="The URL of the Ollama server (default: localhost).",
    show_default=True,
)
@click.option(
    "--ollama-port",
    default=11434,
    type=int,
    help="The port of the Ollama server (default: 11434).",
    show_default=True,
)
@click.option(
    "--ollama-model",
    default="qwen2.5-coder:7b",
    type=str,
    help="The model to use for code review (default: devstral).",
    show_default=True,
)
def main(
    project_root: str,
    ollama_url: str,
    ollama_port: int,
    ollama_model: str,
) -> None:
    """Run the AI code review application."""
    code_explorer = ProjectFileExplorer(
        project_root=project_root,
        extensions=["py"],
    )
    llm_provider = OllamaProvider(
        url=ollama_url,
        port=ollama_port,
        model=ollama_model,
    )
    reviewer = Reviewer(
        code_explorer=code_explorer,
        llm_provider=llm_provider,
    )
    asyncio.run(reviewer.review())


if __name__ == "__main__":
    main()
