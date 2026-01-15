"""Scoring engine for Story ranking."""

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog

from src.config.schemas.topics import ScoringConfig, TopicConfig
from src.linker.models import Story
from src.ranker.constants import DEFAULT_KIND_WEIGHTS, MAX_RECENCY_DAYS
from src.ranker.models import ScoreComponents, ScoredStory
from src.ranker.topic_matcher import TopicMatcher


logger = structlog.get_logger()


@dataclass
class ScorerConfig:
    """Configuration bundle for StoryScorer.

    Attributes:
        scoring_config: Scoring weights configuration.
        topics: Topic configurations for keyword matching.
        entity_ids: List of configured entity IDs for bonus.
        now: Current time for recency calculation.
    """

    scoring_config: ScoringConfig
    topics: list[TopicConfig] = field(default_factory=list)
    entity_ids: list[str] = field(default_factory=list)
    now: datetime | None = None


class StoryScorer:
    """Computes numeric scores for Stories based on configurable weights.

    Scoring formula:
        score = tier_score + kind_score + topic_score + recency_score + entity_score

    Where:
        - tier_score: Based on primary link tier (0/1/2) and tier weights
        - kind_score: Based on source kind (blog/paper/model/etc)
        - topic_score: Sum of matched topic boosts
        - recency_score: Exponential decay based on age
        - entity_score: Bonus for matching configured entities
    """

    def __init__(self, run_id: str, config: ScorerConfig) -> None:
        """Initialize the scorer.

        Args:
            run_id: Run identifier for logging.
            config: Scorer configuration bundle.
        """
        self._run_id = run_id
        self._scoring = config.scoring_config
        self._topics = config.topics
        self._entity_ids = set(config.entity_ids)
        self._now = config.now or datetime.now(UTC)
        self._log = logger.bind(
            component="ranker",
            subcomponent="scorer",
            run_id=run_id,
        )

        # Use TopicMatcher for pre-compiled patterns
        self._topic_matcher = TopicMatcher(self._topics)

    def score_story(self, story: Story) -> ScoredStory:
        """Compute score for a single story.

        Args:
            story: Story to score.

        Returns:
            ScoredStory with computed components.
        """
        tier_score = self._compute_tier_score(story)
        kind_score = self._compute_kind_score(story)
        topic_score = self._compute_topic_score(story)
        recency_score = self._compute_recency_score(story)
        entity_score = self._compute_entity_score(story)

        total_score = (
            tier_score + kind_score + topic_score + recency_score + entity_score
        )

        components = ScoreComponents(
            tier_score=tier_score,
            kind_score=kind_score,
            topic_score=topic_score,
            recency_score=recency_score,
            entity_score=entity_score,
            total_score=total_score,
        )

        return ScoredStory(story=story, components=components)

    def score_stories(self, stories: list[Story]) -> list[ScoredStory]:
        """Score multiple stories.

        Args:
            stories: Stories to score.

        Returns:
            List of ScoredStory objects.
        """
        scored = [self.score_story(story) for story in stories]

        self._log.info(
            "scoring_complete",
            stories_scored=len(scored),
            min_score=min((s.components.total_score for s in scored), default=0.0),
            max_score=max((s.components.total_score for s in scored), default=0.0),
        )

        return scored

    def _compute_tier_score(self, story: Story) -> float:
        """Compute tier-based score.

        Args:
            story: Story to score.

        Returns:
            Tier score component.
        """
        tier = story.primary_link.tier
        if tier == 0:
            return self._scoring.tier_0_weight
        if tier == 1:
            return self._scoring.tier_1_weight
        return self._scoring.tier_2_weight

    def _compute_kind_score(self, story: Story) -> float:
        """Compute kind-based score.

        Args:
            story: Story to score.

        Returns:
            Kind score component.
        """
        # Get kind from the first raw item if available
        if story.raw_items:
            kind = story.raw_items[0].kind.lower()
        else:
            # Fallback: infer from link type
            kind = story.primary_link.link_type.value.lower()

        return DEFAULT_KIND_WEIGHTS.get(kind, 1.0)

    def _compute_topic_score(self, story: Story) -> float:
        """Compute topic keyword match score.

        Args:
            story: Story to score.

        Returns:
            Topic score component (sum of matched topic boosts).
        """
        text_to_match = story.title.lower()

        # Also include raw item titles for more matches
        for item in story.raw_items:
            text_to_match += " " + item.title.lower()

        return self._topic_matcher.compute_boost_score(
            text_to_match, self._scoring.topic_match_weight
        )

    def _compute_recency_score(self, story: Story) -> float:
        """Compute recency decay score.

        Uses exponential decay: e^(-decay_factor * days_old)

        Args:
            story: Story to score.

        Returns:
            Recency score component (0.0 to 1.0).
        """
        if story.published_at is None:
            # Penalize stories without dates
            return 0.1

        age = self._now - story.published_at
        days_old = age.total_seconds() / (24 * 60 * 60)

        # Cap age to prevent extreme penalties
        days_old = min(days_old, MAX_RECENCY_DAYS)

        # Exponential decay
        return math.exp(-self._scoring.recency_decay_factor * days_old)

    def _compute_entity_score(self, story: Story) -> float:
        """Compute entity match bonus.

        Args:
            story: Story to score.

        Returns:
            Entity score component.
        """
        if not story.entities:
            return 0.0

        # Count how many configured entities match
        matched = sum(1 for eid in story.entities if eid in self._entity_ids)

        if matched > 0:
            return self._scoring.entity_match_weight * matched

        return 0.0


def score_stories_pure(
    stories: list[Story],
    config: ScorerConfig,
    run_id: str = "pure",
) -> list[ScoredStory]:
    """Pure function API for scoring stories.

    Args:
        stories: Stories to score.
        config: Scorer configuration bundle.
        run_id: Run identifier.

    Returns:
        List of ScoredStory objects.
    """
    scorer = StoryScorer(run_id=run_id, config=config)
    return scorer.score_stories(stories)
