"""Topics configuration schema."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.config.schemas.base import LinkType


class DedupeConfig(BaseModel):
    """Deduplication configuration.

    Attributes:
        canonical_url_strip_params: URL parameters to strip for canonicalization.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_url_strip_params: list[str] = Field(default_factory=list)


class ScoringConfig(BaseModel):
    """Scoring weights configuration.

    Attributes:
        tier_0_weight: Weight for Tier 0 sources.
        tier_1_weight: Weight for Tier 1 sources.
        tier_2_weight: Weight for Tier 2 sources.
        topic_match_weight: Weight for topic keyword matches.
        entity_match_weight: Weight for entity matches.
        recency_decay_factor: Decay factor for older items.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    tier_0_weight: Annotated[float, Field(ge=0.0, le=5.0)] = 3.0
    tier_1_weight: Annotated[float, Field(ge=0.0, le=5.0)] = 2.0
    tier_2_weight: Annotated[float, Field(ge=0.0, le=5.0)] = 1.0
    topic_match_weight: Annotated[float, Field(ge=0.0, le=5.0)] = 1.5
    entity_match_weight: Annotated[float, Field(ge=0.0, le=5.0)] = 2.0
    recency_decay_factor: Annotated[float, Field(ge=0.0, le=5.0)] = 0.1


class TopicConfig(BaseModel):
    """Configuration for a single topic.

    Attributes:
        name: Topic name.
        keywords: Keywords for matching (at least 1).
        boost_weight: Additional score boost for this topic.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: Annotated[str, Field(min_length=1, max_length=100)]
    keywords: Annotated[list[str], Field(min_length=1)]
    boost_weight: Annotated[float, Field(ge=0.0, le=5.0)] = 1.0

    @model_validator(mode="after")
    def validate_keywords_non_empty(self) -> "TopicConfig":
        """Ensure keywords list contains non-empty strings."""
        for keyword in self.keywords:
            if not keyword.strip():
                msg = "Keywords must be non-empty strings"
                raise ValueError(msg)
        return self


class QuotasConfig(BaseModel):
    """Output quotas configuration.

    Attributes:
        top5_max: Maximum items in Top 5.
        radar_max: Maximum items in Radar.
        per_source_max: Maximum items per source.
        arxiv_per_category_max: Maximum arXiv items per category.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    top5_max: Annotated[int, Field(ge=0)] = 5
    radar_max: Annotated[int, Field(ge=0)] = 10
    per_source_max: Annotated[int, Field(ge=0)] = 10
    arxiv_per_category_max: Annotated[int, Field(ge=0)] = 10


class TopicsConfig(BaseModel):
    """Root configuration for topics.yaml.

    Attributes:
        version: Schema version.
        dedupe: Deduplication configuration.
        scoring: Scoring weights configuration.
        quotas: Output quotas configuration.
        topics: List of topic configurations.
        prefer_primary_link_order: Preferred link types for primary link selection.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: Annotated[str, Field(pattern=r"^\d+\.\d+$")] = "1.0"
    dedupe: DedupeConfig = Field(default_factory=DedupeConfig)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    quotas: QuotasConfig = Field(default_factory=QuotasConfig)
    topics: list[TopicConfig] = Field(default_factory=list)
    prefer_primary_link_order: list[LinkType] = Field(default_factory=list)
