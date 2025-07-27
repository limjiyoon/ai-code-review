"""OllamaProvider class for interacting with the Ollama API."""

from collections.abc import AsyncIterator

import aiohttp
import orjson as json
from loguru import logger

HTTP_OK_STATUS = 200


class OllamaProvider:
    """Provider class for interacting with the Ollama API.

    This class handles the connection to the Ollama server and provides methods
    to stream responses from the Ollama model.
    """

    def __init__(
        self,
        url: str,
        port: int,
        model: str,
    ):
        """Initialize the OllamaProvider with the server URL, port, and model."""
        self._url = url
        self._port = port
        self._model = model
        self._generate_url = f"http://{self._url}:{self._port}/api/generate"
        self._headers = {"Content-Type": "application/json"}

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response from the Ollama model.

        Args:
            prompt (str): The prompt to send to the model.
            system_prompt (str | None): An optional system prompt for the model.

        Returns:
            AsyncIterator[str]: The streamed response from the Ollama server.

        """
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with (
            aiohttp.ClientSession() as session,
            session.post(self._generate_url, json=payload, headers=self._headers) as response,
        ):
            if response.status != HTTP_OK_STATUS:
                logger.error(f"Error: {response.status}")

            async for line in response.content:
                if line.strip():
                    try:
                        data = json.loads(line)
                        yield data.get("response", "")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        break
