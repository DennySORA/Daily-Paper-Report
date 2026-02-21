"""Prompt templates for LLM-powered Traditional Chinese translation."""

from __future__ import annotations


SYSTEM_INSTRUCTION = (
    "You are a professional translator specializing in AI/ML academic papers. "
    "Translate to Traditional Chinese (\u7e41\u9ad4\u4e2d\u6587). "
    "Preserve technical terms, model names, acronyms, and proper nouns in English. "
    "For example: 'Transformer', 'GPT-4', 'RLHF', 'fine-tuning' should remain in English. "
    "Maintain the academic tone and precision of the original text. "
    "Respond ONLY with a JSON array, no markdown fences or extra text."
)

_BATCH_TEMPLATE = """## Stories to Translate

{stories_section}

## Output Format
Respond with a JSON array. Each element must have these fields:
- "id": the story_id exactly as given
- "title_zh": the title translated to Traditional Chinese
- "summary_zh": the summary translated to Traditional Chinese (empty string if no summary)

Keep technical terms, model names, acronyms, and proper nouns in English within the Chinese text.

Example:
[{{"id": "example-1", "title_zh": "\u57fa\u65bc Transformer \u7684\u65b0\u578b\u591a\u6a21\u614b\u5b78\u7fd2\u67b6\u69cb", "summary_zh": "\u672c\u6587\u63d0\u51fa\u4e86\u4e00\u7a2e\u65b0\u7684 multi-modal learning \u67b6\u69cb..."}}]
"""


def build_translation_prompt(stories: list[dict[str, object]]) -> str:
    """Build a batch translation prompt for multiple stories.

    Args:
        stories: Story dicts with at minimum 'story_id', 'title',
                 and optionally 'summary' fields.

    Returns:
        Formatted prompt string for translation.
    """
    lines: list[str] = []
    for i, story in enumerate(stories, 1):
        story_id = story.get("story_id", "")
        title = story.get("title", "")
        summary = story.get("summary", "") or ""
        summary_part = f"\n   Summary: {summary}" if summary else ""
        lines.append(f"{i}. [{story_id}] Title: {title}{summary_part}")

    stories_section = "\n".join(lines)

    return _BATCH_TEMPLATE.format(stories_section=stories_section)
