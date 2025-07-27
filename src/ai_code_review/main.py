"""Entry point for the AI code review application."""

import asyncio
from pathlib import Path

import click
from loguru import logger

from ai_code_review.code_explorer import CodeExplorer
from ai_code_review.ollama_provider import OllamaProvider


@click.command()
@click.option(
    "--ollama-url",
    default="localhost",
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
@click.option(
    "--project-root",
    type=Path,
    help="Path to the project root directory containing code files.",
    default=Path.cwd().parent,
    show_default=True,
)
def main(
    ollama_url: str,
    ollama_port: int,
    ollama_model: str,
    project_root: str,
) -> None:
    """Run the AI code review application."""
    asyncio.run(review(ollama_url, ollama_port, ollama_model, project_root))


async def review(ollama_url: str, ollama_port: int, ollama_model: str, project_root: str) -> None:
    """Orchestrates the code review process.

    Args:
        ollama_url (str): The URL of the Ollama server.
        ollama_port (int): The port of the Ollama server.
        ollama_model (str): The model to use for code review.
        project_root (str): The code snippet to review.

    Raises:
        aiohttp.ClientError: If there is an issue with the HTTP request.
        json.JSONDecodeError: If the response cannot be parsed as JSON.

    """
    code_review_prompt = (
        "You are an AI code reviewer."
        "Your task is to review the provided code and give feedback on its quality, style, and potential improvements."
        "Please provide a detailed analysis."
    )

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
        system_prompt=code_review_prompt,
    ):
        print(chunk, end="", flush=True)


if __name__ == "__main__":
    main()
