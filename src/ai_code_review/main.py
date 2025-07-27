"""Entry point for the AI code review application."""

import asyncio
from pathlib import Path

import click
from loguru import logger

from ai_code_review.code_explorer import CodeExplorer
from ai_code_review.ollama_provider import OllamaProvider
from ai_code_review.prompt_factory import PromptFactory


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
    default="devstral",
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
    asyncio.run(review(ollama_url, ollama_port, ollama_model, project_root))


async def review(ollama_url: str, ollama_port: int, ollama_model: str, project_root: str) -> None:
    """Orchestrates the code review process.

    Args:
        project_root (str): The code snippet to review.
        ollama_url (str): The URL of the Ollama server.
        ollama_port (int): The port of the Ollama server.
        ollama_model (str): The model to use for code review.

    Raises:
        aiohttp.ClientError: If there is an issue with the HTTP request.
        json.JSONDecodeError: If the response cannot be parsed as JSON.

    """
    explorer = CodeExplorer(
        project_root=project_root,
        extensions=["py"],
    )
    code = explorer.explore()

    llm_provider = OllamaProvider(
        url=ollama_url,
        port=ollama_port,
        model=ollama_model,
    )
    logger.info(f"Reviewing code in {project_root} using model {ollama_model} at {ollama_url}:{ollama_port}")
    async for chunk in llm_provider.stream_generate(
        prompt=code,
        system_prompt=PromptFactory.general_review_prompt(),
    ):
        print(chunk, end="", flush=True)


if __name__ == "__main__":
    main()
