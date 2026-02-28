"""Unit tests for LLM client factory."""

from unittest.mock import MagicMock, patch

import pytest

from src.features.llm.errors import LlmAuthError
from src.features.llm.factory import create_llm_client
from src.features.llm.gemini_client import GeminiApiKeyClient
from src.features.llm.protocols import LlmClient


# Test credentials used throughout — not real secrets.
_REFRESH = "test-refresh-tok"  # noqa: S105
_SECRET = "test-client-secret"  # noqa: S105


class TestCreateLlmClient:
    """Tests for the create_llm_client factory."""

    def test_api_key_creates_api_key_client(self) -> None:
        """Should create GeminiApiKeyClient when API key is provided."""
        client = create_llm_client(api_key="test-key")

        assert isinstance(client, GeminiApiKeyClient)
        assert isinstance(client, LlmClient)

    def test_api_key_preferred_over_oauth(self) -> None:
        """Should prefer API key over OAuth when both are provided."""
        client = create_llm_client(
            api_key="test-key",
            refresh_token=_REFRESH,
            client_id="cid",
            client_secret=_SECRET,
        )

        assert isinstance(client, GeminiApiKeyClient)

    @patch("src.features.llm.auth.refresh_access_token")
    def test_oauth_creates_code_assist_client(self, mock_refresh: MagicMock) -> None:
        """Should create GeminiCodeAssistClient with OAuth credentials."""
        mock_refresh.return_value = "ya29.fresh-token"

        client = create_llm_client(
            refresh_token=_REFRESH,
            client_id="cid",
            client_secret=_SECRET,
        )

        from src.features.llm.client import GeminiCodeAssistClient

        assert isinstance(client, GeminiCodeAssistClient)
        assert isinstance(client, LlmClient)

    @patch("src.features.llm.auth.refresh_access_token")
    def test_oauth_client_has_token_refresher(self, mock_refresh: MagicMock) -> None:
        """Should attach a token_refresher to the OAuth client."""
        mock_refresh.return_value = "ya29.fresh-token"

        client = create_llm_client(
            refresh_token=_REFRESH,
            client_id="cid",
            client_secret=_SECRET,
        )

        from src.features.llm.client import GeminiCodeAssistClient

        assert isinstance(client, GeminiCodeAssistClient)
        assert client._token_refresher is not None  # noqa: SLF001

    def test_no_credentials_raises_auth_error(self) -> None:
        """Should raise LlmAuthError when no credentials are provided."""
        with pytest.raises(LlmAuthError, match="No Gemini credentials"):
            create_llm_client()

    def test_empty_strings_treated_as_missing(self) -> None:
        """Should treat empty strings as missing credentials."""
        with pytest.raises(LlmAuthError):
            create_llm_client(api_key="", refresh_token="")
