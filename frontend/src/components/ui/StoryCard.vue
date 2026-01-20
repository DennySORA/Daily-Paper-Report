<script setup lang="ts">
  import type { Story } from '@/types/digest'

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

  const getLinkIcon = (linkType: string): string => {
    const icons: Record<string, string> = {
      blog: '📝',
      paper: '📄',
      model: '🤖',
      github: '💻',
      arxiv: '📚',
      hf: '🤗',
    }
    return icons[linkType] ?? '🔗'
  }
</script>

<template>
  <article
    class="card p-5 group"
    :class="[accentClass, 'animate-fade-in-up', `stagger-${Math.min(rank ?? 1, 5)}`]"
    :data-testid="`story-card-${story.story_id}`"
  >
    <div class="flex items-start gap-4">
      <!-- Rank badge -->
      <div
        v-if="rank"
        class="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-[var(--color-accent-top5)]/10 text-[var(--color-accent-top5)] font-semibold text-sm"
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
            class="hover:text-[var(--color-primary-600)] transition-colors duration-[var(--duration-fast)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] focus-visible:outline-offset-2 rounded"
            :data-testid="`story-link-${story.story_id}`"
          >
            {{ story.title }}
          </a>
        </h3>

        <!-- Meta info -->
        <div class="flex flex-wrap items-center gap-2 mt-2 text-sm text-[var(--color-text-muted)]">
          <span>{{ formatDate(story.published_at) }}</span>

          <template v-if="showEntities && story.entities.length > 0">
            <span class="text-[var(--color-border-strong)]">·</span>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="entity in story.entities"
                :key="entity"
                class="px-2 py-0.5 rounded-full bg-[var(--color-surface-tertiary)] text-xs font-medium"
              >
                {{ entity }}
              </span>
            </div>
          </template>

          <template v-if="showArxiv && story.arxiv_id">
            <span class="text-[var(--color-border-strong)]">·</span>
            <span class="font-mono text-xs">arXiv:{{ story.arxiv_id }}</span>
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
            class="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-[var(--color-text-secondary)] bg-[var(--color-surface-tertiary)] rounded-md hover:bg-[var(--color-surface-secondary)] hover:text-[var(--color-text-primary)] transition-all duration-[var(--duration-fast)]"
            :title="link.title"
          >
            <span>{{ getLinkIcon(link.link_type) }}</span>
            <span>{{ link.link_type }}</span>
          </a>
        </div>
      </div>
    </div>
  </article>
</template>
