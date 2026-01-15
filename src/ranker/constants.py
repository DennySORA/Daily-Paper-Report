"""Constants for the ranker module."""

# Default kind weights (can be overridden by config)
DEFAULT_KIND_WEIGHTS: dict[str, float] = {
    "blog": 1.5,  # Official blogs are important
    "paper": 1.2,  # Research papers
    "model": 1.8,  # Model releases are high priority
    "release": 1.6,  # Software releases
    "news": 0.8,  # News aggregation
    "docs": 1.0,  # Documentation
    "forum": 0.6,  # Forum discussions
    "social": 0.5,  # Social media
}

# ArXiv category patterns for per-category quota
ARXIV_CATEGORY_PATTERNS: list[str] = [
    "cs.AI",
    "cs.LG",
    "cs.CL",
    "cs.CV",
    "stat.ML",
]

# Days for recency calculation
MAX_RECENCY_DAYS: int = 30

# Output section names
SECTION_TOP5 = "top5"
SECTION_MODEL_RELEASES = "model_releases"
SECTION_PAPERS = "papers"
SECTION_RADAR = "radar"
