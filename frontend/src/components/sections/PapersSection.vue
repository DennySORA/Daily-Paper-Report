<script setup lang="ts">
  import { computed, ref } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import StoryCard from '@/components/ui/StoryCard.vue'
  import EmptyState from '@/components/ui/EmptyState.vue'
  import { IconDocument } from '@/components/icons'

  const digestStore = useDigestStore()
  const stories = computed(() => digestStore.filteredPapers)
  const papersByCategory = computed(() => digestStore.filteredPapersByCategory)
  const categories = computed(() => digestStore.filteredPaperCategories)

  // View mode: 'all' or 'by-category'
  const viewMode = ref<'all' | 'by-category'>('by-category')

  // Selected category for filter (null = show all)
  const selectedCategory = ref<string | null>(null)

  const filteredStories = computed(() => {
    if (viewMode.value === 'all' || !selectedCategory.value) {
      return stories.value
    }
    return papersByCategory.value[selectedCategory.value] ?? []
  })

  // Category display names and descriptions
  const categoryInfo: Record<string, { name: string; color: string }> = {
    'cs.AI': { name: 'Artificial Intelligence', color: 'oklch(0.65 0.18 285)' },
    'cs.CL': { name: 'Computation & Language', color: 'oklch(0.68 0.16 220)' },
    'cs.CV': { name: 'Computer Vision', color: 'oklch(0.7 0.15 145)' },
    'cs.LG': { name: 'Machine Learning', color: 'oklch(0.72 0.16 45)' },
    'cs.NE': { name: 'Neural & Evolutionary', color: 'oklch(0.65 0.14 320)' },
    'cs.RO': { name: 'Robotics', color: 'oklch(0.68 0.15 175)' },
    'stat.ML': { name: 'Statistical ML', color: 'oklch(0.7 0.14 100)' },
    Uncategorized: { name: 'Other Research', color: 'oklch(0.6 0.1 265)' },
  }

  const getCategoryDisplayName = (category: string): string => {
    return categoryInfo[category]?.name ?? category
  }

  const getCategoryColor = (category: string): string => {
    return categoryInfo[category]?.color ?? 'var(--color-accent-papers)'
  }

  // Sort categories by paper count
  const sortedCategories = computed(() =>
    [...categories.value].sort(
      (a, b) => (papersByCategory.value[b]?.length ?? 0) - (papersByCategory.value[a]?.length ?? 0),
    ),
  )
</script>

<template>
  <div data-testid="section-papers">
    <!-- Section description -->
    <p class="text-sm text-[var(--color-text-muted)] mb-5">
      Latest research papers from arXiv and academic sources, covering machine learning, NLP,
      computer vision, and AI safety.
    </p>

    <!-- View Controls -->
    <div
      v-if="stories.length > 0"
      class="flex flex-wrap items-center gap-3 mb-5"
    >
      <!-- View Mode Toggle -->
      <div class="filter-toggle">
        <button
          class="filter-toggle-btn"
          :class="{ active: viewMode === 'by-category' }"
          @click="viewMode = 'by-category'"
        >
          By Category
        </button>
        <button
          class="filter-toggle-btn"
          :class="{ active: viewMode === 'all' }"
          @click="viewMode = 'all'; selectedCategory = null"
        >
          All Papers
        </button>
      </div>

      <!-- Category Filter Pills (when in by-category mode) -->
      <div
        v-if="viewMode === 'by-category' && sortedCategories.length > 1"
        class="flex flex-wrap gap-2"
      >
        <button
          class="badge badge-default press-effect"
          :class="{
            '!bg-[var(--color-accent-papers)] !text-white': selectedCategory === null,
          }"
          @click="selectedCategory = null"
        >
          All ({{ stories.length }})
        </button>
        <button
          v-for="category in sortedCategories"
          :key="category"
          class="badge badge-default press-effect"
          :class="{
            '!bg-[var(--color-accent-papers)] !text-white': selectedCategory === category,
          }"
          @click="selectedCategory = category"
        >
          {{ getCategoryDisplayName(category) }} ({{ papersByCategory[category]?.length ?? 0 }})
        </button>
      </div>
    </div>

    <!-- Papers List - Grouped by Category -->
    <div
      v-if="stories.length > 0 && viewMode === 'by-category' && selectedCategory === null"
      class="space-y-6"
    >
      <div
        v-for="(category, index) in sortedCategories"
        :key="category"
        class="source-group animate-fade-in-up"
        :class="`stagger-${Math.min(index + 1, 5)}`"
      >
        <!-- Category Header -->
        <div class="source-group-header">
          <div
            class="source-group-icon"
            :style="{ color: getCategoryColor(category) }"
          >
            <IconDocument :size="20" />
          </div>
          <div class="flex-1 min-w-0">
            <h3
              class="font-semibold text-[var(--color-text-primary)] truncate"
              style="font-family: var(--font-display)"
            >
              {{ getCategoryDisplayName(category) }}
            </h3>
            <p class="text-xs text-[var(--color-text-muted)]">
              {{ papersByCategory[category]?.length ?? 0 }} paper{{
                (papersByCategory[category]?.length ?? 0) !== 1 ? 's' : ''
              }}
              <span
                v-if="category !== 'Uncategorized'"
                class="ml-1.5 font-mono opacity-60"
              >
                ({{ category }})
              </span>
            </p>
          </div>
        </div>

        <!-- Category Papers -->
        <div class="source-group-content space-y-3">
          <StoryCard
            v-for="story in papersByCategory[category]"
            :key="story.story_id"
            :story="story"
            :show-arxiv="true"
            :show-categories="false"
            :show-summary="true"
            :show-authors="true"
            accent-class="accent-papers"
          />
        </div>
      </div>
    </div>

    <!-- Papers List - Flat or Filtered -->
    <div
      v-else-if="stories.length > 0"
      class="space-y-3"
    >
      <StoryCard
        v-for="(story, index) in filteredStories"
        :key="story.story_id"
        :story="story"
        :show-arxiv="true"
        :show-summary="true"
        :show-authors="true"
        accent-class="accent-papers"
        :class="`stagger-${Math.min(index + 1, 8)}`"
      />
    </div>

    <EmptyState
      v-else
      title="No papers"
      description="No new research papers in this time period."
    />
  </div>
</template>
