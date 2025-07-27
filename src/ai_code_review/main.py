"""Entry point for the AI code review application."""

import asyncio
from pathlib import Path

import aiohttp
import click
import orjson as json
from loguru import logger

from ai_code_review.code_explorer import CodeExplorer

HTTP_OK_STATUS = 200


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

    ollama_url = f"http://{ollama_url}:{ollama_port}/api/generate"
    explorer = CodeExplorer(
        project_root=project_root,
        extensions=["py"],
    )
    code = explorer.explore()

    headers = {"Content-Type": "application/json"}
    payload = {
        "model": ollama_model,
        "prompt": code,
        "system": code_review_prompt,
        "stream": True,
    }

    async with (
        aiohttp.ClientSession() as session,
        session.post(ollama_url, headers=headers, data=json.dumps(payload)) as response,
    ):
        if response.status != HTTP_OK_STATUS:
            logger.error(f"Error: {response.status}")
            return

        async for line in response.content:
            if line.strip():
                try:
                    data = json.loads(line)
                    print(data.get("response", ""), end="")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")


if __name__ == "__main__":
    main()
