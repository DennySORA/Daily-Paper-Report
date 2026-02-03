"""Application settings powered by Pydantic BaseSettings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Centralized environment configuration."""

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    github_token: str | None = Field(default=None, validation_alias="GITHUB_TOKEN")
    hf_token: str | None = Field(default=None, validation_alias="HF_TOKEN")
    openreview_token: str | None = Field(
        default=None, validation_alias="OPENREVIEW_TOKEN"
    )
    semantic_scholar_api_key: str | None = Field(
        default=None, validation_alias="SEMANTIC_SCHOLAR_API_KEY"
    )

    def auth_token_for_platform(self, platform: str) -> str | None:
        """Return auth token for a platform identifier."""
        tokens = {
            "github": self.github_token,
            "huggingface": self.hf_token,
            "openreview": self.openreview_token,
            "semantic_scholar": self.semantic_scholar_api_key,
        }
        return tokens.get(platform)


def get_settings() -> AppSettings:
    """Get a settings instance."""
    return AppSettings()
