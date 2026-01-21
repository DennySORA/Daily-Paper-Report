<script setup lang="ts">
import { computed, ref } from 'vue'
import { useDigestStore } from '@/stores/digest'
import StoryCard from '@/components/ui/StoryCard.vue'
import CategorySection from '@/components/sections/CategorySection.vue'
import SourceGroupSection from '@/components/sections/SourceGroupSection.vue'

const digestStore = useDigestStore()

const isLoading = computed(() => digestStore.isLoading)
const hasError = computed(() => digestStore.error !== null)
const errorMessage = computed(() => digestStore.error)
const runDate = computed(() => digestStore.runDate)
const runInfo = computed(() => digestStore.runInfo)
const timeFilter = computed(() => digestStore.timeFilter)

// Active view: 'overview' | 'categories' | 'sources'
const activeView = ref<'overview' | 'categories' | 'sources'>('overview')

// Time filter toggle handler
const setTimeFilter = (filter: 'all' | '24h') => {
  digestStore.setTimeFilter(filter)
}

// Format the last update time
const lastUpdated = computed(() => {
  if (!runInfo.value?.finished_at) return null
  const date = new Date(runInfo.value.finished_at)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
})

// Get top picks for overview
const topPicks = computed(() => digestStore.topPicksBySource.slice(0, 5))

// Total story count (using filtered data)
const totalStories = computed(() => digestStore.filteredTotalStories)

// View tabs configuration
const viewTabs = computed(() => [
  { id: 'overview', label: 'Overview', count: totalStories.value },
  { id: 'categories', label: 'By Category', count: Object.keys(digestStore.papersByCategoryWithPicks).length },
  { id: 'sources', label: 'By Source', count: Object.keys(digestStore.allStoriesBySource).length },
])

// Get source stats
const sourceStats = computed(() => {
  const stats = digestStore.sourcesByStatus
  return {
    healthy: stats.healthy.length,
    failed: stats.failed.length,
    total: stats.healthy.length + stats.failed.length + stats.noUpdate.length,
  }
})
</script>

<template>
  <div data-testid="home-page">
    <!-- Page Header -->
    <header class="mb-8 animate-fade-up">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1
            class="text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)] tracking-tight"
            style="font-family: var(--font-display)"
          >
            Daily Paper Report
          </h1>
          <p
            v-if="runDate"
            class="text-sm text-[var(--color-text-secondary)] mt-1.5"
          >
            {{ runDate }} ·
            <RouterLink
              :to="`/day/${runDate}`"
              class="link"
            >
              Permanent link
            </RouterLink>
          </p>
          <p
            v-else-if="isLoading"
            class="h-5 w-40 mt-1.5 skeleton"
          />
        </div>

        <!-- Stats and time filter -->
        <div
          v-if="!isLoading && !hasError"
          class="flex flex-wrap items-center gap-2"
        >
          <!-- Time Filter Toggle -->
          <div class="time-filter">
            <button
              class="time-filter-btn"
              :class="{ active: timeFilter === 'all' }"
              @click="setTimeFilter('all')"
            >
              All Time
            </button>
            <button
              class="time-filter-btn"
              :class="{ active: timeFilter === '24h' }"
              @click="setTimeFilter('24h')"
            >
              Last 24h
            </button>
          </div>

          <div class="stat-pill">
            <span class="stat-label">Stories</span>
            <span class="stat-value">{{ totalStories }}</span>
          </div>

          <div
            v-if="lastUpdated"
            class="stat-pill hide-mobile"
          >
            <span class="stat-label">Updated</span>
            <span class="stat-value">{{ lastUpdated }}</span>
          </div>

          <div
            v-if="sourceStats.healthy > 0"
            class="stat-pill hide-mobile"
          >
            <span class="stat-label">Sources</span>
            <span class="stat-value">
              {{ sourceStats.healthy }}/{{ sourceStats.total }}
              <span
                v-if="sourceStats.failed > 0"
                class="text-[var(--color-error)]"
              >
                ({{ sourceStats.failed }} failed)
              </span>
            </span>
          </div>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div
      v-if="isLoading"
      class="space-y-6"
      data-testid="loading-state"
    >
      <!-- Tab skeleton -->
      <div class="tab-bar">
        <div
          v-for="i in 3"
          :key="i"
          class="h-10 w-24 skeleton"
        />
      </div>

      <!-- Cards skeleton -->
      <div class="space-y-3">
        <div
          v-for="i in 5"
          :key="i"
          class="card p-5"
        >
          <div class="space-y-3">
            <div class="flex gap-2">
              <div class="h-5 w-16 skeleton" />
              <div class="h-5 w-20 skeleton" />
            </div>
            <div class="h-6 w-3/4 skeleton" />
            <div class="h-4 w-1/2 skeleton" />
            <div class="h-16 w-full skeleton" />
            <div class="flex gap-2">
              <div class="h-4 w-16 skeleton" />
              <div class="h-4 w-20 skeleton" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="hasError"
      class="card p-8 text-center animate-fade-in border-[var(--color-error)]"
      data-testid="error-state"
    >
      <div class="empty-state-icon text-[var(--color-error)]">
        ⚠️
      </div>
      <h3 class="empty-state-title text-[var(--color-error)]">
        Failed to load digest
      </h3>
      <p class="empty-state-desc">
        {{ errorMessage }}
      </p>
      <button
        class="btn btn-primary mt-4"
        data-testid="retry-button"
        @click="digestStore.fetchDigest()"
      >
        <svg
          class="w-4 h-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        Retry
      </button>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- View Navigation -->
      <div class="tab-bar mb-6 animate-fade-up delay-1">
        <button
          v-for="tab in viewTabs"
          :key="tab.id"
          class="tab-button"
          :class="{ active: activeView === tab.id }"
          @click="activeView = tab.id as typeof activeView"
        >
          <span>{{ tab.label }}</span>
          <span class="tab-badge">{{ tab.count }}</span>
        </button>
      </div>

      <!-- Overview View -->
      <div
        v-show="activeView === 'overview'"
        class="space-y-8 animate-fade-up delay-2"
      >
        <!-- Top Picks Section -->
        <section v-if="topPicks.length > 0">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2
                class="text-lg font-bold text-[var(--color-text-primary)]"
                style="font-family: var(--font-display)"
              >
                Top Picks
              </h2>
              <p class="text-sm text-[var(--color-text-tertiary)] mt-0.5">
                Most notable items from each source
              </p>
            </div>
          </div>

          <div class="space-y-3">
            <StoryCard
              v-for="(story, index) in topPicks"
              :key="story.story_id"
              :story="story"
              :rank="index + 1"
              accent-type="highlight"
              :show-entities="true"
              :show-categories="true"
              :show-source="true"
              :show-authors="true"
              :show-summary="true"
              class="animate-fade-up"
              :class="[`delay-${index + 3}`]"
            />
          </div>
        </section>

        <!-- Quick Stats -->
        <section class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="card p-4 text-center">
            <div
              class="text-2xl font-bold text-[var(--color-accent-highlight)]"
              style="font-family: var(--font-mono)"
            >
              {{ digestStore.filteredTop5.length }}
            </div>
            <div class="text-xs text-[var(--color-text-tertiary)] mt-1">
              Top Stories
            </div>
          </div>
          <div class="card p-4 text-center">
            <div
              class="text-2xl font-bold text-[var(--color-accent-papers)]"
              style="font-family: var(--font-mono)"
            >
              {{ digestStore.filteredPapers.length }}
            </div>
            <div class="text-xs text-[var(--color-text-tertiary)] mt-1">
              Papers
            </div>
          </div>
          <div class="card p-4 text-center">
            <div
              class="text-2xl font-bold text-[var(--color-accent-models)]"
              style="font-family: var(--font-mono)"
            >
              {{ Object.values(digestStore.filteredModelReleases).flat().length }}
            </div>
            <div class="text-xs text-[var(--color-text-tertiary)] mt-1">
              Model Releases
            </div>
          </div>
          <div class="card p-4 text-center">
            <div
              class="text-2xl font-bold text-[var(--color-accent-radar)]"
              style="font-family: var(--font-mono)"
            >
              {{ digestStore.filteredRadar.length }}
            </div>
            <div class="text-xs text-[var(--color-text-tertiary)] mt-1">
              Radar Items
            </div>
          </div>
        </section>

        <!-- Empty state for overview -->
        <div
          v-if="totalStories === 0"
          class="empty-state"
        >
          <div class="empty-state-icon">
            📭
          </div>
          <h3 class="empty-state-title">
            No content available
          </h3>
          <p class="empty-state-desc">
            No items found for the selected time range. Try expanding the time filter to "All Time".
          </p>
        </div>
      </div>

      <!-- Categories View -->
      <div
        v-show="activeView === 'categories'"
        class="animate-fade-up delay-2"
      >
        <CategorySection />
      </div>

      <!-- Sources View -->
      <div
        v-show="activeView === 'sources'"
        class="animate-fade-up delay-2"
      >
        <SourceGroupSection />
      </div>
    </template>
  </div>
</template>
