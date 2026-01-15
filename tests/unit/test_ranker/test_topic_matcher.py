"""Unit tests for TopicMatcher utility."""


from src.config.schemas.topics import TopicConfig
from src.ranker.topic_matcher import TopicMatcher


class TestTopicMatcherInit:
    """Tests for TopicMatcher initialization."""

    def test_empty_topics(self) -> None:
        """TopicMatcher with no topics should have zero topic count."""
        matcher = TopicMatcher([])
        assert matcher.topic_count == 0

    def test_single_topic(self) -> None:
        """TopicMatcher with single topic should work."""
        topic = TopicConfig(name="AI", keywords=["ai", "artificial"], boost_weight=1.5)
        matcher = TopicMatcher([topic])
        assert matcher.topic_count == 1

    def test_multiple_topics(self) -> None:
        """TopicMatcher with multiple topics should track all."""
        topics = [
            TopicConfig(name="AI", keywords=["ai"], boost_weight=1.0),
            TopicConfig(name="ML", keywords=["machine learning"], boost_weight=1.5),
            TopicConfig(name="LLM", keywords=["llm", "gpt"], boost_weight=2.0),
        ]
        matcher = TopicMatcher(topics)
        assert matcher.topic_count == 3


class TestMatchText:
    """Tests for match_text method."""

    def test_no_match(self) -> None:
        """No matches when text contains no keywords."""
        topic = TopicConfig(name="AI", keywords=["ai", "artificial"], boost_weight=1.5)
        matcher = TopicMatcher([topic])
        matches = matcher.match_text("Hello world")
        assert matches == []

    def test_single_match(self) -> None:
        """Single match returns correct TopicMatch."""
        topic = TopicConfig(name="AI", keywords=["ai"], boost_weight=1.5)
        matcher = TopicMatcher([topic])
        matches = matcher.match_text("The AI revolution")
        assert len(matches) == 1
        assert matches[0].topic_name == "AI"
        assert matches[0].boost_weight == 1.5

    def test_case_insensitive(self) -> None:
        """Matching is case insensitive."""
        topic = TopicConfig(name="AI", keywords=["AI"], boost_weight=1.0)
        matcher = TopicMatcher([topic])

        assert len(matcher.match_text("ai is here")) == 1
        assert len(matcher.match_text("AI is here")) == 1
        assert len(matcher.match_text("Ai is here")) == 1

    def test_multiple_keywords_same_topic(self) -> None:
        """Only one match per topic even with multiple keywords."""
        topic = TopicConfig(
            name="AI", keywords=["ai", "artificial intelligence"], boost_weight=1.5
        )
        matcher = TopicMatcher([topic])

        # Text has both keywords
        matches = matcher.match_text("AI and artificial intelligence are related")
        assert len(matches) == 1  # Only one match for the topic

    def test_multiple_topics_matched(self) -> None:
        """Multiple topics can be matched in same text."""
        topics = [
            TopicConfig(name="AI", keywords=["ai"], boost_weight=1.0),
            TopicConfig(name="ML", keywords=["machine learning"], boost_weight=1.5),
        ]
        matcher = TopicMatcher(topics)

        matches = matcher.match_text("AI and machine learning are related")
        assert len(matches) == 2
        topic_names = {m.topic_name for m in matches}
        assert topic_names == {"AI", "ML"}

    def test_empty_text(self) -> None:
        """Empty text should return no matches."""
        topic = TopicConfig(name="AI", keywords=["ai"], boost_weight=1.5)
        matcher = TopicMatcher([topic])
        matches = matcher.match_text("")
        assert matches == []


class TestCountMatches:
    """Tests for count_matches method."""

    def test_no_matches(self) -> None:
        """No matches returns empty dict."""
        topic = TopicConfig(name="AI", keywords=["ai"], boost_weight=1.5)
        matcher = TopicMatcher([topic])
        counts = matcher.count_matches("Hello world")
        assert counts == {}

    def test_single_match_count(self) -> None:
        """Single match returns count of 1."""
        topic = TopicConfig(name="AI", keywords=["ai"], boost_weight=1.5)
        matcher = TopicMatcher([topic])
        counts = matcher.count_matches("The AI revolution")
        assert counts == {"AI": 1}

    def test_multiple_matches_count(self) -> None:
        """Multiple matches return correct counts."""
        topics = [
            TopicConfig(name="AI", keywords=["ai"], boost_weight=1.0),
            TopicConfig(name="ML", keywords=["ml"], boost_weight=1.5),
        ]
        matcher = TopicMatcher(topics)
        counts = matcher.count_matches("AI and ML together")
        assert counts == {"AI": 1, "ML": 1}


class TestComputeBoostScore:
    """Tests for compute_boost_score method."""

    def test_no_match_zero_score(self) -> None:
        """No matches returns zero score."""
        topic = TopicConfig(name="AI", keywords=["ai"], boost_weight=1.5)
        matcher = TopicMatcher([topic])
        score = matcher.compute_boost_score("Hello world", topic_match_weight=2.0)
        assert score == 0.0

    def test_single_match_score(self) -> None:
        """Single match returns correct boost score."""
        topic = TopicConfig(name="AI", keywords=["ai"], boost_weight=1.5)
        matcher = TopicMatcher([topic])
        score = matcher.compute_boost_score("The AI revolution", topic_match_weight=2.0)
        # boost_weight * topic_match_weight = 1.5 * 2.0 = 3.0
        assert score == 3.0

    def test_multiple_matches_score(self) -> None:
        """Multiple matches sum up correctly."""
        topics = [
            TopicConfig(name="AI", keywords=["ai"], boost_weight=1.0),
            TopicConfig(name="ML", keywords=["ml"], boost_weight=2.0),
        ]
        matcher = TopicMatcher(topics)
        score = matcher.compute_boost_score(
            "AI and ML together", topic_match_weight=1.5
        )
        # (1.0 * 1.5) + (2.0 * 1.5) = 1.5 + 3.0 = 4.5
        assert score == 4.5

    def test_zero_weight_multiplier(self) -> None:
        """Zero weight multiplier returns zero score."""
        topic = TopicConfig(name="AI", keywords=["ai"], boost_weight=1.5)
        matcher = TopicMatcher([topic])
        score = matcher.compute_boost_score("The AI revolution", topic_match_weight=0.0)
        assert score == 0.0


class TestEdgeCases:
    """Edge case tests for TopicMatcher."""

    def test_empty_topics_list(self) -> None:
        """TopicMatcher with empty topics list should not match anything."""
        matcher = TopicMatcher([])
        matches = matcher.match_text("any text here")
        assert matches == []

    def test_special_regex_characters(self) -> None:
        """Keywords with regex special characters should be escaped."""
        topic = TopicConfig(
            name="Special", keywords=["c++", "c#", ".net"], boost_weight=1.0
        )
        matcher = TopicMatcher([topic])

        assert len(matcher.match_text("I love c++")) == 1
        assert len(matcher.match_text("I use c#")) == 1
        assert len(matcher.match_text("I know .net")) == 1

    def test_very_long_text(self) -> None:
        """Matcher should handle very long text efficiently."""
        topic = TopicConfig(name="AI", keywords=["ai"], boost_weight=1.5)
        matcher = TopicMatcher([topic])

        # Create text with 10000 words + "ai" in the middle
        long_text = " ".join(["word"] * 5000) + " ai " + " ".join(["word"] * 5000)
        matches = matcher.match_text(long_text)
        assert len(matches) == 1
