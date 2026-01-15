"""Data models for the Story linker."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Annotated, NewType

from pydantic import BaseModel, ConfigDict, Field

from src.config.schemas.base import LinkType
from src.store.models import Item


if TYPE_CHECKING:
    from src.linker.entity_matcher import EntityMatch

# Type aliases for improved code clarity
StoryID = NewType("StoryID", str)
"""Unique identifier for a Story (e.g., 'arxiv:2401.12345', 'fallback:abc123')."""

EntityID = NewType("EntityID", str)
"""Identifier for an entity (e.g., 'openai', 'anthropic')."""

SourceID = NewType("SourceID", str)
"""Identifier for a data source (e.g., 'arxiv-rss', 'github-releases')."""


class StorySection(str, Enum):
    """Section where a Story should be displayed.

    - TOP5: Top 5 must-read stories
    - MODEL_RELEASES: Model/weight releases grouped by entity
    - PAPERS: Papers section
    - RADAR: Worth monitoring section
    """

    TOP5 = "top5"
    MODEL_RELEASES = "model_releases"
    PAPERS = "papers"
    RADAR = "radar"


class StoryLink(BaseModel):
    """A typed link within a Story.

    Attributes:
        url: Canonical URL of the link.
        link_type: Type of link (official, arxiv, github, etc.).
        source_id: Source that provided this link.
        tier: Tier of the source (0, 1, 2).
        title: Title from this source.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    url: Annotated[str, Field(min_length=1)]
    link_type: LinkType
    source_id: Annotated[str, Field(min_length=1)]
    tier: Annotated[int, Field(ge=0, le=2)]
    title: str = ""


class Story(BaseModel):
    """A Story aggregating related items from multiple sources.

    Attributes:
        story_id: Deterministic unique identifier.
        title: Display title (from primary link source).
        primary_link: The main link per precedence rules.
        links: All typed links for this story.
        entities: Matched entity IDs.
        section: Which section this story belongs to.
        published_at: Publication timestamp (from best source).
        arxiv_id: arXiv ID if present.
        hf_model_id: Hugging Face model ID if present.
        github_release_url: GitHub release URL if present.
        item_count: Number of items merged into this story.
        raw_items: Original items that were merged.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    story_id: Annotated[str, Field(min_length=1)]
    title: Annotated[str, Field(min_length=1)]
    primary_link: StoryLink
    links: Annotated[list[StoryLink], Field(min_length=1)]
    entities: list[str] = Field(default_factory=list)
    section: StorySection | None = None
    published_at: datetime | None = None
    arxiv_id: str | None = None
    hf_model_id: str | None = None
    github_release_url: str | None = None
    item_count: int = 1
    raw_items: list[Item] = Field(default_factory=list)

    def to_json_dict(self) -> dict[str, object]:
        """Convert to JSON-serializable dictionary (without raw_items).

        Returns:
            Dictionary suitable for JSON serialization.
        """
        return {
            "story_id": self.story_id,
            "title": self.title,
            "primary_link": {
                "url": self.primary_link.url,
                "link_type": self.primary_link.link_type.value,
                "source_id": self.primary_link.source_id,
                "tier": self.primary_link.tier,
                "title": self.primary_link.title,
            },
            "links": [
                {
                    "url": link.url,
                    "link_type": link.link_type.value,
                    "source_id": link.source_id,
                    "tier": link.tier,
                    "title": link.title,
                }
                for link in self.links
            ],
            "entities": self.entities,
            "section": self.section.value if self.section else None,
            "published_at": (
                self.published_at.isoformat() if self.published_at else None
            ),
            "arxiv_id": self.arxiv_id,
            "hf_model_id": self.hf_model_id,
            "github_release_url": self.github_release_url,
            "item_count": self.item_count,
        }


@dataclass
class TaggedItem:
    """Item with entity tags and stable ID.

    Attributes:
        item: Original item.
        entity_matches: Matched entities.
        entity_ids: List of matched entity IDs.
        stable_id: Extracted stable ID (arxiv:..., hf:..., etc.).
        stable_id_type: Type of stable ID.
    """

    item: Item
    entity_matches: list["EntityMatch"] = field(default_factory=list)
    entity_ids: list[str] = field(default_factory=list)
    stable_id: str | None = None
    stable_id_type: str = "none"


@dataclass
class CandidateGroup:
    """Group of items that should be merged into one Story.

    Attributes:
        group_key: Key used for grouping.
        items: Items in this group.
        tagged_items: Tagged items in this group.
    """

    group_key: str
    items: list[Item] = field(default_factory=list)
    tagged_items: list["TaggedItem"] = field(default_factory=list)


@dataclass
class MergeRationale:
    """Audit record for a merge decision.

    Attributes:
        story_id: ID of the resulting story.
        matched_entity_ids: Entity IDs used for matching.
        matched_stable_ids: Stable IDs (arxiv_id, hf_model_id, etc.) used.
        fallback_heuristic: Fallback method used if any.
        source_ids: All source IDs that contributed.
        items_merged: Number of items merged.
    """

    story_id: str
    matched_entity_ids: list[str] = field(default_factory=list)
    matched_stable_ids: dict[str, str] = field(default_factory=dict)
    fallback_heuristic: str | None = None
    source_ids: list[str] = field(default_factory=list)
    items_merged: int = 1


@dataclass
class LinkerResult:
    """Result of the Story linking operation.

    Attributes:
        stories: List of merged stories.
        items_in: Number of input items.
        stories_out: Number of output stories.
        merges_total: Number of merges performed.
        fallback_merges: Number of fallback (title-based) merges.
        rationales: Audit records for each story.
    """

    stories: list[Story]
    items_in: int
    stories_out: int
    merges_total: int = 0
    fallback_merges: int = 0
    rationales: list[MergeRationale] = field(default_factory=list)

    @property
    def fallback_ratio(self) -> float:
        """Calculate ratio of fallback merges.

        Returns:
            Fallback merge ratio (0.0-1.0).
        """
        if self.merges_total == 0:
            return 0.0
        return self.fallback_merges / self.merges_total
