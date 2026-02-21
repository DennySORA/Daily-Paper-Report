"""Batch LLM evaluation orchestrator for paper relevance scoring."""

from __future__ import annotations

import json

import structlog

from src.features.config.schemas.topics import TopicConfig
from src.features.llm.client import GeminiCodeAssistClient
from src.features.llm.errors import LlmApiError, LlmProcessingError
from src.features.llm.json_utils import (
    json_candidates,
    strip_markdown_fences,
    try_parse_json_array,
)
from src.features.llm.models import LlmPhaseResult, LlmRelevanceResult
from src.features.llm.prompts import SYSTEM_INSTRUCTION, build_batch_prompt
from src.linker.models import Story


logger = structlog.get_logger()

BATCH_SIZE = 5
_NEUTRAL_SCORE = 0.5


class LlmRelevanceProcessor:
    """Orchestrates batch LLM evaluation of stories.

    Filters stories to those with meaningful content (papers with
    abstracts), batches them, sends to the Gemini API, and parses
    the structured JSON responses.
    """

    def __init__(
        self,
        client: GeminiCodeAssistClient,
        topics: list[TopicConfig],
    ) -> None:
        """Initialize the processor.

        Args:
            client: Configured Gemini CodeAssist client.
            topics: Topic configurations for relevance evaluation.
        """
        self._client = client
        self._topics = topics
        self._log = logger.bind(component="llm", subcomponent="processor")

    def evaluate_stories(self, stories: list[Story]) -> LlmPhaseResult:
        """Evaluate all stories for relevance using the LLM.

        Stories without abstracts or arxiv_ids are skipped as they
        lack sufficient content for meaningful evaluation.

        Args:
            stories: Stories from the linker phase.

        Returns:
            LlmPhaseResult with scores and audit trail.
        """
        result = LlmPhaseResult()

        evaluatable, skipped = self._partition_stories(stories)
        result.stories_skipped = skipped

        if not evaluatable:
            self._log.info("llm_no_evaluatable_stories")
            return result

        batches = self._create_batches(evaluatable)
        self._log.info(
            "llm_evaluation_started",
            stories=len(evaluatable),
            batches=len(batches),
        )

        for batch_idx, batch in enumerate(batches):
            self._process_batch(batch, batch_idx, result)

        self._log.info(
            "llm_evaluation_complete",
            evaluated=result.stories_evaluated,
            skipped=result.stories_skipped,
            api_calls=result.api_calls_made,
            errors=len(result.errors),
        )

        return result

    def _partition_stories(self, stories: list[Story]) -> tuple[list[Story], int]:
        """Split stories into evaluatable and skipped.

        A story is evaluatable if it has an arxiv_id or at least one
        raw item with abstract/summary content.

        Args:
            stories: All input stories.

        Returns:
            Tuple of (evaluatable stories, skip count).
        """
        evaluatable: list[Story] = []
        skipped = 0

        for story in stories:
            if story.arxiv_id or self._has_abstract(story):
                evaluatable.append(story)
            else:
                skipped += 1

        return evaluatable, skipped

    @staticmethod
    def _has_abstract(story: Story) -> bool:
        """Check if a story has abstract content in its raw items."""
        for item in story.raw_items:
            try:
                raw = json.loads(item.raw_json)
            except (json.JSONDecodeError, TypeError):
                continue
            for field_name in ("abstract_snippet", "summary"):
                if isinstance(raw.get(field_name), str) and raw[field_name]:
                    return True
        return False

    @staticmethod
    def _create_batches(stories: list[Story]) -> list[list[Story]]:
        """Split stories into batches of BATCH_SIZE.

        Args:
            stories: Stories to batch.

        Returns:
            List of story batches.
        """
        return [stories[i : i + BATCH_SIZE] for i in range(0, len(stories), BATCH_SIZE)]

    def _process_batch(
        self,
        batch: list[Story],
        batch_idx: int,
        result: LlmPhaseResult,
    ) -> None:
        """Process a single batch of stories.

        On failure, assigns neutral score (0.5) to all stories in the
        batch to avoid penalizing or boosting them unfairly.

        Args:
            batch: Stories in this batch.
            batch_idx: Batch index for logging.
            result: Accumulated phase result (mutated in place).
        """
        prompt = build_batch_prompt(batch, self._topics)

        try:
            raw_response = self._client.generate_content(
                prompt=prompt,
                system_instruction=SYSTEM_INSTRUCTION,
            )
            result.api_calls_made += 1
        except LlmApiError as exc:
            error_msg = f"Batch {batch_idx} API error: {exc}"
            self._log.warning("llm_batch_api_error", batch=batch_idx, error=str(exc))
            result.errors.append(error_msg)
            self._assign_neutral_scores(batch, result)
            return

        try:
            parsed = self._parse_response(raw_response, batch)
        except LlmProcessingError as exc:
            error_msg = f"Batch {batch_idx} parse error: {exc}"
            self._log.warning("llm_batch_parse_error", batch=batch_idx, error=str(exc))
            result.errors.append(error_msg)
            self._assign_neutral_scores(batch, result)
            return

        for llm_result in parsed:
            result.scores[llm_result.story_id] = llm_result.relevance_score
            result.results.append(llm_result)
            result.stories_evaluated += 1

        # Assign neutral scores to any stories not returned by the LLM
        batch_ids = {s.story_id for s in batch}
        returned_ids = {r.story_id for r in parsed}
        for missing_id in batch_ids - returned_ids:
            result.scores[missing_id] = _NEUTRAL_SCORE
            result.stories_evaluated += 1

    def _parse_response(
        self,
        raw_response: str,
        batch: list[Story],
    ) -> list[LlmRelevanceResult]:
        """Parse the LLM JSON response into structured results.

        Handles common response quirks: markdown code fences, extra
        whitespace, and partial JSON arrays.

        Args:
            raw_response: Raw text response from the LLM.
            batch: Original batch for validation context.

        Returns:
            List of parsed LlmRelevanceResult objects.

        Raises:
            LlmProcessingError: If response cannot be parsed at all.
        """
        text = strip_markdown_fences(raw_response)

        entries = self._robust_json_parse(text)

        if not isinstance(entries, list):
            msg = f"Expected JSON array, got {type(entries).__name__}"
            raise LlmProcessingError(msg)

        valid_ids = {s.story_id for s in batch}
        results: list[LlmRelevanceResult] = []

        for entry in entries:
            if not isinstance(entry, dict):
                continue

            story_id = str(entry.get("id", ""))
            if story_id not in valid_ids:
                continue

            score = _clamp_score(entry.get("score", 0.5))
            rationale = str(entry.get("rationale", ""))
            topics_raw = entry.get("topics", [])
            topics = (
                [str(t) for t in topics_raw] if isinstance(topics_raw, list) else []
            )

            results.append(
                LlmRelevanceResult(
                    story_id=story_id,
                    relevance_score=score,
                    rationale=rationale,
                    topics_matched=topics,
                )
            )

        return results

    @staticmethod
    def _robust_json_parse(text: str) -> list[dict[str, object]]:
        """Parse LLM JSON response with fallbacks for common issues.

        Handles: extra data after JSON array, invalid escape sequences,
        and multiple concatenated JSON arrays.

        Args:
            text: Raw JSON text from LLM response.

        Returns:
            Parsed list of entry dicts.

        Raises:
            LlmProcessingError: If no valid JSON can be extracted.
        """
        for candidate in json_candidates(text):
            result = try_parse_json_array(candidate)
            if result is not None:
                return result

        msg = f"Failed to parse LLM response as JSON after all fallbacks: {text[:200]}"
        raise LlmProcessingError(msg)

    @staticmethod
    def _assign_neutral_scores(batch: list[Story], result: LlmPhaseResult) -> None:
        """Assign neutral score to all stories in a failed batch.

        Args:
            batch: Stories that failed evaluation.
            result: Accumulated phase result (mutated in place).
        """
        for story in batch:
            if story.story_id not in result.scores:
                result.scores[story.story_id] = _NEUTRAL_SCORE
                result.stories_evaluated += 1


def _clamp_score(value: object) -> float:
    """Clamp a value to the [0.0, 1.0] range.

    Args:
        value: Raw score value from LLM response.

    Returns:
        Float clamped between 0.0 and 1.0.
    """
    try:
        score = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return _NEUTRAL_SCORE
    return max(0.0, min(1.0, score))
