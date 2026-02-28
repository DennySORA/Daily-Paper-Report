"""Factory for creating LLM clients with appropriate authentication."""

import structlog

from src.features.llm.errors import LlmAuthError
from src.features.llm.protocols import LlmClient


logger = structlog.get_logger()


def create_llm_client(
    *,
    api_key: str | None = None,
    refresh_token: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
    model: str = "gemini-2.5-flash",
) -> LlmClient:
    """Create an LLM client using the best available credentials.

    Priority: API key (never expires) > OAuth (requires refresh).

    Args:
        api_key: Gemini API key. Preferred when available.
        refresh_token: Google OAuth refresh token for CodeAssist.
        client_id: OAuth client ID (required with refresh_token).
        client_secret: OAuth client secret (required with refresh_token).
        model: Gemini model identifier.

    Returns:
        An LlmClient implementation ready for use.

    Raises:
        LlmAuthError: If no valid credentials are provided.
    """
    log = logger.bind(component="llm", subcomponent="factory")

    if api_key:
        from src.features.llm.gemini_client import GeminiApiKeyClient

        log.info("llm_client_created", auth_method="api_key")
        return GeminiApiKeyClient(api_key=api_key, model=model)

    if refresh_token:
        from src.features.llm.auth import refresh_access_token
        from src.features.llm.client import GeminiCodeAssistClient

        access_token = refresh_access_token(
            refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )

        def _token_refresher() -> str:
            return refresh_access_token(
                refresh_token,
                client_id=client_id,
                client_secret=client_secret,
            )

        log.info("llm_client_created", auth_method="oauth")
        return GeminiCodeAssistClient(
            access_token=access_token,
            model=model,
            token_refresher=_token_refresher,
        )

    msg = (
        "No Gemini credentials configured (need GEMINI_API_KEY or GEMINI_REFRESH_TOKEN)"
    )
    raise LlmAuthError(msg)
