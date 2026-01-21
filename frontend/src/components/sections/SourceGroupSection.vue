<script setup lang="ts">
import { computed, ref } from 'vue'
import { useDigestStore } from '@/stores/digest'
import StoryCard from '@/components/ui/StoryCard.vue'

const digestStore = useDigestStore()

// Expanded states for each source category
const expandedCategories = ref<Record<string, boolean>>({
  arxiv: true,
  huggingface: true,
  blog: true,
  other: true,
})

// Toggle category expansion
const toggleCategory = (category: string) => {
  expandedCategories.value[category] = !expandedCategories.value[category]
}

// Source category configuration
const sourceCategories = computed(() => [
  {
    id: 'arxiv',
    label: 'arXiv Papers',
    icon: '📄',
    description: 'Latest research papers from arXiv',
    accentType: 'papers' as const,
    sources: digestStore.allStoriesBySourceCategory.arxiv,
  },
  {
    id: 'huggingface',
    label: 'HuggingFace',
    icon: '🤗',
    description: 'Models, datasets, and daily papers',
    accentType: 'models' as const,
    sources: digestStore.allStoriesBySourceCategory.huggingface,
  },
  {
    id: 'blog',
    label: 'Research Blogs',
    icon: '📝',
    description: 'Updates from AI research labs',
    accentType: 'radar' as const,
    sources: digestStore.allStoriesBySourceCategory.blog,
  },
  {
    id: 'other',
    label: 'Other Sources',
    icon: '🔗',
    description: 'Additional AI/ML resources',
    accentType: 'sources' as const,
    sources: digestStore.allStoriesBySourceCategory.other,
  },
])

// Filter out empty categories
const nonEmptyCategories = computed(() =>
  sourceCategories.value.filter((cat) => cat.sources.length > 0),
)

// Get total story count for a category
const getCategoryCount = (sources: { stories: unknown[] }[]): number => {
  return sources.reduce((sum, source) => sum + source.stories.length, 0)
}

// Total stories across all sources
const totalStories = computed(() =>
  nonEmptyCategories.value.reduce((sum, cat) => sum + getCategoryCount(cat.sources), 0),
)
</script>

<template>
  <div class="space-y-5">
    <!-- Section header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between animate-fade-in-up">
      <div>
        <h2
          class="text-xl font-bold text-[var(--color-text-primary)] flex items-center gap-2"
          style="font-family: var(--font-display)"
        >
          <span class="text-2xl">🗂️</span>
          Browse by Source
        </h2>
        <p class="text-sm text-[var(--color-text-tertiary)] mt-1">
          <span class="font-semibold text-[var(--color-text-secondary)]">{{ totalStories }}</span> items from
          <span class="font-semibold text-[var(--color-text-secondary)]">{{ nonEmptyCategories.length }}</span> source types
        </p>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-if="nonEmptyCategories.length === 0"
      class="empty-state animate-fade-in-scale"
    >
      <div class="empty-state-icon">
        📭
      </div>
      <h3 class="empty-state-title">
        No items found
      </h3>
      <p class="empty-state-desc">
        No content available for the selected time range. Try expanding the time filter.
      </p>
    </div>

    <!-- Source category groups -->
    <div
      v-else
      class="space-y-4"
    >
      <div
        v-for="(category, index) in nonEmptyCategories"
        :key="category.id"
        class="source-category animate-fade-in-up"
        :class="[`delay-${Math.min(index + 1, 10)}`]"
      >
        <!-- Category header -->
        <button
          class="source-category-header"
          @click="toggleCategory(category.id)"
        >
          <div class="flex items-center gap-3">
            <span class="source-category-icon">
              {{ category.icon }}
            </span>
            <div class="text-left">
              <span class="source-category-title">{{ category.label }}</span>
              <span class="source-category-desc">{{ category.description }}</span>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="source-category-count">
              {{ getCategoryCount(category.sources) }} items
            </span>
            <svg
              class="source-category-chevron"
              :class="{ 'source-category-chevron--expanded': expandedCategories[category.id] }"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </button>

        <!-- Category content -->
        <div
          v-show="expandedCategories[category.id]"
          class="source-category-content"
        >
          <!-- Source sub-groups -->
          <div class="space-y-5">
            <div
              v-for="(source, sourceIndex) in category.sources"
              :key="source.sourceId"
              class="source-group animate-fade-in-up"
              :class="[`delay-${Math.min(sourceIndex + 1, 5)}`]"
            >
              <!-- Source header -->
              <div class="source-header">
                <h4 class="source-name">
                  {{ source.name }}
                </h4>
                <span class="source-count">
                  {{ source.stories.length }} items
                </span>
              </div>

              <!-- Source stories -->
              <div class="source-stories">
                <!-- Top pick (first item) - featured -->
                <StoryCard
                  v-if="source.stories[0]"
                  :story="source.stories[0]"
                  :featured="true"
                  :accent-type="category.accentType"
                  :show-categories="true"
                  :show-source="false"
                  :show-authors="true"
                  :show-summary="true"
                  class="source-story-featured"
                />

                <!-- Rest of stories (compact grid) -->
                <div
                  v-if="source.stories.length > 1"
                  class="source-stories-grid"
                >
                  <StoryCard
                    v-for="story in source.stories.slice(1, 4)"
                    :key="story.story_id"
                    :story="story"
                    :accent-type="category.accentType"
                    :show-categories="true"
                    :show-source="false"
                    :show-authors="false"
                    :show-summary="false"
                    :compact="true"
                  />
                </div>

                <!-- Show more indicator -->
                <div
                  v-if="source.stories.length > 4"
                  class="source-more"
                >
                  <span class="source-more-text">
                    +{{ source.stories.length - 4 }} more items
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.source-category {
  background: var(--color-surface-primary);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: border-color var(--duration-fast) var(--ease-out);
}

.source-category:hover {
  border-color: var(--color-border-default);
}

.source-category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 1rem 1.25rem;
  background: var(--color-surface-secondary);
  border: none;
  border-bottom: 1px solid var(--color-border-subtle);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
  text-align: left;
}

.source-category-header:hover {
  background: var(--color-surface-overlay);
}

.source-category-header:active {
  background: var(--color-surface-sunken);
}

.source-category-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  font-size: 1.25rem;
  background: var(--color-surface-overlay);
  border-radius: var(--radius-lg);
  transition: transform var(--duration-fast) var(--ease-spring);
}

.source-category-header:hover .source-category-icon {
  transform: scale(1.05);
}

.source-category-title {
  display: block;
  font-family: var(--font-display);
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.source-category-desc {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-top: 0.125rem;
}

.source-category-count {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-tertiary);
  padding: 0.25rem 0.75rem;
  background: var(--color-surface-base);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border-subtle);
}

.source-category-chevron {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-text-muted);
  transition: transform var(--duration-base) var(--ease-out);
}

.source-category-chevron--expanded {
  transform: rotate(180deg);
}

.source-category-content {
  padding: 1.25rem;
}

/* Individual source group */
.source-group {
  padding: 1rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  transition: all var(--duration-fast) var(--ease-out);
}

.source-group:hover {
  border-color: var(--color-border-default);
  background: var(--color-surface-overlay);
}

.source-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.875rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

.source-name {
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.source-count {
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-text-muted);
  padding: 0.1875rem 0.5rem;
  background: var(--color-surface-base);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border-subtle);
}

.source-stories {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.source-story-featured {
  margin-bottom: 0.25rem;
}

.source-stories-grid {
  display: grid;
  gap: 0.625rem;
}

@media (min-width: 640px) {
  .source-stories-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .source-stories-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.source-more {
  display: flex;
  justify-content: center;
  padding-top: 0.75rem;
}

.source-more-text {
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--color-text-muted);
  padding: 0.3125rem 0.75rem;
  background: var(--color-surface-base);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border-subtle);
  transition: all var(--duration-fast) var(--ease-out);
}

.source-more-text:hover {
  background: var(--color-surface-overlay);
  border-color: var(--color-border-default);
  color: var(--color-text-tertiary);
}
</style>
