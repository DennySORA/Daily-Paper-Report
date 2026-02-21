<script setup lang="ts">
import { computed, ref } from 'vue'
import { useDigestStore } from '@/stores/digest'
import StoryCard from '@/components/ui/StoryCard.vue'

const digestStore = useDigestStore()

// Selected category filter (null = show all)
const selectedCategory = ref<string | null>(null)

// Expanded state for each category
const expandedCategories = ref<Record<string, boolean>>({})

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

// Toggle category expansion
const toggleCategory = (category: string) => {
  expandedCategories.value[category] = !expandedCategories.value[category]
}

// Check if category is expanded (default to true for first 3)
const isCategoryExpanded = (category: string, index: number) => {
  if (expandedCategories.value[category] !== undefined) {
    return expandedCategories.value[category]
  }
  return index < 3 // First 3 categories expanded by default
}
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
          <span class="text-2xl">📚</span>
          Papers by Category
        </h2>
        <p class="text-sm text-[var(--color-text-tertiary)] mt-1">
          <span class="font-semibold text-[var(--color-text-secondary)]">{{ totalPapers }}</span> papers across
          <span class="font-semibold text-[var(--color-text-secondary)]">{{ sortedCategories.length }}</span> categories
        </p>
      </div>

      <!-- Category filter pills -->
      <div
        v-if="sortedCategories.length > 0"
        class="flex flex-wrap gap-1.5"
      >
        <button
          class="badge transition-all cursor-pointer"
          :class="selectedCategory === null ? 'badge-papers' : 'badge-muted hover:bg-[var(--color-surface-overlay)]'"
          @click="selectedCategory = null"
        >
          All
        </button>
        <button
          v-for="category in sortedCategories.slice(0, 6)"
          :key="category"
          class="badge transition-all cursor-pointer"
          :class="
            selectedCategory === category
              ? 'badge-papers'
              : 'badge-muted hover:bg-[var(--color-surface-overlay)]'
          "
          @click="selectedCategory = selectedCategory === category ? null : category"
        >
          {{ category }}
          <span class="text-[0.625rem] opacity-70 ml-0.5">
            {{ getCategoryInfo(category).stories.length }}
          </span>
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-if="sortedCategories.length === 0"
      class="empty-state animate-fade-in-scale"
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
      class="space-y-4"
    >
      <div
        v-for="(category, index) in displayedCategories"
        :key="category"
        class="category-group animate-fade-in-up"
        :class="[`delay-${Math.min(index + 1, 10)}`]"
      >
        <!-- Category header (clickable) -->
        <button
          class="category-header"
          @click="toggleCategory(category)"
        >
          <div class="flex items-center gap-3">
            <span class="category-badge badge-papers">
              {{ category }}
            </span>
            <span class="text-sm text-[var(--color-text-secondary)] font-medium">
              {{ getCategoryInfo(category).displayName }}
            </span>
          </div>
          <div class="flex items-center gap-3">
            <span class="category-count">
              {{ getCategoryInfo(category).stories.length }} papers
            </span>
            <svg
              class="category-chevron"
              :class="{ 'category-chevron--expanded': isCategoryExpanded(category, index) }"
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
          v-show="isCategoryExpanded(category, index)"
          class="category-content"
        >
          <!-- Top pick (featured) -->
          <div
            v-if="getCategoryInfo(category).topPick"
            class="mb-3"
          >
            <StoryCard
              :story="getCategoryInfo(category).topPick!"
              :featured="true"
              accent-type="papers"
              :show-categories="false"
              :show-source="true"
              :show-authors="true"
              :show-summary="true"
              :show-arxiv="true"
            />
          </div>

          <!-- Other papers in grid -->
          <div
            v-if="getCategoryInfo(category).stories.length > 1"
            class="category-grid"
          >
            <StoryCard
              v-for="(story, storyIndex) in getCategoryInfo(category).stories.slice(1, 5)"
              :key="story.story_id"
              :story="story"
              accent-type="papers"
              :show-categories="false"
              :show-source="true"
              :show-authors="true"
              :show-summary="false"
              :show-arxiv="true"
              :compact="true"
              class="animate-fade-in-up"
              :class="[`delay-${Math.min(storyIndex + 2, 10)}`]"
            />
          </div>

          <!-- Show more indicator -->
          <div
            v-if="getCategoryInfo(category).stories.length > 5"
            class="category-more"
          >
            <span class="category-more-text">
              +{{ getCategoryInfo(category).stories.length - 5 }} more papers in this category
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.category-group {
  background: var(--color-surface-primary);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: border-color var(--duration-fast) var(--ease-out);
}

.category-group:hover {
  border-color: var(--color-border-default);
}

.category-header {
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

.category-header:hover {
  background: var(--color-surface-overlay);
}

.category-header:active {
  background: var(--color-surface-sunken);
}

.category-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-radius: var(--radius-full);
}

.category-count {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-tertiary);
  padding: 0.25rem 0.75rem;
  background: var(--color-surface-base);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border-subtle);
}

.category-chevron {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-text-muted);
  transition: transform var(--duration-base) var(--ease-out);
}

.category-chevron--expanded {
  transform: rotate(180deg);
}

.category-content {
  padding: 1.25rem;
}

.category-grid {
  display: grid;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .category-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.category-more {
  display: flex;
  justify-content: center;
  padding: 1rem 0 0.5rem;
}

.category-more-text {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  padding: 0.375rem 0.875rem;
  background: var(--color-surface-secondary);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border-subtle);
  transition: all var(--duration-fast) var(--ease-out);
}

.category-more-text:hover {
  background: var(--color-surface-overlay);
  border-color: var(--color-border-default);
  color: var(--color-text-tertiary);
}
</style>
