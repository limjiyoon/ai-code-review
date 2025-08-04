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
        auth_token: str | None = None,
    ):
        """Initialize the OllamaProvider with the server URL, port, model, and optional auth token."""
        self._url = f"http://{url}:{port}/api/generate"
        self._model = model
        self._headers = {"Content-Type": "application/json"}
        if auth_token is not None:
            self._headers["Authorization"] = f"Bearer {auth_token}"

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

        # Mask sensitive header values before logging
        safe_headers = self._headers.copy()
        if "Authorization" in safe_headers:
            safe_headers["Authorization"] = "***"
        logger.info(f"Sending request to {self._url} with headers {safe_headers}")

        async with (
            aiohttp.ClientSession() as session,
            session.post(self._url, json=payload, headers=self._headers) as response,
        ):
            if response.status != HTTP_OK_STATUS:
                response_text = await response.text()
                logger.error(f"Error: {response.status} - Response: {response_text}")
                raise RuntimeError(f"Ollama API returned status {response.status}: {response_text}")

            async for line in response.content:
                line_str = line.decode("utf-8")
                if line_str.strip():
                    try:
                        data = json.loads(line_str)
                        yield data.get("response", "")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        break
