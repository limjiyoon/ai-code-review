"""Entry point for the AI code review application."""

import asyncio

import aiohttp
import orjson as json
from loguru import logger

HTTP_OK_STATUS = 200


async def main() -> None:
    """Orchestrates the code review process."""
    code_review_prompt = (
        "You are an AI code reviewer."
        "Your task is to review the provided code and give feedback on its quality, style, and potential improvements."
        "Please provide a detailed analysis."
    )

    test_code_snippet = """def add(a, b):
    return a + b"""
    ollam_url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "devstral",
        "prompt": test_code_snippet,
        "system": code_review_prompt,
        "stream": True,
    }

    async with (
        aiohttp.ClientSession() as session,
        session.post(ollam_url, headers=headers, data=json.dumps(payload)) as response,
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
    asyncio.run(main())
