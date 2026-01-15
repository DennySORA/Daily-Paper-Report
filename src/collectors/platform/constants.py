"""Constants for platform collectors."""

# GitHub API
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_API_RELEASES_PATH = "/repos/{owner}/{repo}/releases"
GITHUB_DEFAULT_MAX_QPS = 5.0  # 5 requests per second (unauthenticated: 60/hour)
GITHUB_AUTHENTICATED_MAX_QPS = 15.0  # With token: 5000/hour

# HuggingFace API
HF_API_BASE_URL = "https://huggingface.co/api"
HF_API_MODELS_PATH = "/models"
HF_DEFAULT_MAX_QPS = 10.0  # Conservative default

# OpenReview API
OPENREVIEW_API_BASE_URL = "https://api2.openreview.net"
OPENREVIEW_API_NOTES_PATH = "/notes"
OPENREVIEW_DEFAULT_MAX_QPS = 5.0  # Conservative default

# Default model card/README size cap in bytes
MODEL_CARD_MAX_SIZE = 200 * 1024  # 200 KB

# Truncation limits for raw_json fields
RELEASE_BODY_MAX_LENGTH = 1000  # Max chars for release notes body

# Platform identifiers
PLATFORM_GITHUB = "github"
PLATFORM_HUGGINGFACE = "huggingface"
PLATFORM_OPENREVIEW = "openreview"

# Field names for raw_json
FIELD_PLATFORM = "platform"
FIELD_RELEASE_ID = "release_id"
FIELD_TAG_NAME = "tag_name"
FIELD_PRERELEASE = "prerelease"
FIELD_RELEASE_NOTES_URL = "release_notes_url"
FIELD_MODEL_ID = "model_id"
FIELD_PIPELINE_TAG = "pipeline_tag"
FIELD_LICENSE = "license"
FIELD_MODEL_CARD_URL = "model_card_url"
FIELD_FORUM_ID = "forum_id"
FIELD_PDF_URL = "pdf_url"
FIELD_LAST_MODIFIED = "last_modified"

# HTTP status codes for auth errors
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403

# Environment variable names for auth tokens
AUTH_TOKEN_ENV_VARS = {
    PLATFORM_GITHUB: "GITHUB_TOKEN",
    PLATFORM_HUGGINGFACE: "HF_TOKEN",
    PLATFORM_OPENREVIEW: "OPENREVIEW_TOKEN",
}

# Auth error remediation hints
AUTH_ERROR_HINTS = {
    PLATFORM_GITHUB: (
        "Authentication failed. Check that GITHUB_TOKEN environment variable "
        "is set with a valid personal access token."
    ),
    PLATFORM_HUGGINGFACE: (
        "Authentication failed. Check that HF_TOKEN environment variable "
        "is set with a valid Hugging Face token."
    ),
    PLATFORM_OPENREVIEW: (
        "Authentication failed. Check that OPENREVIEW_TOKEN environment variable "
        "is set if required by the venue policy."
    ),
}
