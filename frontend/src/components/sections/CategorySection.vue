<script setup lang="ts">
import { computed, ref } from 'vue'
import { useDigestStore } from '@/stores/digest'
import StoryCard from '@/components/ui/StoryCard.vue'

const digestStore = useDigestStore()

// Selected category filter (null = show all)
const selectedCategory = ref<string | null>(null)

// Get papers grouped by category
const papersByCategory = computed(() => digestStore.papersByCategoryWithPicks)
const sortedCategories = computed(() => digestStore.sortedCategories)

// Filtered categories based on selection
const displayedCategories = computed(() => {
  if (!selectedCategory.value) return sortedCategories.value
  return sortedCategories.value.filter((cat) => cat === selectedCategory.value)
})

// Get category info
const getCategoryInfo = (category: string) => papersByCategory.value[category]

// Total papers count
const totalPapers = computed(() =>
  Object.values(papersByCategory.value).reduce((sum, cat) => sum + cat.stories.length, 0),
)
</script>

<template>
  <div class="space-y-4">
    <!-- Section header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2
          class="text-lg font-bold text-[var(--color-text-primary)]"
          style="font-family: var(--font-display)"
        >
          Papers by Category
        </h2>
        <p class="text-sm text-[var(--color-text-tertiary)] mt-0.5">
          {{ totalPapers }} papers across {{ sortedCategories.length }} categories
        </p>
      </div>

      <!-- Category filter pills -->
      <div
        v-if="sortedCategories.length > 0"
        class="flex flex-wrap gap-1.5"
      >
        <button
          class="badge transition-all"
          :class="selectedCategory === null ? 'badge-papers' : 'badge-muted hover:bg-[var(--color-surface-overlay)]'"
          @click="selectedCategory = null"
        >
          All
        </button>
        <button
          v-for="category in sortedCategories.slice(0, 6)"
          :key="category"
          class="badge transition-all"
          :class="
            selectedCategory === category
              ? 'badge-papers'
              : 'badge-muted hover:bg-[var(--color-surface-overlay)]'
          "
          @click="selectedCategory = selectedCategory === category ? null : category"
        >
          {{ category }}
          <span class="text-[0.625rem] opacity-70">
            ({{ getCategoryInfo(category).stories.length }})
          </span>
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-if="sortedCategories.length === 0"
      class="empty-state"
    >
      <div class="empty-state-icon">
        📄
      </div>
      <h3 class="empty-state-title">
        No papers available
      </h3>
      <p class="empty-state-desc">
        No papers found for the selected time range. Try expanding the time filter.
      </p>
    </div>

    <!-- Category groups -->
    <div
      v-else
      class="space-y-6"
    >
      <div
        v-for="(category, index) in displayedCategories"
        :key="category"
        class="animate-fade-up"
        :class="[`delay-${Math.min(index + 1, 10)}`]"
      >
        <!-- Category header -->
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="badge badge-category badge-papers">
              {{ category }}
            </span>
            <span class="text-sm text-[var(--color-text-secondary)]">
              {{ getCategoryInfo(category).displayName }}
            </span>
          </div>
          <span class="text-xs text-[var(--color-text-quaternary)]">
            {{ getCategoryInfo(category).stories.length }} papers
          </span>
        </div>

        <!-- Papers grid -->
        <div class="space-y-3">
          <!-- Top pick (featured) -->
          <StoryCard
            v-if="getCategoryInfo(category).topPick"
            :story="getCategoryInfo(category).topPick!"
            :featured="true"
            accent-type="papers"
            :show-categories="false"
            :show-source="true"
            :show-authors="true"
            :show-summary="true"
            :show-arxiv="true"
          />

          <!-- Other papers -->
          <div
            v-if="getCategoryInfo(category).stories.length > 1"
            class="grid gap-2 sm:grid-cols-2"
          >
            <StoryCard
              v-for="story in getCategoryInfo(category).stories.slice(1, 5)"
              :key="story.story_id"
              :story="story"
              accent-type="papers"
              :show-categories="false"
              :show-source="true"
              :show-authors="true"
              :show-summary="false"
              :show-arxiv="true"
              :compact="true"
            />
          </div>

          <!-- Show more indicator -->
          <div
            v-if="getCategoryInfo(category).stories.length > 5"
            class="text-center py-2"
          >
            <span class="text-xs text-[var(--color-text-quaternary)]">
              +{{ getCategoryInfo(category).stories.length - 5 }} more papers in this category
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
