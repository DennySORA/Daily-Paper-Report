"""Prompt templates for LLM paper relevance evaluation."""

from src.features.config.schemas.topics import TopicConfig
from src.linker.models import Story


SYSTEM_INSTRUCTION = (
    "You are an expert AI/ML research curator for practitioners and researchers "
    "focused on large language models, AI agents, multi-agent systems, reasoning, "
    "alignment, and safety. "
    "Your task is to evaluate papers on BOTH topical relevance AND research quality. "
    "Score generously for papers that: (a) advance LLM/agent capabilities, "
    "(b) introduce novel multi-agent architectures or orchestration, "
    "(c) propose new safety/alignment methods, or (d) provide practical frameworks "
    "for agentic systems, even when applied to specific domains. "
    "Score lower for papers that merely USE LLMs as a black-box tool for narrow "
    "domain tasks without methodological contribution. "
    "Prioritize: (1) novelty of approach, (2) practical utility for AI practitioners, "
    "(3) broad impact and applicability, (4) methodological rigor. "
    "Penalize: keyword-stuffing without substance, trivial prompt engineering, "
    "routine domain applications with no AI methodology contribution. "
    "Respond ONLY with a JSON array, no markdown fences or extra text."
)

_BATCH_TEMPLATE = """## Topics of Interest
{topics_section}

## Papers to Evaluate
{papers_section}

## Scoring Rubric
Rate each paper considering BOTH relevance and quality:

- **0.85-1.0**: Breakthrough or highly novel work. New architectures, paradigm-shifting methods,
  or major advances in LLM/agent/reasoning/safety capabilities. Papers from top venues
  (ICLR, NeurIPS, ICML, ACL) or leading labs (Google DeepMind, OpenAI, Anthropic, Meta FAIR,
  Stanford, MIT, CMU) that practitioners must read.
- **0.7-0.84**: Significant contribution with clear novelty. New training techniques,
  meaningful benchmark results, practical frameworks, or open-source tools that advance
  the field. Theoretical advances that explain WHY existing methods work (e.g., proving
  properties of attention mechanisms). Cross-model safety findings with empirical evidence.
  Production-scale systems with real-world deployment insights.
- **0.5-0.69**: Solid work with some novelty. Useful ablations, new datasets, meaningful
  improvements on existing approaches, or insightful analysis of existing methods.
- **0.3-0.49**: Incremental or narrow. Applies existing methods to specific domains without
  methodological novelty, or provides minor improvements without new insights.
- **0.1-0.29**: Tangentially related. Domain-specific applications (e.g., LLMs for medical
  diagnosis, weather prediction, agriculture, particle physics) without contributions to
  core AI/ML methodology. Papers that mention AI keywords but focus on domain science.
- **0.0-0.09**: Not relevant. Pure domain science, unrelated to AI/ML, or trivial extensions.

CRITICAL SCORING RULES:
1. Keyword density does NOT equal quality. A paper mentioning "LLM" 20 times can still be 0.2.
2. DOMAIN vs METHOD: A paper about "using transformers for crop yield prediction" is domain (0.2).
   A paper about "improving transformer attention for long sequences" is method (0.6+).
3. TOP-VENUE ACCEPTANCE (NeurIPS, ICML, ICLR, ACL, CVPR oral/spotlight) adds +0.1 to base score.
4. OPEN-SOURCE code/models with the paper adds +0.05 to base score.

## Output Format
Respond with a JSON array. Each element must have these fields:
- "id": the story_id exactly as given
- "score": float from 0.0 to 1.0 using the rubric above
- "rationale": one sentence explaining the score
- "topics": list of matched topic names (empty list if none)

Example:
[{{"id": "example-1", "score": 0.85, "rationale": "Novel RLHF variant with strong empirical results, accepted at ICLR.", "topics": ["Alignment & RLHF", "Large Language Models"]}}]
"""


def build_topics_section(topics: list[TopicConfig]) -> str:
    """Build the topics section of the prompt.

    Args:
        topics: Configured topic definitions with keywords.

    Returns:
        Formatted topics section string.
    """
    lines: list[str] = []
    for topic in topics:
        keywords_str = ", ".join(topic.keywords)
        lines.append(f"- **{topic.name}**: {keywords_str}")
    return "\n".join(lines)


def _extract_abstract(story: Story) -> str:
    """Extract abstract text from a story's raw items.

    Args:
        story: Story to extract abstract from.

    Returns:
        Abstract text or empty string if not found.
    """
    import json

    for item in story.raw_items:
        try:
            raw = json.loads(item.raw_json)
        except (json.JSONDecodeError, TypeError):
            continue
        for field_name in ("abstract_snippet", "summary", "readme_summary"):
            value = raw.get(field_name)
            if isinstance(value, str) and value:
                return value
    return ""


def build_batch_prompt(
    stories: list[Story],
    topics: list[TopicConfig],
) -> str:
    """Build a batch evaluation prompt for multiple stories.

    Args:
        stories: Stories to evaluate (up to batch size).
        topics: Configured topic definitions.

    Returns:
        Formatted prompt string.
    """
    topics_section = build_topics_section(topics)

    paper_lines: list[str] = []
    for i, story in enumerate(stories, 1):
        abstract = _extract_abstract(story)
        abstract_part = f" | Abstract: {abstract}" if abstract else ""
        paper_lines.append(
            f"{i}. [{story.story_id}] Title: {story.title}{abstract_part}"
        )

    papers_section = "\n".join(paper_lines)

    return _BATCH_TEMPLATE.format(
        topics_section=topics_section,
        papers_section=papers_section,
    )
