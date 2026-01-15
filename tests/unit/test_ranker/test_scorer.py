"""Unit tests for ranker scoring engine."""

import math
from datetime import UTC, datetime, timedelta

import pytest

from src.config.schemas.base import LinkType
from src.config.schemas.topics import ScoringConfig, TopicConfig
from src.linker.models import Story, StoryLink
from src.ranker.scorer import ScorerConfig, StoryScorer, score_stories_pure
from src.store.models import DateConfidence, Item


def _make_item(
    url: str = "https://example.com/item",
    source_id: str = "test-source",
    tier: int = 0,
    kind: str = "blog",
    title: str = "Test Item",
    published_at: datetime | None = None,
) -> Item:
    """Create a test Item."""
    return Item(
        url=url,
        source_id=source_id,
        tier=tier,
        kind=kind,
        title=title,
        published_at=published_at,
        date_confidence=DateConfidence.HIGH if published_at else DateConfidence.LOW,
        content_hash="test-hash",
        raw_json="{}",
    )


def _make_story(
    story_id: str = "test-story-1",
    title: str = "Test Story",
    tier: int = 0,
    kind: str = "blog",
    entities: list[str] | None = None,
    published_at: datetime | None = None,
    raw_items: list[Item] | None = None,
) -> Story:
    """Create a test Story."""
    link = StoryLink(
        url="https://example.com/story",
        link_type=LinkType.OFFICIAL,
        source_id="test-source",
        tier=tier,
        title=title,
    )

    if raw_items is None:
        raw_items = [
            _make_item(
                kind=kind,
                title=title,
                published_at=published_at,
            )
        ]

    return Story(
        story_id=story_id,
        title=title,
        primary_link=link,
        links=[link],
        entities=entities or [],
        published_at=published_at,
        raw_items=raw_items,
    )


def _make_scorer(
    scoring_config: ScoringConfig | None = None,
    topics: list[TopicConfig] | None = None,
    entity_ids: list[str] | None = None,
    now: datetime | None = None,
) -> StoryScorer:
    """Create a StoryScorer with defaults."""
    config = ScorerConfig(
        scoring_config=scoring_config or ScoringConfig(),
        topics=topics or [],
        entity_ids=entity_ids or [],
        now=now,
    )
    return StoryScorer(run_id="test", config=config)


class TestTierScoring:
    """Tests for tier-based scoring."""

    def test_tier_0_score(self) -> None:
        """Tier 0 gets highest weight."""
        scorer = _make_scorer(
            ScoringConfig(tier_0_weight=3.0, tier_1_weight=2.0, tier_2_weight=1.0)
        )
        story = _make_story(tier=0)
        scored = scorer.score_story(story)
        assert scored.components.tier_score == 3.0

    def test_tier_1_score(self) -> None:
        """Tier 1 gets medium weight."""
        scorer = _make_scorer(
            ScoringConfig(tier_0_weight=3.0, tier_1_weight=2.0, tier_2_weight=1.0)
        )
        story = _make_story(tier=1)
        scored = scorer.score_story(story)
        assert scored.components.tier_score == 2.0

    def test_tier_2_score(self) -> None:
        """Tier 2 gets lowest weight."""
        scorer = _make_scorer(
            ScoringConfig(tier_0_weight=3.0, tier_1_weight=2.0, tier_2_weight=1.0)
        )
        story = _make_story(tier=2)
        scored = scorer.score_story(story)
        assert scored.components.tier_score == 1.0


class TestKindScoring:
    """Tests for kind-based scoring."""

    def test_model_kind_high_score(self) -> None:
        """Model kind gets high weight."""
        scorer = _make_scorer()
        story = _make_story(kind="model")
        scored = scorer.score_story(story)
        # Model kind has 1.8 weight in constants
        assert scored.components.kind_score == 1.8

    def test_blog_kind_score(self) -> None:
        """Blog kind gets expected weight."""
        scorer = _make_scorer()
        story = _make_story(kind="blog")
        scored = scorer.score_story(story)
        assert scored.components.kind_score == 1.5

    def test_unknown_kind_default_score(self) -> None:
        """Unknown kind gets default weight of 1.0."""
        scorer = _make_scorer()
        story = _make_story(kind="unknown_kind")
        scored = scorer.score_story(story)
        assert scored.components.kind_score == 1.0


class TestTopicScoring:
    """Tests for topic keyword matching."""

    def test_topic_match_boosts_score(self) -> None:
        """Matching topic keywords boosts score."""
        topics = [
            TopicConfig(
                name="LLM",
                keywords=["GPT", "language model"],
                boost_weight=1.5,
            )
        ]
        scorer = _make_scorer(
            ScoringConfig(topic_match_weight=1.5),
            topics=topics,
        )
        story = _make_story(title="GPT-4 is released")
        scored = scorer.score_story(story)
        # Should get topic boost: 1.5 * 1.5 = 2.25
        assert scored.components.topic_score == pytest.approx(2.25)

    def test_multiple_topics_stack(self) -> None:
        """Multiple matching topics add up."""
        topics = [
            TopicConfig(name="LLM", keywords=["GPT"], boost_weight=1.0),
            TopicConfig(name="Safety", keywords=["alignment"], boost_weight=1.0),
        ]
        scorer = _make_scorer(
            ScoringConfig(topic_match_weight=1.0),
            topics=topics,
        )
        story = _make_story(title="GPT alignment research")
        scored = scorer.score_story(story)
        # Two topics matched: 1.0 * 1.0 + 1.0 * 1.0 = 2.0
        assert scored.components.topic_score == pytest.approx(2.0)

    def test_no_topic_match(self) -> None:
        """No matching topics gives zero boost."""
        topics = [
            TopicConfig(name="LLM", keywords=["GPT", "transformer"], boost_weight=1.5)
        ]
        scorer = _make_scorer(
            ScoringConfig(topic_match_weight=1.5),
            topics=topics,
        )
        story = _make_story(title="Unrelated news")
        scored = scorer.score_story(story)
        assert scored.components.topic_score == 0.0

    def test_case_insensitive_matching(self) -> None:
        """Topic matching is case insensitive."""
        topics = [TopicConfig(name="LLM", keywords=["GPT"], boost_weight=1.0)]
        scorer = _make_scorer(
            ScoringConfig(topic_match_weight=1.0),
            topics=topics,
        )
        story = _make_story(title="gpt-4 release")
        scored = scorer.score_story(story)
        assert scored.components.topic_score == 1.0


class TestRecencyScoring:
    """Tests for recency decay scoring."""

    def test_today_high_recency(self) -> None:
        """Story from today has high recency score."""
        now = datetime.now(UTC)
        scorer = _make_scorer(
            ScoringConfig(recency_decay_factor=0.1),
            now=now,
        )
        story = _make_story(published_at=now)
        scored = scorer.score_story(story)
        # e^(-0.1 * 0) = 1.0
        assert scored.components.recency_score == pytest.approx(1.0)

    def test_one_day_old_decay(self) -> None:
        """Story from 1 day ago has decayed score."""
        now = datetime.now(UTC)
        yesterday = now - timedelta(days=1)
        scorer = _make_scorer(
            ScoringConfig(recency_decay_factor=0.1),
            now=now,
        )
        story = _make_story(published_at=yesterday)
        scored = scorer.score_story(story)
        # e^(-0.1 * 1) ≈ 0.905
        expected = math.exp(-0.1 * 1)
        assert scored.components.recency_score == pytest.approx(expected)

    def test_one_week_old_decay(self) -> None:
        """Story from 1 week ago has significantly decayed score."""
        now = datetime.now(UTC)
        week_ago = now - timedelta(days=7)
        scorer = _make_scorer(
            ScoringConfig(recency_decay_factor=0.1),
            now=now,
        )
        story = _make_story(published_at=week_ago)
        scored = scorer.score_story(story)
        # e^(-0.1 * 7) ≈ 0.497
        expected = math.exp(-0.1 * 7)
        assert scored.components.recency_score == pytest.approx(expected)

    def test_no_date_penalty(self) -> None:
        """Story without date gets penalty."""
        scorer = _make_scorer(ScoringConfig(recency_decay_factor=0.1))
        story = _make_story(published_at=None)
        scored = scorer.score_story(story)
        # Penalty for no date
        assert scored.components.recency_score == pytest.approx(0.1)


class TestEntityScoring:
    """Tests for entity match scoring."""

    def test_entity_match_bonus(self) -> None:
        """Matching entity gives bonus."""
        scorer = _make_scorer(
            ScoringConfig(entity_match_weight=2.0),
            entity_ids=["openai", "anthropic"],
        )
        story = _make_story(entities=["openai"])
        scored = scorer.score_story(story)
        assert scored.components.entity_score == 2.0

    def test_multiple_entity_matches(self) -> None:
        """Multiple entity matches stack."""
        scorer = _make_scorer(
            ScoringConfig(entity_match_weight=2.0),
            entity_ids=["openai", "anthropic"],
        )
        story = _make_story(entities=["openai", "anthropic"])
        scored = scorer.score_story(story)
        # Two matches: 2.0 * 2 = 4.0
        assert scored.components.entity_score == 4.0

    def test_no_entity_match(self) -> None:
        """No matching entity gives zero bonus."""
        scorer = _make_scorer(
            ScoringConfig(entity_match_weight=2.0),
            entity_ids=["openai"],
        )
        story = _make_story(entities=["google"])
        scored = scorer.score_story(story)
        assert scored.components.entity_score == 0.0

    def test_no_entities_in_story(self) -> None:
        """Story without entities gets no bonus."""
        scorer = _make_scorer(
            ScoringConfig(entity_match_weight=2.0),
            entity_ids=["openai"],
        )
        story = _make_story(entities=[])
        scored = scorer.score_story(story)
        assert scored.components.entity_score == 0.0


class TestTotalScore:
    """Tests for total score calculation."""

    def test_total_is_sum_of_components(self) -> None:
        """Total score is sum of all components."""
        now = datetime.now(UTC)
        scorer = _make_scorer(
            ScoringConfig(
                tier_0_weight=3.0,
                topic_match_weight=1.5,
                entity_match_weight=2.0,
                recency_decay_factor=0.0,  # No decay for easy calculation
            ),
            topics=[TopicConfig(name="LLM", keywords=["GPT"], boost_weight=1.0)],
            entity_ids=["openai"],
            now=now,
        )
        story = _make_story(
            tier=0,
            kind="blog",
            title="GPT-4 release",
            entities=["openai"],
            published_at=now,
        )
        scored = scorer.score_story(story)
        expected = (
            scored.components.tier_score
            + scored.components.kind_score
            + scored.components.topic_score
            + scored.components.recency_score
            + scored.components.entity_score
        )
        assert scored.components.total_score == pytest.approx(expected)


class TestPureFunction:
    """Tests for pure function API."""

    def test_score_stories_pure(self) -> None:
        """Pure function scores multiple stories."""
        stories = [
            _make_story(story_id="1", title="First story"),
            _make_story(story_id="2", title="Second story"),
        ]
        config = ScorerConfig(scoring_config=ScoringConfig())
        scored = score_stories_pure(stories=stories, config=config)
        assert len(scored) == 2
        assert all(s.components.total_score > 0 for s in scored)
