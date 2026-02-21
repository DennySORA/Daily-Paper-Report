"""Gemini CodeAssist API client."""

import random
import time
import uuid
from http import HTTPStatus

import httpx
import structlog

from src.features.llm.errors import LlmApiError


logger = structlog.get_logger()

_GENERATE_ENDPOINT = "https://cloudcode-pa.googleapis.com/v1internal:generateContent"
_CODE_ASSIST_ENDPOINT = "https://cloudcode-pa.googleapis.com/v1internal:loadCodeAssist"

_MIN_REQUEST_INTERVAL = 2.0  # seconds between requests
_MAX_RETRIES = 5
_RETRY_BASE_DELAY = 3.0  # seconds
_RETRYABLE_STATUS_CODES = {HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.SERVICE_UNAVAILABLE}


class GeminiCodeAssistClient:
    """Client for the Gemini CodeAssist API.

    Handles request formatting, rate limiting, and response parsing
    for the CodeAssist generateContent endpoint.

    Attributes:
        model: Gemini model identifier to use.
    """

    def __init__(
        self,
        access_token: str,
        model: str = "gemini-2.5-flash",
    ) -> None:
        """Initialize the client.

        Args:
            access_token: Google OAuth access token.
            model: Gemini model identifier.
        """
        self._access_token = access_token
        self.model = model
        self._project: str | None = None
        self._last_request_time: float = 0.0
        self._log = logger.bind(component="llm", subcomponent="client")

    def _get_project(self) -> str:
        """Obtain or return cached project identifier from CodeAssist.

        Returns:
            Project string for API requests.

        Raises:
            LlmApiError: If project lookup fails.
        """
        if self._project is not None:
            return self._project

        try:
            response = httpx.post(
                _CODE_ASSIST_ENDPOINT,
                headers={"Authorization": f"Bearer {self._access_token}"},
                json={},
                timeout=15.0,
            )
        except httpx.HTTPError as exc:
            msg = f"CodeAssist project lookup failed: {exc}"
            raise LlmApiError(msg) from exc

        if response.status_code != HTTPStatus.OK:
            msg = f"CodeAssist project lookup returned {response.status_code}"
            raise LlmApiError(msg, status_code=response.status_code)

        data = response.json()
        project: str = data.get("cloudaicompanionProject", "") or data.get(
            "project", ""
        )
        if not project:
            msg = "No project in CodeAssist response"
            raise LlmApiError(msg)

        self._project = project
        self._log.info("code_assist_project_resolved", project=project)
        return project

    def _rate_limit(self) -> None:
        """Enforce minimum interval between requests."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < _MIN_REQUEST_INTERVAL:
            time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.monotonic()

    def generate_content(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        """Send a generate content request to the CodeAssist API.

        Retries with exponential backoff on 429/503 responses.

        Args:
            prompt: User prompt text.
            system_instruction: Optional system instruction.

        Returns:
            Generated text from the model response.

        Raises:
            LlmApiError: If the API call fails after all retries.
        """
        project = self._get_project()

        request_inner: dict[str, object] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        }

        if system_instruction:
            request_inner["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        request_body: dict[str, object] = {
            "model": self.model,
            "project": project,
            "user_prompt_id": str(uuid.uuid4()),
            "request": request_inner,
        }

        last_exc: LlmApiError | None = None

        for attempt in range(_MAX_RETRIES + 1):
            self._rate_limit()

            try:
                response = httpx.post(
                    _GENERATE_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {self._access_token}",
                        "Content-Type": "application/json",
                    },
                    json=request_body,
                    timeout=60.0,
                )
            except httpx.HTTPError as exc:
                msg = f"GenerateContent request failed: {exc}"
                raise LlmApiError(msg) from exc

            if response.status_code == HTTPStatus.OK:
                break

            status = HTTPStatus(response.status_code)
            if status in _RETRYABLE_STATUS_CODES and attempt < _MAX_RETRIES:
                delay = _RETRY_BASE_DELAY * (2**attempt) + random.uniform(0, 1)  # noqa: S311
                self._log.warning(
                    "llm_retryable_error",
                    status=response.status_code,
                    attempt=attempt + 1,
                    retry_delay=round(delay, 1),
                )
                time.sleep(delay)
                last_exc = LlmApiError(
                    f"GenerateContent returned {response.status_code}",
                    status_code=response.status_code,
                )
                continue

            msg = f"GenerateContent returned {response.status_code}"
            raise LlmApiError(msg, status_code=response.status_code)
        else:
            # All retries exhausted
            raise last_exc or LlmApiError("All retries exhausted")

        data = response.json()
        # Response may be nested under "response" key or flat
        inner = data.get("response", data)
        candidates = inner.get("candidates", [])
        if not candidates:
            msg = "No candidates in GenerateContent response"
            raise LlmApiError(msg)

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            msg = "No parts in first candidate"
            raise LlmApiError(msg)

        text: str = parts[0].get("text", "")
        if not text:
            msg = "Empty text in response"
            raise LlmApiError(msg)

        return text
