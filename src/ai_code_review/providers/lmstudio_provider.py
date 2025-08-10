"""LMStudioProvider class for interacting with the LMStudio API."""

from collections.abc import AsyncIterator

import aiohttp
import orjson as json
from loguru import logger

from ai_code_review.providers.base_llm_provider import BaseLLMProvider

HTTP_OK_STATUS = 200


class LMStudioProvider(BaseLLMProvider):
    """Provider class for interacting with the LMStudio API.

    This class handles the connection to the LMStudio server and provides methods
    to stream responses from the LMStudio model.
    """

    def __init__(
        self,
        url: str,
        port: int,
        model: str,
        auth_token: str | None = None,
    ):
        """Initialize the LMStudioProvider with the server URL, port, model, and optional auth token."""
        self._url = f"http://{url}:{port}/v1/chat/completions"
        self._model = model
        self._headers = {"Content-Type": "application/json"}
        if auth_token is not None:
            self._headers["Authorization"] = f"Bearer {auth_token}"

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response from the LMStudio model.

        Args:
            prompt (str): The prompt to send to the model.
            system_prompt (str | None): An optional system prompt for the model.

        Returns:
            AsyncIterator[str]: The streamed response from the LMStudio server.

        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self._model,
            "messages": messages,
            "stream": True,
        }

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
                raise RuntimeError(f"LMStudio API returned status {response.status}: {response_text}")

            async for line in response.content:
                line_str = line.decode("utf-8").strip()
                if line_str and line_str.startswith("data: "):
                    data_str = line_str[6:]  # Remove "data: " prefix
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and data["choices"]:
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        continue
