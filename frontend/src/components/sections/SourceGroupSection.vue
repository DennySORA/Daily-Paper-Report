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
    iconClass: 'section-group-icon-arxiv',
    sources: digestStore.allStoriesBySourceCategory.arxiv,
  },
  {
    id: 'huggingface',
    label: 'HuggingFace Models',
    icon: '🤗',
    iconClass: 'section-group-icon-hf',
    sources: digestStore.allStoriesBySourceCategory.huggingface,
  },
  {
    id: 'blog',
    label: 'Research Blogs',
    icon: '📝',
    iconClass: 'section-group-icon-blog',
    sources: digestStore.allStoriesBySourceCategory.blog,
  },
  {
    id: 'other',
    label: 'Other Sources',
    icon: '🔗',
    iconClass: 'section-group-icon-other',
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

// Get accent type for source
const getAccentType = (
  categoryId: string,
): 'highlight' | 'papers' | 'models' | 'sources' | 'radar' => {
  switch (categoryId) {
    case 'arxiv':
      return 'papers'
    case 'huggingface':
      return 'models'
    case 'blog':
      return 'radar'
    default:
      return 'sources'
  }
}
</script>

<template>
  <div class="space-y-4">
    <!-- Section header -->
    <div class="flex items-center justify-between">
      <div>
        <h2
          class="text-lg font-bold text-[var(--color-text-primary)]"
          style="font-family: var(--font-display)"
        >
          Browse by Source
        </h2>
        <p class="text-sm text-[var(--color-text-tertiary)] mt-0.5">
          Explore content organized by data source
        </p>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-if="nonEmptyCategories.length === 0"
      class="empty-state"
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
        class="section-group animate-fade-up"
        :class="[`delay-${index + 1}`]"
      >
        <!-- Category header -->
        <div
          class="section-group-header"
          @click="toggleCategory(category.id)"
        >
          <div class="section-group-title">
            <span
              class="section-group-icon"
              :class="category.iconClass"
            >
              {{ category.icon }}
            </span>
            <span>{{ category.label }}</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="section-group-count">
              {{ getCategoryCount(category.sources) }} items
            </span>
            <svg
              class="w-4 h-4 text-[var(--color-text-tertiary)] transition-transform duration-[var(--duration-fast)]"
              :class="{ 'rotate-180': expandedCategories[category.id] }"
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
        </div>

        <!-- Category content -->
        <div
          v-show="expandedCategories[category.id]"
          class="section-group-content"
        >
          <!-- Source sub-groups -->
          <div class="space-y-4">
            <div
              v-for="source in category.sources"
              :key="source.sourceId"
            >
              <!-- Source header -->
              <div class="flex items-center justify-between mb-2 px-1">
                <h4 class="text-sm font-semibold text-[var(--color-text-secondary)]">
                  {{ source.name }}
                </h4>
                <span class="text-xs text-[var(--color-text-quaternary)]">
                  {{ source.stories.length }} items
                </span>
              </div>

              <!-- Source stories -->
              <div class="section-group-grid">
                <!-- Top pick (first item) -->
                <StoryCard
                  v-if="source.stories[0]"
                  :story="source.stories[0]"
                  :featured="true"
                  :accent-type="getAccentType(category.id)"
                  :show-categories="true"
                  :show-source="false"
                  :show-authors="true"
                  :show-summary="true"
                />

                <!-- Rest of stories (compact) -->
                <StoryCard
                  v-for="story in source.stories.slice(1, 4)"
                  :key="story.story_id"
                  :story="story"
                  :accent-type="getAccentType(category.id)"
                  :show-categories="true"
                  :show-source="false"
                  :show-authors="false"
                  :show-summary="false"
                  :compact="true"
                />

                <!-- Show more indicator -->
                <div
                  v-if="source.stories.length > 4"
                  class="text-center py-2"
                >
                  <span class="text-xs text-[var(--color-text-quaternary)]">
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
