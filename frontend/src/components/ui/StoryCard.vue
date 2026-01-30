<script setup lang="ts">
import type { Story } from '@/types/digest'
import { computed } from 'vue'

interface Props {
  story: Story
  rank?: number
  showEntities?: boolean
  showArxiv?: boolean
  showSummary?: boolean
  showAuthors?: boolean
  showCategories?: boolean
  showSource?: boolean
  featured?: boolean
  accentType?: 'highlight' | 'papers' | 'models' | 'sources' | 'radar'
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  rank: undefined,
  showEntities: false,
  showArxiv: false,
  showSummary: true,
  showAuthors: true,
  showCategories: true,
  showSource: true,
  featured: false,
  accentType: undefined,
  compact: false,
})

// Format date as absolute date
const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return 'Date unknown'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Format as relative time
const formatRelativeTime = (dateStr: string | null): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`
  return formatDate(dateStr)
}

// Get link type label
const getLinkTypeLabel = (linkType: string): string => {
  const labels: Record<string, string> = {
    blog: 'Blog',
    paper: 'Paper',
    model: 'Model',
    github: 'GitHub',
    arxiv: 'arXiv',
    huggingface: 'HuggingFace',
    official: 'Official',
  }
  return labels[linkType] ?? linkType
}

// Decode LaTeX escape sequences commonly found in arXiv data
const decodeLatex = (text: string): string => {
  if (!text) return text

  // First handle math mode superscripts and subscripts (e.g., $^3$, $_{10}$)
  const result = text
    // Superscripts in math mode: $^{...}$ or $^X$
    .replace(/\$\^{([^}]+)}\$/g, (_, content) => toSuperscript(content))
    .replace(/\$\^([0-9a-zA-Z])\$/g, (_, char) => toSuperscript(char))
    // Subscripts in math mode: $_{...}$ or $_X$
    .replace(/\$_{([^}]+)}\$/g, (_, content) => toSubscript(content))
    .replace(/\$_([0-9a-zA-Z])\$/g, (_, char) => toSubscript(char))
    // Remove remaining empty math delimiters
    .replace(/\$\$/g, '')

  return result
    // Accented characters
    .replace(/\\'e/g, 'é')
    .replace(/\\'a/g, 'á')
    .replace(/\\'i/g, 'í')
    .replace(/\\'o/g, 'ó')
    .replace(/\\'u/g, 'ú')
    .replace(/\\"e/g, 'ë')
    .replace(/\\"a/g, 'ä')
    .replace(/\\"i/g, 'ï')
    .replace(/\\"o/g, 'ö')
    .replace(/\\"u/g, 'ü')
    .replace(/\\`e/g, 'è')
    .replace(/\\`a/g, 'à')
    .replace(/\\`i/g, 'ì')
    .replace(/\\`o/g, 'ò')
    .replace(/\\`u/g, 'ù')
    .replace(/\\~n/g, 'ñ')
    .replace(/\\c\{c\}/g, 'ç')
    .replace(/\\c c/g, 'ç')
    .replace(/\\\^e/g, 'ê')
    .replace(/\\\^a/g, 'â')
    .replace(/\\\^i/g, 'î')
    .replace(/\\\^o/g, 'ô')
    .replace(/\\\^u/g, 'û')
    // Common LaTeX symbols
    .replace(/\\&/g, '&')
    .replace(/\\\$/g, '$')
    .replace(/\\%/g, '%')
    .replace(/\\_/g, '_')
    .replace(/\\#/g, '#')
    .replace(/\\{/g, '{')
    .replace(/\\}/g, '}')
    // Handle remaining backslash escapes
    .replace(/\\\\/g, '')
}

// Convert digits/letters to Unicode superscript
const toSuperscript = (str: string): string => {
  const superscriptMap: Record<string, string> = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
    'n': 'ⁿ', 'i': 'ⁱ',
  }
  return str.split('').map(c => superscriptMap[c] || c).join('')
}

// Convert digits/letters to Unicode subscript
const toSubscript = (str: string): string => {
  const subscriptMap: Record<string, string> = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
    '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎',
    'a': 'ₐ', 'e': 'ₑ', 'o': 'ₒ', 'x': 'ₓ',
  }
  return str.split('').map(c => subscriptMap[c] || c).join('')
}

// Strip HTML tags from text
const stripHtml = (html: string): string => {
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/&[a-zA-Z0-9#]+;/g, ' ')
    .trim()
}

// Clean arXiv metadata prefix from summary
const cleanArxivPrefix = (text: string): string => {
  // Remove patterns like "arXiv:2507.23541v4 Announce Type: replace Abstract: "
  // or "arXiv:2507.23541 Announce Type: new Abstract: "
  // or "arXiv:2410.01553v2 Announce Type: replace-cross Abstract: "
  return text
    .replace(/^arXiv:\d+\.\d+(?:v\d+)?\s+Announce Type:\s*[\w-]+\s*Abstract:\s*/i, '')
    .trim()
}

// Clean LaTeX emphasis and formatting commands from text
const cleanLatexEmphasis = (text: string): string => {
  return text
    // Handle {\em text} -> text
    .replace(/\{\\em\s+([^}]+)\}/g, '$1')
    // Handle \emph{text} -> text
    .replace(/\\emph\{([^}]+)\}/g, '$1')
    // Handle {\it text} -> text
    .replace(/\{\\it\s+([^}]+)\}/g, '$1')
    // Handle {\bf text} -> text
    .replace(/\{\\bf\s+([^}]+)\}/g, '$1')
    // Handle \textit{text} -> text
    .replace(/\\textit\{([^}]+)\}/g, '$1')
    // Handle \textbf{text} -> text
    .replace(/\\textbf\{([^}]+)\}/g, '$1')
}

// Check if text looks like image alt text (not a real summary)
const looksLikeImageAlt = (text: string): boolean => {
  const altPatterns = [
    /^illustration\s+of\s+/i,
    /^image\s+of\s+/i,
    /^photo\s+of\s+/i,
    /^screenshot\s+of\s+/i,
    /^diagram\s+(of|showing)\s+/i,
    /^figure\s+\d+/i,
    /^a\s+(photo|image|illustration)\s+/i,
  ]
  return altPatterns.some((pattern) => pattern.test(text.trim()))
}

// Clean and prepare summary (no truncation for scrollable display)
const cleanedSummary = computed(() => {
  if (!props.story.summary) return null
  let cleanSummary = stripHtml(props.story.summary)
  if (!cleanSummary) return null

  // Remove arXiv metadata prefix
  cleanSummary = cleanArxivPrefix(cleanSummary)
  if (!cleanSummary) return null

  // Clean LaTeX emphasis commands
  cleanSummary = cleanLatexEmphasis(cleanSummary)

  // Filter out summaries that look like image alt text
  if (looksLikeImageAlt(cleanSummary)) return null

  return cleanSummary
})

// Truncate summary for compact mode only
const truncatedSummary = computed(() => {
  if (!cleanedSummary.value) return null

  // Only truncate in compact mode
  if (props.compact) {
    const maxLength = 120
    if (cleanedSummary.value.length <= maxLength) return cleanedSummary.value
    const truncated = cleanedSummary.value.slice(0, maxLength)
    const lastSpace = truncated.lastIndexOf(' ')
    return (lastSpace > maxLength * 0.7 ? truncated.slice(0, lastSpace) : truncated).trim() + '...'
  }

  // For non-compact mode, return full cleaned summary (will be scrollable)
  return cleanedSummary.value
})

// Check if summary is long enough to be scrollable (more than ~4 lines worth)
const isScrollableSummary = computed(() => {
  if (!cleanedSummary.value || props.compact) return false
  // Approximate: ~80 chars per line, 4 lines = 320 chars threshold
  return cleanedSummary.value.length > 320
})

// Display authors with smart truncation and LaTeX decoding
const displayAuthors = computed(() => {
  if (!props.story.authors || props.story.authors.length === 0) return null
  const decodedAuthors = props.story.authors.map(author => decodeLatex(author))
  if (decodedAuthors.length <= 3) return decodedAuthors.join(', ')
  return `${decodedAuthors.slice(0, 3).join(', ')} +${decodedAuthors.length - 3} more`
})

// Decoded title for display
const displayTitle = computed(() => {
  return decodeLatex(props.story.title)
})

// Get category label
const categoryLabel = computed(() => {
  if (!props.story.categories || props.story.categories.length === 0) return null
  return props.story.categories[0]
})

// Get source display name
const sourceName = computed(() => {
  return props.story.source_name || formatSourceId(props.story.primary_link.source_id)
})

// Format source ID to readable name
const formatSourceId = (sourceId: string): string => {
  return sourceId
    .replace(/^hf-/, '')
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

// Card classes based on props
const cardClasses = computed(() => {
  const classes = ['card', 'paper-card', 'group']

  if (props.featured) {
    classes.push('card-featured')
  }

  if (props.accentType) {
    classes.push(`card-accent`, `card-accent-${props.accentType}`)
  }

  if (props.compact) {
    classes.push('paper-card--compact')
  }

  return classes
})

// Get badge class for source type
const getSourceBadgeClass = (sourceId: string): string => {
  if (sourceId.startsWith('arxiv')) return 'badge-source-arxiv'
  if (sourceId.startsWith('hf-')) return 'badge-source-hf'
  if (sourceId.includes('blog')) return 'badge-source-blog'
  return 'badge-muted'
}

// Get accent badge class
const getAccentBadgeClass = computed(() => {
  if (!props.accentType) return 'badge-muted'
  return `badge-${props.accentType}`
})
</script>

<template>
  <article
    :class="cardClasses"
    :data-testid="`story-card-${story.story_id}`"
  >
    <div class="flex items-start gap-3">
      <!-- Rank badge (for top picks) -->
      <div
        v-if="rank"
        class="rank-badge"
        :class="{ 'rank-badge--top': rank <= 3 }"
        style="font-family: var(--font-mono)"
        :data-testid="`story-rank-${rank}`"
      >
        {{ rank }}
      </div>

      <div class="flex-1 min-w-0 space-y-2.5">
        <!-- Header: Featured badge, Category & Source -->
        <div class="flex flex-wrap items-center gap-2">
          <span
            v-if="featured"
            class="badge badge-top-pick"
          >
            <svg
              class="w-3 h-3"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            Top Pick
          </span>
          <span
            v-if="showCategories && categoryLabel"
            class="badge badge-category"
            :class="getAccentBadgeClass"
          >
            {{ categoryLabel }}
          </span>
          <span
            v-if="showSource && sourceName"
            class="badge badge-category"
            :class="getSourceBadgeClass(story.primary_link.source_id)"
          >
            {{ sourceName }}
          </span>
        </div>

        <!-- Title -->
        <h3
          class="paper-card-title"
          :class="compact ? 'text-[0.8125rem]' : 'text-[0.9375rem]'"
        >
          <a
            :href="story.primary_link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="paper-card-link group/link"
            :data-testid="`story-link-${story.story_id}`"
          >
            <span :class="compact ? 'line-clamp-2' : 'line-clamp-3'">{{ displayTitle }}</span>
            <svg
              class="paper-card-external-icon"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        </h3>

        <!-- Authors -->
        <p
          v-if="showAuthors && displayAuthors"
          class="paper-card-authors"
        >
          <svg
            class="inline-block w-3.5 h-3.5 mr-1.5 opacity-50"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
          {{ displayAuthors }}
        </p>

        <!-- Summary/Abstract -->
        <div
          v-if="showSummary && truncatedSummary"
          class="paper-card-summary-wrapper"
          :class="{ 'paper-card-summary-scrollable': isScrollableSummary }"
        >
          <p class="paper-card-summary">
            {{ truncatedSummary }}
          </p>
        </div>

        <!-- Meta info -->
        <div class="paper-card-meta">
          <!-- Time -->
          <span
            class="paper-card-time"
            :title="formatDate(story.published_at)"
          >
            <svg
              class="w-3.5 h-3.5 opacity-60"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span class="tabular-nums">{{ formatRelativeTime(story.published_at) }}</span>
          </span>

          <!-- Entity badges -->
          <template v-if="showEntities && story.entities.length > 0">
            <span class="meta-divider">·</span>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="entity in story.entities.slice(0, 3)"
                :key="entity"
                class="badge badge-muted text-[0.625rem] py-0.5 px-2"
              >
                {{ entity }}
              </span>
              <span
                v-if="story.entities.length > 3"
                class="badge badge-muted text-[0.625rem] py-0.5 px-2"
              >
                +{{ story.entities.length - 3 }}
              </span>
            </div>
          </template>

          <!-- arXiv ID -->
          <template v-if="showArxiv && story.arxiv_id">
            <span class="meta-divider">·</span>
            <code class="arxiv-id">
              arXiv:{{ story.arxiv_id }}
            </code>
          </template>
        </div>

        <!-- Additional links -->
        <div
          v-if="story.links.length > 1 && !compact"
          class="paper-card-links"
        >
          <a
            v-for="link in story.links.slice(0, 4)"
            :key="link.url"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="paper-card-link-btn"
            :title="link.title"
          >
            <svg
              v-if="link.link_type === 'github'"
              class="w-3.5 h-3.5"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
              />
            </svg>
            <svg
              v-else-if="link.link_type === 'arxiv'"
              class="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
            <svg
              v-else
              class="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
              />
            </svg>
            <span>{{ getLinkTypeLabel(link.link_type) }}</span>
          </a>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   STORY CARD - Premium Paper Display Component
   ═══════════════════════════════════════════════════════════════════════════ */

/* Rank badge */
.rank-badge {
  flex-shrink: 0;
  width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  font-weight: 700;
  font-size: 0.875rem;
  background: var(--color-surface-secondary);
  color: var(--color-text-tertiary);
  border: 1px solid var(--color-border-subtle);
  transition: all var(--duration-base) var(--ease-out);
  position: relative;
}

.rank-badge--top {
  background: linear-gradient(135deg, rgb(251 191 36 / 0.2) 0%, rgb(245 158 11 / 0.12) 100%);
  color: var(--color-section-top);
  border-color: rgb(251 191 36 / 0.4);
  box-shadow: 0 2px 8px rgb(251 191 36 / 0.15);
}

.rank-badge--top::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  background: linear-gradient(135deg, rgb(251 191 36 / 0.3) 0%, transparent 50%);
  opacity: 0;
  transition: opacity var(--duration-base) var(--ease-out);
}

.group:hover .rank-badge {
  transform: scale(1.08) translateY(-2px);
}

.group:hover .rank-badge--top {
  box-shadow: 0 4px 16px rgb(251 191 36 / 0.35);
}

.group:hover .rank-badge--top::before {
  opacity: 1;
}

/* Compact variant */
.paper-card--compact {
  padding: 0.875rem 1rem;
}

.paper-card--compact .paper-card-meta {
  padding-top: 0.625rem;
  margin-top: 0.5rem;
}

/* Title link - Enhanced hover effect */
.paper-card-link {
  display: inline-flex;
  align-items: flex-start;
  gap: 0.5rem;
  color: var(--color-text-primary);
  text-decoration: none;
  transition: all var(--duration-fast) var(--ease-out);
  border-radius: var(--radius-sm);
  position: relative;
}

.paper-card-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background: linear-gradient(90deg, var(--color-accent-primary), var(--color-accent-primary-hover));
  transition: width var(--duration-base) var(--ease-out);
}

.paper-card-link:hover {
  color: var(--color-accent-primary);
}

.paper-card-link:hover::after {
  width: 100%;
}

.paper-card-link:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--color-surface-base), 0 0 0 4px var(--color-border-focus);
}

/* External link icon */
.paper-card-external-icon {
  flex-shrink: 0;
  width: 0.875rem;
  height: 0.875rem;
  margin-top: 0.1875rem;
  opacity: 0;
  transform: translateX(-6px) translateY(4px);
  transition: all var(--duration-base) var(--ease-spring);
  color: var(--color-accent-primary);
}

.paper-card-link:hover .paper-card-external-icon {
  opacity: 0.8;
  transform: translateX(0) translateY(0);
}

/* Authors - Improved styling */
.paper-card-authors {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
  display: flex;
  align-items: center;
}

/* Meta divider */
.meta-divider {
  color: var(--color-border-strong);
  opacity: 0.5;
}

/* arXiv ID */
.arxiv-id {
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  background: var(--color-surface-secondary);
  color: var(--color-text-tertiary);
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-subtle);
  transition: all var(--duration-fast) var(--ease-out);
}

.group:hover .arxiv-id {
  background: var(--color-surface-overlay);
  border-color: var(--color-border-default);
}

/* Additional links section */
.paper-card-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding-top: 0.875rem;
  border-top: 1px solid var(--color-border-subtle);
  margin-top: 0.375rem;
}

.paper-card-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.4375rem 0.75rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: all var(--duration-fast) var(--ease-out);
  position: relative;
  overflow: hidden;
}

.paper-card-link-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--color-accent-primary-glow) 0%, transparent 50%);
  opacity: 0;
  transition: opacity var(--duration-fast) var(--ease-out);
}

.paper-card-link-btn:hover {
  background: var(--color-surface-elevated);
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.paper-card-link-btn:hover::before {
  opacity: 0.5;
}

.paper-card-link-btn:active {
  transform: translateY(0) scale(0.97);
}

.paper-card-link-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--color-surface-base), 0 0 0 4px var(--color-border-focus);
}

/* Icon styling for link buttons */
.paper-card-link-btn svg {
  transition: transform var(--duration-fast) var(--ease-spring);
}

.paper-card-link-btn:hover svg {
  transform: scale(1.1);
}
</style>
