<script setup lang="ts">
  import type { Story } from '@/types/digest'
  import { IconExternalLink, IconGithub, IconDocument } from '@/components/icons'

  interface Props {
    story: Story
    rank?: number
    showEntities?: boolean
    showArxiv?: boolean
    accentClass?: string
  }

  withDefaults(defineProps<Props>(), {
    rank: undefined,
    showEntities: false,
    showArxiv: false,
    accentClass: '',
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

  const getLinkTypeLabel = (linkType: string): string => {
    const labels: Record<string, string> = {
      blog: 'Blog',
      paper: 'Paper',
      model: 'Model',
      github: 'GitHub',
      arxiv: 'arXiv',
      hf: 'HuggingFace',
    }
    return labels[linkType] ?? linkType
  }
</script>

<template>
  <article
    class="card p-5 group hover-lift focus-within:shadow-[var(--shadow-glow)]"
    :class="[accentClass, 'animate-fade-in-up', `stagger-${Math.min(rank ?? 1, 5)}`]"
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
        <!-- Title -->
        <h3 class="font-medium text-[var(--color-text-primary)] leading-snug">
          <a
            :href="story.primary_link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 hover:text-[var(--color-primary-600)] transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] focus-visible:outline-offset-2 rounded group/link active:scale-[0.99]"
            :data-testid="`story-link-${story.story_id}`"
          >
            <span>{{ story.title }}</span>
            <IconExternalLink
              :size="14"
              class="opacity-0 -translate-x-1 group-hover/link:opacity-100 group-hover/link:translate-x-0 transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] text-[var(--color-text-muted)]"
            />
          </a>
        </h3>

        <!-- Meta info -->
        <div class="flex flex-wrap items-center gap-2 mt-2 text-sm text-[var(--color-text-muted)]">
          <span class="tabular-nums">{{ formatDate(story.published_at) }}</span>

          <template v-if="showEntities && story.entities.length > 0">
            <span class="text-[var(--color-border-strong)]">·</span>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="entity in story.entities"
                :key="entity"
                class="px-2 py-0.5 rounded-md bg-[var(--color-surface-tertiary)] text-xs font-medium text-[var(--color-text-secondary)] transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] hover:bg-[var(--color-primary-50)] hover:text-[var(--color-primary-600)] cursor-default"
              >
                {{ entity }}
              </span>
            </div>
          </template>

          <template v-if="showArxiv && story.arxiv_id">
            <span class="text-[var(--color-border-strong)]">·</span>
            <span
              class="font-mono text-xs bg-[var(--color-surface-tertiary)] px-1.5 py-0.5 rounded"
            >
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
            class="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--color-text-secondary)] bg-[var(--color-surface-tertiary)] rounded-lg hover:bg-[var(--color-primary-50)] hover:text-[var(--color-primary-600)] hover:shadow-[var(--shadow-sm)] transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] active:scale-[0.97]"
            :title="link.title"
          >
            <IconGithub v-if="link.link_type === 'github'" :size="14" />
            <IconDocument v-else :size="14" />
            <span>{{ getLinkTypeLabel(link.link_type) }}</span>
          </a>
        </div>
      </div>
    </div>
  </article>
</template>
