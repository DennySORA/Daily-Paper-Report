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

// Strip HTML tags from text
const stripHtml = (html: string): string => {
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/&[a-zA-Z0-9#]+;/g, ' ')
    .trim()
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

// Truncate summary with smart word boundary
const truncatedSummary = computed(() => {
  if (!props.story.summary) return null
  const cleanSummary = stripHtml(props.story.summary)
  if (!cleanSummary) return null

  // Filter out summaries that look like image alt text
  if (looksLikeImageAlt(cleanSummary)) return null

  const maxLength = props.compact ? 100 : 200
  if (cleanSummary.length <= maxLength) return cleanSummary

  const truncated = cleanSummary.slice(0, maxLength)
  const lastSpace = truncated.lastIndexOf(' ')
  return (lastSpace > maxLength * 0.7 ? truncated.slice(0, lastSpace) : truncated).trim() + '...'
})

// Display authors with smart truncation
const displayAuthors = computed(() => {
  if (!props.story.authors || props.story.authors.length === 0) return null
  if (props.story.authors.length <= 3) return props.story.authors.join(', ')
  return `${props.story.authors.slice(0, 3).join(', ')} +${props.story.authors.length - 3} more`
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
    classes.push('py-3', 'px-4')
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
</script>

<template>
  <article
    :class="cardClasses"
    :data-testid="`story-card-${story.story_id}`"
  >
    <div class="flex items-start gap-3">
      <!-- Rank badge -->
      <div
        v-if="rank"
        class="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg font-bold text-sm transition-all"
        :class="
          rank <= 3
            ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400 group-hover:bg-amber-500/25'
            : 'bg-[var(--color-surface-overlay)] text-[var(--color-text-tertiary)] group-hover:bg-[var(--color-surface-sunken)]'
        "
        style="font-family: var(--font-mono)"
        :data-testid="`story-rank-${rank}`"
      >
        {{ rank }}
      </div>

      <div class="flex-1 min-w-0 space-y-2">
        <!-- Header: Featured badge, Category & Source -->
        <div class="flex flex-wrap items-center gap-2">
          <span
            v-if="featured"
            class="badge badge-top-pick"
          >
            Top Pick
          </span>
          <span
            v-if="showCategories && categoryLabel"
            class="badge badge-category badge-papers"
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
          class="font-semibold leading-snug"
          :class="compact ? 'text-[0.8125rem]' : 'text-[0.9375rem]'"
          style="font-family: var(--font-display)"
        >
          <a
            :href="story.primary_link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-start gap-2 text-[var(--color-text-primary)] hover:text-[var(--color-accent-primary)] transition-colors focus-outline rounded group/link"
            :data-testid="`story-link-${story.story_id}`"
          >
            <span class="line-clamp-2">{{ story.title }}</span>
            <svg
              class="flex-shrink-0 w-3.5 h-3.5 mt-0.5 opacity-0 -translate-x-1 group-hover/link:opacity-50 group-hover/link:translate-x-0 transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] text-[var(--color-text-tertiary)]"
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
          class="text-[0.8125rem] text-[var(--color-text-secondary)] line-clamp-1"
        >
          {{ displayAuthors }}
        </p>

        <!-- Summary/Abstract -->
        <p
          v-if="showSummary && truncatedSummary"
          class="text-[0.8125rem] text-[var(--color-text-tertiary)] leading-relaxed line-clamp-3"
        >
          {{ truncatedSummary }}
        </p>

        <!-- Meta info -->
        <div class="paper-card-meta">
          <!-- Time -->
          <span
            class="paper-card-time"
            :title="formatDate(story.published_at)"
          >
            <svg
              class="w-3 h-3 opacity-50"
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
            <span class="text-[var(--color-border-default)]">·</span>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="entity in story.entities"
                :key="entity"
                class="badge badge-muted text-[0.625rem] py-0.5"
              >
                {{ entity }}
              </span>
            </div>
          </template>

          <!-- arXiv ID -->
          <template v-if="showArxiv && story.arxiv_id">
            <span class="text-[var(--color-border-default)]">·</span>
            <code class="bg-[var(--color-surface-sunken)] px-1.5 py-0.5 rounded text-[0.625rem] text-[var(--color-text-tertiary)]">
              arXiv:{{ story.arxiv_id }}
            </code>
          </template>
        </div>

        <!-- Additional links -->
        <div
          v-if="story.links.length > 1"
          class="flex flex-wrap gap-1.5 pt-3 border-t border-[var(--color-border-subtle)]"
        >
          <a
            v-for="link in story.links"
            :key="link.url"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1 px-2 py-1 text-[0.6875rem] font-semibold text-[var(--color-text-secondary)] bg-[var(--color-surface-overlay)] rounded-md border border-[var(--color-border-subtle)] hover:bg-[var(--color-surface-sunken)] hover:border-[var(--color-border-default)] hover:text-[var(--color-accent-primary)] transition-all focus-outline"
            :title="link.title"
          >
            <svg
              v-if="link.link_type === 'github'"
              class="w-3 h-3"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
              />
            </svg>
            <svg
              v-else
              class="w-3 h-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span>{{ getLinkTypeLabel(link.link_type) }}</span>
          </a>
        </div>
      </div>
    </div>
  </article>
</template>
