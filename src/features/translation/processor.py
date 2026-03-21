"""Batch LLM translation orchestrator for Traditional Chinese."""

from __future__ import annotations

from pathlib import Path

import structlog

from src.features.llm.errors import LlmApiError, LlmProcessingError
from src.features.llm.json_utils import (
    json_candidates,
    strip_markdown_fences,
    try_parse_json_array,
)
from src.features.llm.protocols import LlmClient
from src.features.translation.models import TranslationCache, TranslationEntry
from src.features.translation.prompts import (
    SYSTEM_INSTRUCTION,
    build_translation_prompt,
)


logger = structlog.get_logger()

BATCH_SIZE = 5
_MAX_BATCH_RETRIES = 1
_MAX_RAW_RESPONSE_LOG_LEN = 300


class TranslationProcessor:
    """Orchestrates batch LLM translation of story titles and summaries.

    Translates stories to Traditional Chinese using the same Gemini
    CodeAssist client and batch/cache/retry patterns established by
    LlmRelevanceProcessor.
    """

    def __init__(
        self,
        client: LlmClient,
        output_dir: Path,
    ) -> None:
        """Initialize the translation processor.

        Args:
            client: Any LLM client implementing the LlmClient protocol.
            output_dir: Output directory for cache file storage.
        """
        self._client = client
        self._cache = TranslationCache(output_dir / "api" / "translations_zh.json")
        self._log = logger.bind(component="translation", subcomponent="processor")

    def translate(
        self, stories: list[dict[str, object]]
    ) -> dict[str, TranslationEntry]:
        """Translate all stories, skipping those already cached.

        Args:
            stories: Story dicts (from to_json_dict), each with at
                     minimum 'story_id', 'title', and optionally 'summary'.

        Returns:
            Map of story_id to TranslationEntry for all stories
            (cached + newly translated).
        """
        self._cache.load()

        uncached = [
            s for s in stories if not self._cache.has(str(s.get("story_id", "")))
        ]

        self._log.info(
            "translation_started",
            total=len(stories),
            cached=len(stories) - len(uncached),
            to_translate=len(uncached),
        )

        if uncached:
            batches = _create_batches(uncached, BATCH_SIZE)
            for batch_idx, batch in enumerate(batches):
                self._process_batch(batch, batch_idx)

            self._cache.save()

        return dict(self._cache.entries)

    def _process_batch(
        self,
        batch: list[dict[str, object]],
        batch_idx: int,
    ) -> None:
        """Process a single batch of stories for translation.

        On failure or partial result, retries the batch once. If retry
        still leaves untranslated stories, falls back to translating
        each missing story individually.

        Args:
            batch: Story dicts in this batch.
            batch_idx: Batch index for logging.
        """
        entries = self._attempt_batch(batch, batch_idx, attempt=0)
        for entry in entries:
            self._cache.put(entry)

        translated_ids = {e.story_id for e in entries}
        missing = [s for s in batch if str(s.get("story_id", "")) not in translated_ids]

        if not missing:
            self._log.info(
                "translation_batch_complete",
                batch=batch_idx,
                translated=len(entries),
                batch_size=len(batch),
            )
            return

        # Retry the missing stories as a batch once.
        if len(missing) > 1:
            retry_entries = self._attempt_batch(missing, batch_idx, attempt=1)
            for entry in retry_entries:
                self._cache.put(entry)
            retry_ids = {e.story_id for e in retry_entries}
            missing = [
                s for s in missing if str(s.get("story_id", "")) not in retry_ids
            ]

        # Fall back to single-item translation for any remaining.
        single_ok = 0
        for story in missing:
            sid = str(story.get("story_id", ""))
            single_entries = self._attempt_batch([story], batch_idx, attempt=2)
            for entry in single_entries:
                self._cache.put(entry)
                single_ok += 1
            if not single_entries:
                self._log.warning(
                    "translation_story_failed",
                    batch=batch_idx,
                    story_id=sid,
                    title=str(story.get("title", ""))[:120],
                )

        total_translated = len(batch) - len(missing) + single_ok
        self._log.info(
            "translation_batch_complete",
            batch=batch_idx,
            translated=total_translated,
            batch_size=len(batch),
            retried_single=single_ok,
            failed_ids=[
                str(s.get("story_id", ""))
                for s in missing
                if not self._cache.has(str(s.get("story_id", "")))
            ],
        )

    def _attempt_batch(
        self,
        batch: list[dict[str, object]],
        batch_idx: int,
        attempt: int,
    ) -> list[TranslationEntry]:
        """Make a single translation attempt for a batch.

        Args:
            batch: Story dicts to translate.
            batch_idx: Batch index for logging.
            attempt: Attempt number (0=first, 1=retry, 2=single fallback).

        Returns:
            List of successfully parsed TranslationEntry objects.
        """
        prompt = build_translation_prompt(batch)
        story_ids = [str(s.get("story_id", "")) for s in batch]

        try:
            raw_response = self._client.generate_content(
                prompt=prompt,
                system_instruction=SYSTEM_INSTRUCTION,
            )
        except LlmApiError as exc:
            self._log.warning(
                "translation_batch_api_error",
                batch=batch_idx,
                attempt=attempt,
                story_ids=story_ids,
                error=str(exc),
            )
            return []

        try:
            entries = self._parse_response(raw_response, batch)
        except LlmProcessingError as exc:
            self._log.warning(
                "translation_batch_parse_error",
                batch=batch_idx,
                attempt=attempt,
                story_ids=story_ids,
                error=str(exc),
                raw_response_preview=raw_response[:_MAX_RAW_RESPONSE_LOG_LEN],
            )
            return []

        if not entries and batch:
            self._log.warning(
                "translation_batch_empty_result",
                batch=batch_idx,
                attempt=attempt,
                story_ids=story_ids,
                raw_response_preview=raw_response[:_MAX_RAW_RESPONSE_LOG_LEN],
            )

        return entries

    def _parse_response(
        self,
        raw_response: str,
        batch: list[dict[str, object]],
    ) -> list[TranslationEntry]:
        """Parse the LLM JSON response into TranslationEntry objects.

        Args:
            raw_response: Raw text response from the LLM.
            batch: Original batch for validation.

        Returns:
            List of parsed TranslationEntry objects.

        Raises:
            LlmProcessingError: If response cannot be parsed.
        """
        text = strip_markdown_fences(raw_response)

        parsed: list[dict[str, object]] | None = None
        for candidate in json_candidates(text):
            parsed = try_parse_json_array(candidate)
            if parsed is not None:
                break

        if parsed is None:
            msg = f"Failed to parse translation response: {text[:200]}"
            raise LlmProcessingError(msg)

        valid_ids = {str(s.get("story_id", "")) for s in batch}
        results: list[TranslationEntry] = []

        for item in parsed:
            if not isinstance(item, dict):
                continue

            story_id = str(item.get("id", ""))
            if story_id not in valid_ids:
                continue

            title_zh = str(item.get("title_zh", ""))
            summary_zh = str(item.get("summary_zh", ""))

            if not title_zh:
                continue

            results.append(
                TranslationEntry(
                    story_id=story_id,
                    title_zh=title_zh,
                    summary_zh=summary_zh,
                )
            )

        return results


def _create_batches(
    items: list[dict[str, object]], batch_size: int
) -> list[list[dict[str, object]]]:
    """Split items into fixed-size batches.

    Args:
        items: Items to batch.
        batch_size: Maximum items per batch.

    Returns:
        List of item batches.
    """
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
