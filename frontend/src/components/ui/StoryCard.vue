<script setup lang="ts">
  import type { Story } from '@/types/digest'
  import { IconExternalLink, IconGithub, IconDocument } from '@/components/icons'
  import { computed } from 'vue'

  interface Props {
    story: Story
    rank?: number
    showEntities?: boolean
    showArxiv?: boolean
    showSummary?: boolean
    showAuthors?: boolean
    showCategories?: boolean
    accentClass?: string
    compact?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    rank: undefined,
    showEntities: false,
    showArxiv: false,
    showSummary: true,
    showAuthors: true,
    showCategories: true,
    accentClass: '',
    compact: false,
  })

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return 'Date unknown'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const formatRelativeTime = (dateStr: string | null): string => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays}d ago`
    return formatDate(dateStr)
  }

  const getLinkTypeLabel = (linkType: string): string => {
    const labels: Record<string, string> = {
      blog: 'Blog',
      paper: 'Paper',
      model: 'Model',
      github: 'GitHub',
      arxiv: 'arXiv',
      hf: 'HuggingFace',
      official: 'Official',
    }
    return labels[linkType] ?? linkType
  }

  const truncatedSummary = computed(() => {
    if (!props.story.summary) return null
    const maxLength = props.compact ? 120 : 200
    if (props.story.summary.length <= maxLength) return props.story.summary
    return props.story.summary.slice(0, maxLength).trim() + '...'
  })

  const displayAuthors = computed(() => {
    if (!props.story.authors || props.story.authors.length === 0) return null
    if (props.story.authors.length <= 3) return props.story.authors.join(', ')
    return `${props.story.authors.slice(0, 3).join(', ')} +${props.story.authors.length - 3} more`
  })

  const categoryLabel = computed(() => {
    if (!props.story.categories || props.story.categories.length === 0) return null
    return props.story.categories[0]
  })
</script>

<template>
  <article
    class="card group hover-lift focus-within:shadow-[var(--shadow-glow)] overflow-hidden"
    :class="[
      accentClass,
      'animate-fade-in-up',
      `stagger-${Math.min(rank ?? 1, 5)}`,
      compact ? 'p-4' : 'p-5',
    ]"
    :data-testid="`story-card-${story.story_id}`"
  >
    <div class="flex items-start gap-4">
      <!-- Rank badge -->
      <div
        v-if="rank"
        class="flex-shrink-0 w-9 h-9 flex items-center justify-center rounded-full bg-[var(--color-accent-top5)]/15 text-[var(--color-accent-top5)] font-bold text-sm ring-2 ring-[var(--color-accent-top5)]/20 transition-all duration-[var(--duration-base)] ease-[var(--ease-out)] group-hover:ring-[var(--color-accent-top5)]/50 group-hover:scale-110 group-hover:bg-[var(--color-accent-top5)]/25"
        :data-testid="`story-rank-${rank}`"
      >
        {{ rank }}
      </div>

      <div class="flex-1 min-w-0">
        <!-- Header: Category & Source -->
        <div
          v-if="(showCategories && categoryLabel) || story.source_name"
          class="flex flex-wrap items-center gap-2 mb-2"
        >
          <span
            v-if="showCategories && categoryLabel"
            class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-[var(--color-primary-50)] text-[var(--color-primary-600)] border border-[var(--color-primary-100)]"
          >
            {{ categoryLabel }}
          </span>
          <span
            v-if="story.source_name"
            class="text-xs text-[var(--color-text-muted)]"
          >
            {{ story.source_name }}
          </span>
        </div>

        <!-- Title -->
        <h3
          class="font-semibold leading-snug"
          :class="compact ? 'text-sm' : 'text-base'"
        >
          <a
            :href="story.primary_link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-start gap-1.5 text-[var(--color-text-primary)] hover:text-[var(--color-primary-600)] transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] focus-visible:outline-offset-2 rounded group/link active:scale-[0.99]"
            :data-testid="`story-link-${story.story_id}`"
          >
            <span class="line-clamp-2">{{ story.title }}</span>
            <IconExternalLink
              :size="14"
              class="flex-shrink-0 mt-1 opacity-0 -translate-x-1 group-hover/link:opacity-100 group-hover/link:translate-x-0 transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] text-[var(--color-text-muted)]"
            />
          </a>
        </h3>

        <!-- Authors -->
        <p
          v-if="showAuthors && displayAuthors"
          class="mt-1.5 text-sm text-[var(--color-text-secondary)] line-clamp-1"
        >
          {{ displayAuthors }}
        </p>

        <!-- Summary/Abstract -->
        <p
          v-if="showSummary && truncatedSummary"
          class="mt-2 text-sm text-[var(--color-text-muted)] leading-relaxed line-clamp-3"
        >
          {{ truncatedSummary }}
        </p>

        <!-- Meta info -->
        <div
          class="flex flex-wrap items-center gap-x-3 gap-y-1.5 mt-3 text-xs text-[var(--color-text-muted)]"
        >
          <!-- Time -->
          <span
            class="inline-flex items-center gap-1 tabular-nums"
            :title="formatDate(story.published_at)"
          >
            <svg
              class="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            {{ formatRelativeTime(story.published_at) }}
          </span>

          <!-- Entity badges -->
          <template v-if="showEntities && story.entities.length > 0">
            <span class="text-[var(--color-border-strong)]">·</span>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="entity in story.entities"
                :key="entity"
                class="px-1.5 py-0.5 rounded bg-[var(--color-surface-tertiary)] text-[var(--color-text-secondary)] font-medium transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] hover:bg-[var(--color-primary-50)] hover:text-[var(--color-primary-600)] cursor-default"
              >
                {{ entity }}
              </span>
            </div>
          </template>

          <!-- arXiv ID -->
          <template v-if="showArxiv && story.arxiv_id">
            <span class="text-[var(--color-border-strong)]">·</span>
            <span class="font-mono bg-[var(--color-surface-tertiary)] px-1.5 py-0.5 rounded">
              arXiv:{{ story.arxiv_id }}
            </span>
          </template>
        </div>

        <!-- Additional links -->
        <div
          v-if="story.links.length > 1"
          class="flex flex-wrap gap-2 mt-3 pt-3 border-t border-[var(--color-border-light)]"
        >
          <a
            v-for="link in story.links"
            :key="link.url"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 px-2 py-1 text-xs font-medium text-[var(--color-text-secondary)] bg-[var(--color-surface-tertiary)] rounded-md hover:bg-[var(--color-primary-50)] hover:text-[var(--color-primary-600)] hover:shadow-[var(--shadow-xs)] transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] active:scale-[0.97]"
            :title="link.title"
          >
            <IconGithub
              v-if="link.link_type === 'github'"
              :size="12"
            />
            <IconDocument
              v-else
              :size="12"
            />
            <span>{{ getLinkTypeLabel(link.link_type) }}</span>
          </a>
        </div>
      </div>
    </div>
  </article>
</template>
