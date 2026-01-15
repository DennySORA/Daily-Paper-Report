"""Hugging Face org models collector.

This module provides a collector for Hugging Face organization models,
capturing model IDs, last modified timestamps, and metadata.
"""

import json
import re
import time
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

import structlog

from src.collectors.base import BaseCollector, CollectorResult
from src.collectors.errors import CollectorErrorClass, ErrorRecord
from src.collectors.platform.constants import (
    AUTH_ERROR_HINTS,
    FIELD_LAST_MODIFIED,
    FIELD_LICENSE,
    FIELD_MODEL_CARD_URL,
    FIELD_MODEL_ID,
    FIELD_PIPELINE_TAG,
    FIELD_PLATFORM,
    HF_API_BASE_URL,
    HF_API_MODELS_PATH,
    HF_DEFAULT_MAX_QPS,
    PLATFORM_HUGGINGFACE,
)
from src.collectors.platform.helpers import get_auth_token, is_auth_error
from src.collectors.platform.metrics import PlatformMetrics
from src.collectors.platform.rate_limiter import (
    TokenBucketRateLimiter,
    get_platform_rate_limiter,
)
from src.collectors.state_machine import SourceState, SourceStateMachine
from src.config.schemas.sources import SourceConfig
from src.fetch.client import HttpFetcher
from src.store.hash import compute_content_hash
from src.store.models import DateConfidence, Item


logger = structlog.get_logger()

# Regex to extract org from HuggingFace URL
HF_ORG_PATTERN = re.compile(r"huggingface\.co/(?P<org>[^/]+)/?$")


def extract_org(url: str) -> str | None:
    """Extract organization from a HuggingFace URL.

    Args:
        url: HuggingFace organization URL.

    Returns:
        Organization name or None if not a valid HuggingFace org URL.
    """
    match = HF_ORG_PATTERN.search(url)
    if match:
        return match.group("org")
    return None


class HuggingFaceOrgCollector(BaseCollector):
    """Collector for Hugging Face organization models.

    Lists models for configured orgs and ingests:
    - model_id
    - lastModified timestamp
    - pipeline_tag
    - license
    - model card URL

    Canonical URL is the model page URL.

    API documentation: https://huggingface.co/docs/hub/api
    """

    def __init__(
        self,
        strip_params: list[str] | None = None,
        run_id: str = "",
        rate_limiter: TokenBucketRateLimiter | None = None,
    ) -> None:
        """Initialize the HuggingFace org collector.

        Args:
            strip_params: URL parameters to strip (not used for HuggingFace).
            run_id: Run identifier for logging.
            rate_limiter: Optional rate limiter for dependency injection.
        """
        super().__init__(strip_params)
        self._run_id = run_id
        self._metrics = PlatformMetrics.get_instance()
        self._rate_limiter = rate_limiter or get_platform_rate_limiter(
            PLATFORM_HUGGINGFACE, HF_DEFAULT_MAX_QPS
        )

    def collect(
        self,
        source_config: SourceConfig,
        http_client: HttpFetcher,
        now: datetime,  # noqa: ARG002
    ) -> CollectorResult:
        """Collect models from a HuggingFace organization.

        Args:
            source_config: Configuration for the source.
            http_client: HTTP client for fetching.
            now: Current timestamp for consistency (unused, for interface compliance).

        Returns:
            CollectorResult with items and status.
        """
        log = logger.bind(
            component="platform",
            platform=PLATFORM_HUGGINGFACE,
            run_id=self._run_id,
            source_id=source_config.id,
        )

        state_machine = SourceStateMachine(
            source_id=source_config.id,
            run_id=self._run_id,
        )

        parse_warnings: list[str] = []

        try:
            state_machine.to_fetching()

            # Extract org from URL
            org = extract_org(source_config.url)
            if not org:
                log.warning("invalid_hf_url", url=source_config.url)
                state_machine.to_failed()
                return CollectorResult(
                    items=[],
                    error=ErrorRecord(
                        error_class=CollectorErrorClass.SCHEMA,
                        message=f"Invalid HuggingFace organization URL: {source_config.url}",
                        source_id=source_config.id,
                    ),
                    state=SourceState.SOURCE_FAILED,
                )

            api_url = self._build_api_url(org, source_config.max_items)

            log.info(
                "fetching_models",
                org=org,
            )

            # Acquire rate limit token
            self._rate_limiter.acquire()

            # Build headers with auth if available
            headers = self._build_headers()

            # Fetch models
            start_time = time.monotonic()
            result = http_client.fetch(
                source_id=source_config.id,
                url=api_url,
                extra_headers=headers,
            )
            duration_ms = (time.monotonic() - start_time) * 1000
            self._metrics.record_api_call(PLATFORM_HUGGINGFACE)

            # Check for auth errors
            if result.error:
                if is_auth_error(result):
                    remediation = AUTH_ERROR_HINTS[PLATFORM_HUGGINGFACE]
                    log.warning(
                        "auth_error",
                        status_code=result.status_code,
                        remediation=remediation,
                    )
                    self._metrics.record_error(PLATFORM_HUGGINGFACE, "auth")
                    state_machine.to_failed()
                    return CollectorResult(
                        items=[],
                        error=ErrorRecord(
                            error_class=CollectorErrorClass.FETCH,
                            message=f"Authentication failed (HTTP {result.status_code}). {remediation}",
                            source_id=source_config.id,
                        ),
                        state=SourceState.SOURCE_FAILED,
                    )

                log.warning(
                    "fetch_failed",
                    error_class=result.error.error_class.value,
                    status_code=result.status_code,
                )
                self._metrics.record_error(PLATFORM_HUGGINGFACE, "fetch")
                state_machine.to_failed()
                return CollectorResult(
                    items=[],
                    error=ErrorRecord(
                        error_class=CollectorErrorClass.FETCH,
                        message=str(result.error.message),
                        source_id=source_config.id,
                    ),
                    state=SourceState.SOURCE_FAILED,
                )

            state_machine.to_parsing()

            # Parse JSON response
            items = self._parse_models(
                body=result.body_bytes,
                source_config=source_config,
                org=org,
                parse_warnings=parse_warnings,
            )

            if not items:
                log.info("empty_response")
                state_machine.to_done()
                return CollectorResult(
                    items=[],
                    parse_warnings=parse_warnings,
                    state=SourceState.SOURCE_DONE,
                )

            items = self.sort_items_deterministically(items)
            items = self.enforce_max_items(items, source_config.max_items)

            self._metrics.record_items(PLATFORM_HUGGINGFACE, len(items))

            # Check if we were rate limited
            rate_limited = self._rate_limiter.was_rate_limited

            log.info(
                "collection_complete",
                items_emitted=len(items),
                org=org,
                request_count=1,
                rate_limited=rate_limited,
                duration_ms=round(duration_ms, 2),
            )

            state_machine.to_done()
            return CollectorResult(
                items=items,
                parse_warnings=parse_warnings,
                state=SourceState.SOURCE_DONE,
            )

        except Exception as e:  # noqa: BLE001
            log.warning("unexpected_error", error=str(e))
            self._metrics.record_error(PLATFORM_HUGGINGFACE, "parse")
            state_machine.to_failed()
            return CollectorResult(
                items=[],
                error=ErrorRecord(
                    error_class=CollectorErrorClass.PARSE,
                    message=f"Unexpected error: {e}",
                    source_id=source_config.id,
                ),
                parse_warnings=parse_warnings,
                state=SourceState.SOURCE_FAILED,
            )

    def _build_api_url(self, org: str, limit: int) -> str:
        """Build HuggingFace API URL for models.

        Args:
            org: Organization name.
            limit: Number of models to fetch.

        Returns:
            Full API URL.
        """
        params = {
            "author": org,
            "limit": min(limit, 1000),  # HF API limit
            "sort": "lastModified",
            "direction": "-1",  # Descending
        }
        return f"{HF_API_BASE_URL}{HF_API_MODELS_PATH}?{urlencode(params)}"

    def _build_headers(self) -> dict[str, str]:
        """Build request headers with optional auth.

        Returns:
            Headers dictionary.
        """
        headers: dict[str, str] = {
            "Accept": "application/json",
        }

        token = get_auth_token(PLATFORM_HUGGINGFACE)
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def _parse_models(
        self,
        body: bytes,
        source_config: SourceConfig,
        org: str,  # noqa: ARG002
        parse_warnings: list[str],
    ) -> list[Item]:
        """Parse HuggingFace models JSON response.

        Args:
            body: Response body bytes.
            source_config: Source configuration.
            org: Organization name (unused, models contain full ID).
            parse_warnings: List to append warnings to.

        Returns:
            List of parsed items.
        """
        items: list[Item] = []

        try:
            models = json.loads(body)
        except json.JSONDecodeError as e:
            parse_warnings.append(f"Failed to parse JSON response: {e}")
            return []

        if not isinstance(models, list):
            parse_warnings.append("Expected array of models")
            return []

        for model in models:
            try:
                item = self._parse_model(model, source_config)
                if item:
                    items.append(item)
            except Exception as e:  # noqa: BLE001
                parse_warnings.append(f"Failed to parse model: {e}")

        return items

    def _parse_model(
        self,
        model: dict[str, Any],
        source_config: SourceConfig,
    ) -> Item | None:
        """Parse a single model object.

        Args:
            model: Model JSON object.
            source_config: Source configuration.

        Returns:
            Item if parsing succeeded, None otherwise.
        """
        # Extract required fields
        model_id = model.get("id") or model.get("modelId")
        if not model_id:
            return None

        # Build canonical URL
        canonical_url = f"https://huggingface.co/{model_id}"

        # Use model_id as title
        title = model_id

        # Extract dates
        published_at = None
        date_confidence = DateConfidence.LOW

        last_modified = model.get("lastModified")
        if last_modified:
            try:
                published_at = datetime.fromisoformat(
                    last_modified.replace("Z", "+00:00")
                )
                date_confidence = DateConfidence.HIGH
            except ValueError:
                pass

        # Build raw_json
        raw_data = self._build_raw_data(model)
        raw_json, _ = self.truncate_raw_json(raw_data)

        # Compute content hash
        content_hash = self._compute_content_hash(model, canonical_url)

        return Item(
            url=canonical_url,
            source_id=source_config.id,
            tier=source_config.tier,
            kind=source_config.kind.value,
            title=title,
            published_at=published_at,
            date_confidence=date_confidence,
            content_hash=content_hash,
            raw_json=raw_json,
        )

    def _build_raw_data(
        self,
        model: dict[str, Any],
    ) -> dict[str, Any]:
        """Build raw_json data from model.

        Args:
            model: Model JSON object.

        Returns:
            Dictionary of raw metadata.
        """
        raw_data: dict[str, Any] = {
            FIELD_PLATFORM: PLATFORM_HUGGINGFACE,
        }

        model_id = model.get("id") or model.get("modelId")
        if model_id:
            raw_data[FIELD_MODEL_ID] = model_id

        if model.get("lastModified"):
            raw_data[FIELD_LAST_MODIFIED] = model["lastModified"]

        if model.get("pipeline_tag"):
            raw_data[FIELD_PIPELINE_TAG] = model["pipeline_tag"]

        # License can be in different places
        card_data = model.get("cardData") or {}
        license_value = model.get("license") or card_data.get("license")
        if license_value:
            raw_data[FIELD_LICENSE] = license_value

        # Model card URL
        if model_id:
            raw_data[FIELD_MODEL_CARD_URL] = f"https://huggingface.co/{model_id}"

        # Include author if present
        if model.get("author"):
            raw_data["author"] = model["author"]

        # Include downloads if present
        if model.get("downloads") is not None:
            raw_data["downloads"] = model["downloads"]

        # Include likes if present
        if model.get("likes") is not None:
            raw_data["likes"] = model["likes"]

        return raw_data

    def _compute_content_hash(
        self,
        model: dict[str, Any],
        canonical_url: str,
    ) -> str:
        """Compute content hash for model.

        Hash is computed from: model_id, lastModified, pipeline_tag.

        Args:
            model: Model JSON object.
            canonical_url: Canonical URL.

        Returns:
            Content hash string.
        """
        model_id = model.get("id") or model.get("modelId") or ""

        extra: dict[str, str] = {}

        if model.get("lastModified"):
            extra["lastModified"] = model["lastModified"]

        if model.get("pipeline_tag"):
            extra["pipeline_tag"] = model["pipeline_tag"]

        return compute_content_hash(
            title=model_id,
            url=canonical_url,
            extra=extra if extra else None,
        )
