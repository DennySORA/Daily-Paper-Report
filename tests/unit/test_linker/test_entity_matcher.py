"""Unit tests for entity matcher."""

from src.config.schemas.base import LinkType
from src.config.schemas.entities import EntityConfig, EntityRegion
from src.linker.entity_matcher import (
    get_all_entity_ids,
    get_primary_entity,
    match_item_to_entities,
)
from src.store.models import DateConfidence, Item


def create_test_item(
    title: str = "Test Title",
    raw_json: str = "{}",
) -> Item:
    """Create a test Item."""
    return Item(
        url="https://example.com/post",
        source_id="test-source",
        tier=1,
        kind="blog",
        title=title,
        content_hash="test-hash",
        raw_json=raw_json,
        date_confidence=DateConfidence.LOW,
    )


def create_test_entity(
    entity_id: str = "test-entity",
    name: str = "Test Entity",
    keywords: list[str] | None = None,
    aliases: list[str] | None = None,
) -> EntityConfig:
    """Create a test EntityConfig."""
    return EntityConfig(
        id=entity_id,
        name=name,
        region=EntityRegion.INTL,
        keywords=keywords or ["test"],
        prefer_links=[LinkType.OFFICIAL],
        aliases=aliases or [],
    )


class TestMatchItemToEntities:
    """Tests for match_item_to_entities function."""

    def test_no_match(self) -> None:
        """Test item with no matching keywords."""
        item = create_test_item(title="Random blog post")
        entities = [create_test_entity(keywords=["OpenAI", "GPT"])]

        matches = match_item_to_entities(item, entities)
        assert len(matches) == 0

    def test_single_keyword_match(self) -> None:
        """Test matching single keyword in title."""
        item = create_test_item(title="OpenAI announces new model")
        entities = [create_test_entity(entity_id="openai", keywords=["OpenAI"])]

        matches = match_item_to_entities(item, entities)
        assert len(matches) == 1
        assert matches[0].entity_id == "openai"
        assert "OpenAI" in matches[0].matched_keywords

    def test_multiple_keyword_match(self) -> None:
        """Test matching multiple keywords."""
        item = create_test_item(title="OpenAI GPT-4 Technical Report")
        entities = [
            create_test_entity(entity_id="openai", keywords=["OpenAI", "GPT-4", "GPT"])
        ]

        matches = match_item_to_entities(item, entities)
        assert len(matches) == 1
        assert len(matches[0].matched_keywords) >= 2

    def test_multiple_entities_match(self) -> None:
        """Test matching multiple entities."""
        item = create_test_item(title="OpenAI and Anthropic release new models")
        entities = [
            create_test_entity(entity_id="openai", keywords=["OpenAI"]),
            create_test_entity(entity_id="anthropic", keywords=["Anthropic"]),
        ]

        matches = match_item_to_entities(item, entities)
        assert len(matches) == 2

    def test_alias_match(self) -> None:
        """Test matching via alias."""
        item = create_test_item(title="Google DeepMind paper")
        entities = [
            create_test_entity(
                entity_id="deepmind",
                keywords=["DeepMind"],
                aliases=["Google DeepMind"],
            )
        ]

        matches = match_item_to_entities(item, entities)
        assert len(matches) == 1
        assert "Google DeepMind" in matches[0].matched_keywords

    def test_case_insensitive_match(self) -> None:
        """Test matching is case insensitive."""
        item = create_test_item(title="OPENAI announces CLAUDE competitor")
        entities = [create_test_entity(entity_id="openai", keywords=["openai"])]

        matches = match_item_to_entities(item, entities)
        assert len(matches) == 1

    def test_raw_json_abstract_match(self) -> None:
        """Test matching in raw_json abstract."""
        import json

        raw = json.dumps({"abstract": "This paper from OpenAI discusses..."})
        item = create_test_item(title="Technical Report", raw_json=raw)
        entities = [create_test_entity(entity_id="openai", keywords=["OpenAI"])]

        matches = match_item_to_entities(item, entities)
        assert len(matches) == 1

    def test_sorted_by_score(self) -> None:
        """Test matches are sorted by score descending."""
        item = create_test_item(title="OpenAI GPT-4 paper mentions Anthropic")
        entities = [
            create_test_entity(entity_id="openai", keywords=["OpenAI", "GPT-4"]),
            create_test_entity(entity_id="anthropic", keywords=["Anthropic"]),
        ]

        matches = match_item_to_entities(item, entities)
        assert len(matches) == 2
        # OpenAI should have higher score (more matches)
        assert matches[0].entity_id == "openai"

    def test_word_boundary_matching(self) -> None:
        """Test word boundary matching prevents partial matches."""
        item = create_test_item(title="AI safety research")
        entities = [create_test_entity(entity_id="openai", keywords=["OpenAI"])]

        # "AI" should not match "OpenAI"
        matches = match_item_to_entities(item, entities)
        assert len(matches) == 0


class TestGetPrimaryEntity:
    """Tests for get_primary_entity function."""

    def test_returns_first_entity(self) -> None:
        """Test returns first entity ID."""
        item = create_test_item(title="OpenAI paper")
        entities = [create_test_entity(entity_id="openai", keywords=["OpenAI"])]
        matches = match_item_to_entities(item, entities)

        primary = get_primary_entity(matches)
        assert primary == "openai"

    def test_returns_none_for_empty(self) -> None:
        """Test returns None for empty matches."""
        primary = get_primary_entity([])
        assert primary is None


class TestGetAllEntityIds:
    """Tests for get_all_entity_ids function."""

    def test_returns_all_ids(self) -> None:
        """Test returns all entity IDs."""
        item = create_test_item(title="OpenAI and Anthropic collaboration")
        entities = [
            create_test_entity(entity_id="openai", keywords=["OpenAI"]),
            create_test_entity(entity_id="anthropic", keywords=["Anthropic"]),
        ]
        matches = match_item_to_entities(item, entities)

        ids = get_all_entity_ids(matches)
        assert "openai" in ids
        assert "anthropic" in ids

    def test_returns_empty_for_no_matches(self) -> None:
        """Test returns empty list for no matches."""
        ids = get_all_entity_ids([])
        assert ids == []
