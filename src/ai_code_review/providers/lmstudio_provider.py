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
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        if auth_token is not None:
            self._headers["Authorization"] = f"Bearer {auth_token}"

        # Mask sensitive header values before logging
        self._safe_headers = self._headers.copy()
        if "Authorization" in self._safe_headers:
            self._safe_headers["Authorization"] = "***"

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        show_reasoning: bool = False,
    ) -> AsyncIterator[str]:
        """Stream a response from the LMStudio model.

        Args:
            prompt (str): The prompt to send to the model.
            system_prompt (str | None): An optional system prompt for the model.
            show_reasoning (bool): Whether to show reasoning in the response. Defaults to False.

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

        logger.info(f"Sending request to {self._url} with headers {self._safe_headers}")

        async with (
            aiohttp.ClientSession() as session,
            session.post(self._url, json=payload, headers=self._headers) as response,
        ):
            if response.status != HTTP_OK_STATUS:
                response_text = await response.text()
                logger.error(f"Error: {response.status} - Response: {response_text}")
                raise RuntimeError(f"LMStudio API returned status {response.status}: {response_text}")

            is_reasoning_stage = False
            async for chunk in response.content:
                chunk_str = chunk.decode("utf-8").strip()
                if chunk_str and chunk_str.startswith("data: "):
                    data_str = chunk_str[6:]  # Remove "data: " prefix
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        continue

                    if data.get("choices", None):
                        delta = data["choices"][0].get("delta", {})
                        if show_reasoning:
                            reasoning_content = delta.get("reasoning_content", "")
                            if reasoning_content and not is_reasoning_stage:  # Start of reasoning stage
                                is_reasoning_stage = True
                                yield f"[Reasoning Start]\n{reasoning_content}"
                            elif reasoning_content and is_reasoning_stage:  # Continuation of reasoning stage
                                yield reasoning_content
                            elif not reasoning_content and is_reasoning_stage:  # End of reasoning stage
                                is_reasoning_stage = False
                                yield "\n[Reasoning End]\n\n"

                        content = delta.get("content", "")
                        if content:
                            yield content
