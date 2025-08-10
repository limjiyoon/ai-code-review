"""OllamaProvider class for interacting with the Ollama API."""

from collections.abc import AsyncIterator

import aiohttp
import orjson as json
from loguru import logger

from ai_code_review.providers.base_llm_provider import BaseLLMProvider

HTTP_OK_STATUS = 200


class OllamaProvider(BaseLLMProvider):
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

        self._safe_headers = self._headers.copy()
        if "Authorization" in self._safe_headers:
            self._safe_headers["Authorization"] = "***"

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        show_reasoning: bool = False,
    ) -> AsyncIterator[str]:
        """Stream a response from the Ollama model.

        Args:
            prompt (str): The prompt to send to the model.
            system_prompt (str | None): An optional system prompt for the model.
            show_reasoning (bool): Whether to show reasoning in the response. Defaults to False.

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
        logger.info(f"Sending request to {self._url} with headers {self._safe_headers}")

        async with (
            aiohttp.ClientSession() as session,
            session.post(self._url, json=payload, headers=self._headers) as response,
        ):
            if response.status != HTTP_OK_STATUS:
                response_text = await response.text()
                logger.error(f"Error: {response.status} - Response: {response_text}")
                raise RuntimeError(f"Ollama API returned status {response.status}: {response_text}")

            is_reasoning_stage = False
            async for chunk in response.content:
                chunk_str = chunk.decode("utf-8")
                if chunk_str.strip():
                    try:
                        data = json.loads(chunk_str)
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        break

                    if show_reasoning:
                        reasoning_content = data.get("reasoning_content", "")
                        if reasoning_content and not is_reasoning_stage:  # Start of reasoning stage
                            is_reasoning_stage = True
                            yield f"[Reasoning Start]\n{reasoning_content}"
                        elif reasoning_content and is_reasoning_stage:  # Continuation of reasoning stage
                            yield reasoning_content
                        elif not reasoning_content and is_reasoning_stage:  # End of reasoning stage
                            is_reasoning_stage = False
                            yield "\n[Reasoning End]\n\n"
                    yield data.get("response", "")
