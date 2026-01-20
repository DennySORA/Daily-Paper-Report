<script setup lang="ts">
  import { computed, ref } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import StoryCard from '@/components/ui/StoryCard.vue'
  import EmptyState from '@/components/ui/EmptyState.vue'

  const digestStore = useDigestStore()
  const stories = computed(() => digestStore.papers)
  const papersByCategory = computed(() => digestStore.papersByCategory)
  const categories = computed(() => digestStore.paperCategories)

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

  const getCategoryDisplayName = (category: string): string => {
    const categoryNames: Record<string, string> = {
      'cs.AI': 'Artificial Intelligence',
      'cs.CL': 'Computation & Language',
      'cs.CV': 'Computer Vision',
      'cs.LG': 'Machine Learning',
      'cs.NE': 'Neural & Evolutionary',
      'cs.RO': 'Robotics',
      'stat.ML': 'Statistical ML',
      Uncategorized: 'Other',
    }
    return categoryNames[category] ?? category
  }
</script>

<template>
  <div data-testid="section-papers">
    <!-- Section description -->
    <p class="text-sm text-[var(--color-text-muted)] mb-4">
      Latest research papers from arXiv and academic sources, covering machine learning, NLP,
      computer vision, and AI safety.
    </p>

    <!-- View Controls -->
    <div
      v-if="stories.length > 0"
      class="flex flex-wrap items-center gap-3 mb-4"
    >
      <!-- View Mode Toggle -->
      <div
        class="inline-flex rounded-lg bg-[var(--color-surface-secondary)] p-1 border border-[var(--color-border-light)]"
      >
        <button
          class="px-3 py-1.5 text-xs font-semibold rounded-md transition-all"
          :class="
            viewMode === 'by-category'
              ? 'bg-[var(--color-surface-elevated)] text-[var(--color-text-primary)] shadow-sm'
              : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'
          "
          @click="viewMode = 'by-category'"
        >
          By Category
        </button>
        <button
          class="px-3 py-1.5 text-xs font-semibold rounded-md transition-all"
          :class="
            viewMode === 'all'
              ? 'bg-[var(--color-surface-elevated)] text-[var(--color-text-primary)] shadow-sm'
              : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'
          "
          @click="viewMode = 'all'; selectedCategory = null"
        >
          All Papers
        </button>
      </div>

      <!-- Category Filter Pills (when in by-category mode) -->
      <div
        v-if="viewMode === 'by-category' && categories.length > 1"
        class="flex flex-wrap gap-2"
      >
        <button
          class="px-2.5 py-1 text-xs font-medium rounded-full transition-all border"
          :class="
            selectedCategory === null
              ? 'bg-[var(--color-accent-papers)] text-white border-[var(--color-accent-papers)]'
              : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border-[var(--color-border-default)] hover:border-[var(--color-accent-papers)] hover:text-[var(--color-accent-papers)]'
          "
          @click="selectedCategory = null"
        >
          All ({{ stories.length }})
        </button>
        <button
          v-for="category in categories"
          :key="category"
          class="px-2.5 py-1 text-xs font-medium rounded-full transition-all border"
          :class="
            selectedCategory === category
              ? 'bg-[var(--color-accent-papers)] text-white border-[var(--color-accent-papers)]'
              : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border-[var(--color-border-default)] hover:border-[var(--color-accent-papers)] hover:text-[var(--color-accent-papers)]'
          "
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
        v-for="category in categories"
        :key="category"
        class="animate-fade-in-up"
      >
        <h3
          class="flex items-center gap-2 text-sm font-semibold text-[var(--color-text-secondary)] mb-3 pb-2 border-b border-[var(--color-border-light)]"
          style="font-family: var(--font-display)"
        >
          <span class="w-2 h-2 rounded-full bg-[var(--color-accent-papers)]" />
          {{ getCategoryDisplayName(category) }}
          <span class="text-[var(--color-text-muted)] font-normal">
            ({{ papersByCategory[category]?.length ?? 0 }})
          </span>
        </h3>
        <div class="space-y-3">
          <StoryCard
            v-for="story in papersByCategory[category]"
            :key="story.story_id"
            :story="story"
            :show-arxiv="true"
            :show-categories="false"
            :show-summary="true"
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
        v-for="story in filteredStories"
        :key="story.story_id"
        :story="story"
        :show-arxiv="true"
        :show-summary="true"
        accent-class="accent-papers"
      />
    </div>

    <EmptyState
      v-else
      title="No new papers today"
      description="Check back tomorrow!"
    />
  </div>
</template>
