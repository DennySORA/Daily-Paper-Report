"""Unit tests for Gemini CodeAssist API client."""

from unittest.mock import MagicMock, patch

import pytest

from src.features.llm.client import GeminiCodeAssistClient
from src.features.llm.errors import LlmApiError


def _make_client(
    access_token: str = "ya29.test-token",  # noqa: S107
    model: str = "gemini-3-pro-preview",
) -> GeminiCodeAssistClient:
    """Create a test client with pre-set project."""
    client = GeminiCodeAssistClient(access_token=access_token, model=model)
    client._project = "test-project"  # noqa: SLF001
    return client


class TestGenerateContent:
    """Tests for GeminiCodeAssistClient.generate_content."""

    @patch("src.features.llm.client.httpx.post")
    def test_success_returns_text(self, mock_post: MagicMock) -> None:
        """Should return text from model response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Hello world"}]}}]
        }
        mock_post.return_value = mock_response

        client = _make_client()
        result = client.generate_content("Say hello")

        assert result == "Hello world"

    @patch("src.features.llm.client.httpx.post")
    def test_sends_correct_request_format(self, mock_post: MagicMock) -> None:
        """Should send request in CodeAssist API format."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "ok"}]}}]
        }
        mock_post.return_value = mock_response

        client = _make_client()
        client.generate_content("Test prompt", system_instruction="Be helpful")

        call_kwargs = mock_post.call_args
        body = call_kwargs[1]["json"]
        assert body["model"] == "gemini-3-pro-preview"
        assert body["project"] == "test-project"
        assert "user_prompt_id" in body
        assert body["request"]["contents"][0]["parts"][0]["text"] == "Test prompt"
        assert "systemInstruction" in body["request"]

    @patch("src.features.llm.client.httpx.post")
    def test_non_200_raises_api_error(self, mock_post: MagicMock) -> None:
        """Should raise LlmApiError on non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        client = _make_client()

        with pytest.raises(LlmApiError, match="429"):
            client.generate_content("Test")

    @patch("src.features.llm.client.httpx.post")
    def test_empty_candidates_raises_api_error(self, mock_post: MagicMock) -> None:
        """Should raise LlmApiError when response has no candidates."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"candidates": []}
        mock_post.return_value = mock_response

        client = _make_client()

        with pytest.raises(LlmApiError, match="No candidates"):
            client.generate_content("Test")

    @patch("src.features.llm.client.httpx.post")
    def test_network_error_raises_api_error(self, mock_post: MagicMock) -> None:
        """Should raise LlmApiError on network failure."""
        import httpx

        mock_post.side_effect = httpx.ConnectError("Connection refused")

        client = _make_client()

        with pytest.raises(LlmApiError, match="request failed"):
            client.generate_content("Test")

    @patch("src.features.llm.client.httpx.post")
    def test_no_system_instruction_omitted(self, mock_post: MagicMock) -> None:
        """Should omit systemInstruction when not provided."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "ok"}]}}]
        }
        mock_post.return_value = mock_response

        client = _make_client()
        client.generate_content("Test prompt")

        body = mock_post.call_args[1]["json"]
        assert "systemInstruction" not in body["request"]


class TestGetProject:
    """Tests for project resolution."""

    @patch("src.features.llm.client.httpx.post")
    def test_resolves_project_from_cloudai_field(self, mock_post: MagicMock) -> None:
        """Should resolve project from cloudaicompanionProject field."""
        project_response = MagicMock()
        project_response.status_code = 200
        project_response.json.return_value = {
            "cloudaicompanionProject": "rapid-elevator-abc",
            "currentTier": {"id": "standard-tier"},
        }

        generate_response = MagicMock()
        generate_response.status_code = 200
        generate_response.json.return_value = {
            "response": {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
        }

        mock_post.side_effect = [project_response, generate_response]

        client = GeminiCodeAssistClient(access_token="ya29.test")  # noqa: S106
        result = client.generate_content("Test")

        assert result == "ok"
        assert mock_post.call_count == 2

    @patch("src.features.llm.client.httpx.post")
    def test_resolves_project_from_legacy_field(self, mock_post: MagicMock) -> None:
        """Should fall back to legacy project field."""
        project_response = MagicMock()
        project_response.status_code = 200
        project_response.json.return_value = {"project": "my-project-123"}

        generate_response = MagicMock()
        generate_response.status_code = 200
        generate_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "ok"}]}}]
        }

        mock_post.side_effect = [project_response, generate_response]

        client = GeminiCodeAssistClient(access_token="ya29.test")  # noqa: S106
        result = client.generate_content("Test")

        assert result == "ok"
        assert mock_post.call_count == 2

    @patch("src.features.llm.client.httpx.post")
    def test_project_lookup_failure_raises(self, mock_post: MagicMock) -> None:
        """Should raise LlmApiError if project lookup fails."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        client = GeminiCodeAssistClient(access_token="ya29.test")  # noqa: S106

        with pytest.raises(LlmApiError, match="project lookup"):
            client.generate_content("Test")
