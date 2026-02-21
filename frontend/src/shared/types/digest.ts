/**
 * Type definitions for the Daily Paper Report digest data.
 */

export interface StoryLink {
  link_type: 'blog' | 'paper' | 'model' | 'github' | 'arxiv' | 'hf' | string
  source_id: string
  tier: number
  title: string
  url: string
}

export interface HfMetadata {
  pipeline_tag?: string
  downloads?: number
  likes?: number
  license?: string
}

export interface EntityDetail {
  name: string
  type: 'organization' | 'researcher' | 'institution'
}

export interface ScoreBreakdown {
  total_score: number
  tier_score: number
  kind_score: number
  topic_score: number
  recency_score: number
  entity_score: number
  citation_score: number
  cross_source_score: number
  semantic_score: number
  llm_relevance_score: number
}

export interface Story {
  story_id: string
  title: string
  arxiv_id: string | null
  entities: string[]
  github_release_url: string | null
  hf_model_id: string | null
  item_count: number
  links: StoryLink[]
  primary_link: StoryLink
  published_at: string | null
  section: string | null
  // New metadata fields
  authors: string[]
  summary: string | null
  categories: string[]
  source_name: string | null
  first_seen_at: string | null // When item was first seen by crawler
  // HuggingFace-specific metadata
  hf_metadata?: HfMetadata | null
  // Score breakdown from ranker
  scores?: ScoreBreakdown
  // Traditional Chinese translations (optional, populated by translation phase)
  title_zh?: string | null
  summary_zh?: string | null
}

export interface SourceStatus {
  source_id: string
  name: string
  method: string
  category: string
  tier: number
  status: 'HAS_UPDATE' | 'NO_UPDATE' | 'FETCH_FAILED' | 'PARSE_FAILED' | string
  reason_code: string
  reason_text: string
  remediation_hint: string | null
  items_new: number
  items_updated: number
  newest_item_date: string | null
  last_fetch_status_code: number | null
}

export interface RunInfo {
  run_id: string
  started_at: string
  finished_at: string
  success: boolean
  items_total: number
  stories_total: number
  error_summary: string | null
}

export interface DigestData {
  generated_at: string
  run_date: string
  run_id: string
  run_info: RunInfo
  top5: Story[]
  papers: Story[]
  model_releases_by_entity: Record<string, Story[]>
  radar: Story[]
  sources_status: SourceStatus[]
  archive_dates: string[]
  entity_catalog: Record<string, EntityDetail>
}

export type SectionType = 'top5' | 'papers' | 'models' | 'radar'
export type IconName = 'star' | 'document' | 'rocket' | 'radar' | 'cpu' | 'inbox'

export interface SectionConfig {
  type: SectionType
  title: string
  description: string
  iconName: IconName
  accentColor: 'amber' | 'purple' | 'cyan' | 'emerald'
}

export const SECTION_CONFIGS: Record<SectionType, SectionConfig> = {
  top5: {
    type: 'top5',
    title: 'Top 5 Must-Read',
    description:
      'Curated selection of the most significant AI/ML developments today, combining breakthrough research, major releases, and high-impact announcements.',
    iconName: 'star',
    accentColor: 'amber',
  },
  papers: {
    type: 'papers',
    title: 'Papers',
    description:
      'Latest research papers from arXiv and academic sources, covering machine learning, NLP, computer vision, and AI safety.',
    iconName: 'document',
    accentColor: 'purple',
  },
  models: {
    type: 'models',
    title: 'Model Releases',
    description:
      'New model releases and updates from leading AI labs and the open-source community.',
    iconName: 'rocket',
    accentColor: 'cyan',
  },
  radar: {
    type: 'radar',
    title: 'Radar',
    description:
      'Broader AI ecosystem updates including blog posts, tools, datasets, and industry news worth tracking.',
    iconName: 'radar',
    accentColor: 'emerald',
  },
}
