<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useDigestStore } from '@/stores/digest'
import StoryCard from '@/components/ui/StoryCard.vue'
import type { Story } from '@/types/digest'

const digestStore = useDigestStore()

const isLoading = computed(() => digestStore.isLoading)
const hasError = computed(() => digestStore.error !== null)
const errorMessage = computed(() => digestStore.error)
const runDate = computed(() => digestStore.runDate)
const runInfo = computed(() => digestStore.runInfo)
const timeFilter = computed(() => digestStore.timeFilter)

// Active view: 'all' | 'category' | 'source'
const activeView = ref<'all' | 'category' | 'source'>('all')

// Expanded categories/sources for accordion views
const expandedCategories = ref<Set<string>>(new Set())
const expandedSources = ref<Set<string>>(new Set())

// Time filter toggle handler
const setTimeFilter = (filter: 'all' | '24h') => {
  digestStore.setTimeFilter(filter)
}

// Format the last update time
const lastUpdated = computed(() => {
  if (!runInfo.value?.finished_at) return null
  const date = new Date(runInfo.value.finished_at)
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
})

// Total story count (using filtered data)
const totalStories = computed(() => digestStore.filteredTotalStories)

// Total categories
const totalCategories = computed(() => Object.keys(digestStore.papersByCategoryWithPicks).length)

// Get source stats
const sourceStats = computed(() => {
  const stats = digestStore.sourcesByStatus
  return {
    healthy: stats.healthy.length,
    failed: stats.failed.length,
    noUpdate: stats.noUpdate.length,
    total: stats.healthy.length + stats.failed.length + stats.noUpdate.length,
  }
})

// All papers for "All" view - combine top5, papers, radar, and releases
const allPapers = computed(() => {
  const seen = new Set<string>()
  const result: Story[] = []

  // Add top5 first (featured)
  for (const story of digestStore.filteredTop5) {
    if (!seen.has(story.story_id)) {
      seen.add(story.story_id)
      result.push(story)
    }
  }

  // Add papers
  for (const story of digestStore.filteredPapers) {
    if (!seen.has(story.story_id)) {
      seen.add(story.story_id)
      result.push(story)
    }
  }

  // Add radar
  for (const story of digestStore.filteredRadar) {
    if (!seen.has(story.story_id)) {
      seen.add(story.story_id)
      result.push(story)
    }
  }

  // Add model releases
  for (const stories of Object.values(digestStore.filteredModelReleases)) {
    for (const story of stories) {
      if (!seen.has(story.story_id)) {
        seen.add(story.story_id)
        result.push(story)
      }
    }
  }

  return result
})

// Papers by category with sorted categories
const categoriesWithPapers = computed(() => {
  const data = digestStore.papersByCategoryWithPicks
  return digestStore.sortedCategories
    .filter(cat => data[cat])
    .map(category => ({
      category,
      papers: data[category].stories,
      topPick: data[category].topPick,
      count: data[category].stories.length,
    }))
})

// Papers by source type - flatten the nested structure
const sourceGroups = computed(() => {
  const groups = digestStore.allStoriesBySourceCategory
  return Object.entries(groups)
    .filter(([_, sourceList]) => sourceList.length > 0)
    .map(([sourceType, sourceList]) => {
      // Flatten all stories from all sources in this category
      const allStories = sourceList.flatMap(source => source.stories)
      return {
        sourceType,
        stories: allStories,
        count: allStories.length,
        label: getSourceLabel(sourceType),
        icon: getSourceIcon(sourceType),
      }
    })
    .filter(group => group.count > 0)
    .sort((a, b) => b.count - a.count)
})

function getSourceLabel(sourceType: string): string {
  const labels: Record<string, string> = {
    arxiv: 'arXiv Papers',
    huggingface: 'Hugging Face',
    blog: 'Blog Posts',
    github: 'GitHub',
    news: 'News',
  }
  return labels[sourceType] || sourceType
}

function getSourceIcon(sourceType: string): string {
  const icons: Record<string, string> = {
    arxiv: '📄',
    huggingface: '🤗',
    blog: '📝',
    github: '🐙',
    news: '📰',
  }
  return icons[sourceType] || '📌'
}

// Toggle category expansion
function toggleCategory(category: string) {
  if (expandedCategories.value.has(category)) {
    expandedCategories.value.delete(category)
  } else {
    expandedCategories.value.add(category)
  }
  expandedCategories.value = new Set(expandedCategories.value)
}

// Toggle source expansion
function toggleSource(sourceType: string) {
  if (expandedSources.value.has(sourceType)) {
    expandedSources.value.delete(sourceType)
  } else {
    expandedSources.value.add(sourceType)
  }
  expandedSources.value = new Set(expandedSources.value)
}

// Auto-expand first category/source on mount
onMounted(() => {
  if (categoriesWithPapers.value.length > 0) {
    expandedCategories.value.add(categoriesWithPapers.value[0].category)
  }
  if (sourceGroups.value.length > 0) {
    expandedSources.value.add(sourceGroups.value[0].sourceType)
  }
})

// Reset expansions when switching views
watch(activeView, () => {
  expandedCategories.value = new Set()
  expandedSources.value = new Set()

  // Auto-expand first item in new view
  setTimeout(() => {
    if (activeView.value === 'category' && categoriesWithPapers.value.length > 0) {
      expandedCategories.value.add(categoriesWithPapers.value[0].category)
    }
    if (activeView.value === 'source' && sourceGroups.value.length > 0) {
      expandedSources.value.add(sourceGroups.value[0].sourceType)
    }
  }, 100)
})
</script>

<template>
  <div
    data-testid="home-page"
    class="home-page"
  >
    <!-- ═══════════════════════════════════════════════════════════════════
         HERO HEADER SECTION
         ═══════════════════════════════════════════════════════════════════ -->
    <header class="hero-header">
      <div class="hero-title-row">
        <div class="hero-title-group">
          <h1 class="hero-title">
            Daily Paper Report
          </h1>
          <p
            v-if="runDate"
            class="hero-subtitle"
          >
            {{ runDate }}
            <span class="hero-divider">·</span>
            <RouterLink
              :to="`/day/${runDate}`"
              class="hero-link"
            >
              Permanent link
            </RouterLink>
          </p>
          <p
            v-else-if="isLoading"
            class="hero-subtitle-skeleton"
          />
        </div>

        <!-- Time Filter Toggle -->
        <div
          v-if="!isLoading && !hasError"
          class="time-toggle"
        >
          <button
            class="time-toggle-btn"
            :class="{ active: timeFilter === 'all' }"
            @click="setTimeFilter('all')"
          >
            All Time
          </button>
          <button
            class="time-toggle-btn"
            :class="{ active: timeFilter === '24h' }"
            @click="setTimeFilter('24h')"
          >
            Last 24h
          </button>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════════════
           HERO STATS GRID
           ═══════════════════════════════════════════════════════════════════ -->
      <div
        v-if="!isLoading && !hasError"
        class="stats-grid"
      >
        <div class="stat-card stat-card--primary">
          <div class="stat-value">
            {{ totalStories }}
          </div>
          <div class="stat-label">
            Total Papers
          </div>
        </div>

        <div class="stat-card stat-card--accent">
          <div class="stat-value">
            {{ totalCategories }}
          </div>
          <div class="stat-label">
            Categories
          </div>
        </div>

        <div class="stat-card stat-card--success">
          <div class="stat-value">
            {{ sourceStats.healthy }}
          </div>
          <div class="stat-label">
            Sources OK
          </div>
        </div>

        <div
          class="stat-card"
          :class="sourceStats.failed > 0 ? 'stat-card--danger' : 'stat-card--muted'"
        >
          <div class="stat-value">
            {{ sourceStats.failed }}
          </div>
          <div class="stat-label">
            Failed
          </div>
        </div>

        <div class="stat-card stat-card--subtle">
          <div class="stat-value stat-value--small">
            {{ lastUpdated || '—' }}
          </div>
          <div class="stat-label">
            Last Updated
          </div>
        </div>
      </div>

      <!-- Stats Skeleton -->
      <div
        v-else-if="isLoading"
        class="stats-grid"
      >
        <div
          v-for="i in 5"
          :key="i"
          class="stat-card stat-card--skeleton"
        >
          <div class="stat-value-skeleton" />
          <div class="stat-label-skeleton" />
        </div>
      </div>
    </header>

    <!-- ═══════════════════════════════════════════════════════════════════
         TAB NAVIGATION
         ═══════════════════════════════════════════════════════════════════ -->
    <nav
      v-if="!isLoading && !hasError"
      class="tab-nav"
    >
      <button
        class="tab-nav-btn"
        :class="{ active: activeView === 'all' }"
        @click="activeView = 'all'"
      >
        <span class="tab-icon">📄</span>
        <span class="tab-text">All Papers</span>
        <span class="tab-count">{{ allPapers.length }}</span>
      </button>

      <button
        class="tab-nav-btn"
        :class="{ active: activeView === 'category' }"
        @click="activeView = 'category'"
      >
        <span class="tab-icon">📁</span>
        <span class="tab-text">By Category</span>
        <span class="tab-count">{{ totalCategories }}</span>
      </button>

      <button
        class="tab-nav-btn"
        :class="{ active: activeView === 'source' }"
        @click="activeView = 'source'"
      >
        <span class="tab-icon">🔗</span>
        <span class="tab-text">By Source</span>
        <span class="tab-count">{{ sourceGroups.length }}</span>
      </button>
    </nav>

    <!-- Tab Navigation Skeleton -->
    <nav
      v-else-if="isLoading"
      class="tab-nav"
    >
      <div
        v-for="i in 3"
        :key="i"
        class="tab-nav-skeleton"
      />
    </nav>

    <!-- ═══════════════════════════════════════════════════════════════════
         CONTENT AREA
         ═══════════════════════════════════════════════════════════════════ -->

    <!-- Loading State -->
    <div
      v-if="isLoading"
      class="content-area"
      data-testid="loading-state"
    >
      <div
        v-for="i in 5"
        :key="i"
        class="paper-skeleton"
      >
        <div class="paper-skeleton-badges" />
        <div class="paper-skeleton-title" />
        <div class="paper-skeleton-meta" />
        <div class="paper-skeleton-summary" />
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="hasError"
      class="error-state"
      data-testid="error-state"
    >
      <div class="error-icon">
        ⚠️
      </div>
      <h3 class="error-title">
        Failed to load digest
      </h3>
      <p class="error-message">
        {{ errorMessage }}
      </p>
      <button
        class="retry-btn"
        data-testid="retry-button"
        @click="digestStore.fetchDigest()"
      >
        <svg
          class="retry-icon"
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
    <main
      v-else
      class="content-area"
    >
      <!-- ═══════════════════════════════════════════════════════════════════
           ALL PAPERS VIEW
           ═══════════════════════════════════════════════════════════════════ -->
      <div
        v-show="activeView === 'all'"
        class="papers-list"
      >
        <StoryCard
          v-for="(story, index) in allPapers"
          :key="story.story_id"
          :story="story"
          :rank="index < 5 ? index + 1 : undefined"
          :accent-type="index < 5 ? 'highlight' : undefined"
          :featured="index < 5"
          :show-entities="true"
          :show-categories="true"
          :show-source="true"
          :show-authors="true"
          :show-summary="true"
          class="paper-card-animated"
          :style="{ '--delay': `${Math.min(index, 10) * 50}ms` }"
        />

        <!-- Empty State -->
        <div
          v-if="allPapers.length === 0"
          class="empty-state"
        >
          <div class="empty-icon">
            📭
          </div>
          <h3 class="empty-title">
            No papers available
          </h3>
          <p class="empty-desc">
            No items found for the selected time range. Try "All Time".
          </p>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════════════
           BY CATEGORY VIEW
           ═══════════════════════════════════════════════════════════════════ -->
      <div
        v-show="activeView === 'category'"
        class="accordion-list"
      >
        <div
          v-for="cat in categoriesWithPapers"
          :key="cat.category"
          class="accordion-item"
          :class="{ expanded: expandedCategories.has(cat.category) }"
        >
          <button
            class="accordion-header"
            @click="toggleCategory(cat.category)"
          >
            <span class="accordion-icon">
              {{ expandedCategories.has(cat.category) ? '▼' : '▶' }}
            </span>
            <span class="accordion-title">{{ cat.category }}</span>
            <span class="accordion-count">{{ cat.count }}</span>
          </button>

          <div
            v-show="expandedCategories.has(cat.category)"
            class="accordion-content"
          >
            <!-- Top Pick -->
            <div
              v-if="cat.topPick"
              class="top-pick-banner"
            >
              <span class="top-pick-label">⭐ Top Pick</span>
            </div>
            <StoryCard
              v-if="cat.topPick"
              :story="cat.topPick"
              :rank="1"
              accent-type="highlight"
              :featured="true"
              :show-entities="true"
              :show-categories="false"
              :show-source="true"
              :show-authors="true"
              :show-summary="true"
              class="top-pick-card"
            />

            <!-- Other Papers -->
            <StoryCard
              v-for="(story, idx) in cat.papers.filter(s => s.story_id !== cat.topPick?.story_id)"
              :key="story.story_id"
              :story="story"
              :show-entities="true"
              :show-categories="false"
              :show-source="true"
              :show-authors="true"
              :show-summary="true"
              class="paper-card-animated"
              :style="{ '--delay': `${idx * 30}ms` }"
            />
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="categoriesWithPapers.length === 0"
          class="empty-state"
        >
          <div class="empty-icon">
            📁
          </div>
          <h3 class="empty-title">
            No categories available
          </h3>
          <p class="empty-desc">
            No categorized papers found for the selected time range.
          </p>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════════════
           BY SOURCE VIEW
           ═══════════════════════════════════════════════════════════════════ -->
      <div
        v-show="activeView === 'source'"
        class="accordion-list"
      >
        <div
          v-for="group in sourceGroups"
          :key="group.sourceType"
          class="accordion-item"
          :class="{ expanded: expandedSources.has(group.sourceType) }"
        >
          <button
            class="accordion-header"
            @click="toggleSource(group.sourceType)"
          >
            <span class="accordion-icon">
              {{ expandedSources.has(group.sourceType) ? '▼' : '▶' }}
            </span>
            <span class="accordion-emoji">{{ group.icon }}</span>
            <span class="accordion-title">{{ group.label }}</span>
            <span class="accordion-count">{{ group.count }}</span>
          </button>

          <div
            v-show="expandedSources.has(group.sourceType)"
            class="accordion-content"
          >
            <StoryCard
              v-for="(story, idx) in group.stories"
              :key="story.story_id"
              :story="story"
              :show-entities="true"
              :show-categories="true"
              :show-source="false"
              :show-authors="true"
              :show-summary="true"
              class="paper-card-animated"
              :style="{ '--delay': `${idx * 30}ms` }"
            />
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="sourceGroups.length === 0"
          class="empty-state"
        >
          <div class="empty-icon">
            🔗
          </div>
          <h3 class="empty-title">
            No sources available
          </h3>
          <p class="empty-desc">
            No items found from any source for the selected time range.
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   HOMEPAGE REDESIGN - PREMIUM DARK THEME
   Aesthetic: Professional research dashboard with clear visual hierarchy
   ═══════════════════════════════════════════════════════════════════════════ */

.home-page {
  --stat-primary: #60a5fa;      /* Blue - Total Papers */
  --stat-accent: #a78bfa;       /* Purple - Categories */
  --stat-success: #34d399;      /* Green - Sources OK */
  --stat-danger: #f87171;       /* Red - Failed */
  --stat-subtle: #94a3b8;       /* Gray - Updated */

  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ═══════════════════════════════════════════════════════════════════════════
   HERO HEADER
   ═══════════════════════════════════════════════════════════════════════════ */

.hero-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  animation: fadeInDown 0.5s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-title-row {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 640px) {
  .hero-title-row {
    flex-direction: row;
    align-items: flex-start;
    justify-content: space-between;
  }
}

.hero-title-group {
  flex: 1;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

@media (min-width: 640px) {
  .hero-title {
    font-size: 2.25rem;
  }
}

.hero-subtitle {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.hero-divider {
  margin: 0 0.375rem;
  opacity: 0.5;
}

.hero-link {
  color: var(--color-accent-highlight);
  text-decoration: none;
  transition: opacity 0.15s;
}

.hero-link:hover {
  opacity: 0.8;
  text-decoration: underline;
}

.hero-subtitle-skeleton {
  margin-top: 0.5rem;
  height: 1.25rem;
  width: 10rem;
  background: var(--color-surface-elevated);
  border-radius: 0.25rem;
  animation: pulse 1.5s infinite;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TIME TOGGLE
   ═══════════════════════════════════════════════════════════════════════════ */

.time-toggle {
  display: flex;
  background: var(--color-surface-elevated);
  border-radius: 0.5rem;
  padding: 0.25rem;
  border: 1px solid var(--color-border);
}

.time-toggle-btn {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-tertiary);
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.time-toggle-btn:hover {
  color: var(--color-text-secondary);
}

.time-toggle-btn.active {
  background: var(--color-accent-highlight);
  color: #fff;
  font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════════════════════
   STATS GRID
   ═══════════════════════════════════════════════════════════════════════════ */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(5, 1fr);
    gap: 1rem;
  }
}

.stat-card {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1rem;
  text-align: center;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: currentColor;
  opacity: 0;
  transition: opacity 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: currentColor;
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card--primary {
  color: var(--stat-primary);
}

.stat-card--accent {
  color: var(--stat-accent);
}

.stat-card--success {
  color: var(--stat-success);
}

.stat-card--danger {
  color: var(--stat-danger);
}

.stat-card--muted {
  color: var(--color-text-tertiary);
}

.stat-card--subtle {
  color: var(--stat-subtle);
}

.stat-card--skeleton {
  animation: pulse 1.5s infinite;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  color: currentColor;
}

.stat-value--small {
  font-size: 1.125rem;
}

.stat-label {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value-skeleton {
  height: 2rem;
  width: 60%;
  margin: 0 auto;
  background: var(--color-border);
  border-radius: 0.25rem;
}

.stat-label-skeleton {
  margin-top: 0.5rem;
  height: 0.75rem;
  width: 80%;
  margin-left: auto;
  margin-right: auto;
  background: var(--color-border);
  border-radius: 0.25rem;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TAB NAVIGATION
   ═══════════════════════════════════════════════════════════════════════════ */

.tab-nav {
  display: flex;
  gap: 0.5rem;
  padding: 0.25rem;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  animation: fadeIn 0.4s ease-out 0.1s both;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.tab-nav-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-tertiary);
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-nav-btn:hover {
  color: var(--color-text-secondary);
  background: var(--color-surface-hover);
}

.tab-nav-btn.active {
  background: var(--color-accent-highlight);
  color: #fff;
  font-weight: 600;
}

.tab-icon {
  font-size: 1rem;
}

.tab-text {
  display: none;
}

@media (min-width: 480px) {
  .tab-text {
    display: inline;
  }
}

.tab-count {
  padding: 0.125rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: var(--font-mono);
  background: rgba(255, 255, 255, 0.15);
  border-radius: 1rem;
}

.tab-nav-btn:not(.active) .tab-count {
  background: var(--color-surface-hover);
  color: var(--color-text-tertiary);
}

.tab-nav-skeleton {
  flex: 1;
  height: 2.75rem;
  background: var(--color-border);
  border-radius: 0.5rem;
  animation: pulse 1.5s infinite;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CONTENT AREA
   ═══════════════════════════════════════════════════════════════════════════ */

.content-area {
  animation: fadeIn 0.4s ease-out 0.2s both;
}

.papers-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.paper-card-animated {
  animation: slideInUp 0.4s ease-out both;
  animation-delay: var(--delay, 0ms);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ═══════════════════════════════════════════════════════════════════════════
   ACCORDION (Category/Source Views)
   ═══════════════════════════════════════════════════════════════════════════ */

.accordion-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.accordion-item {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
  transition: border-color 0.2s;
}

.accordion-item.expanded {
  border-color: var(--color-accent-highlight);
}

.accordion-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background-color 0.15s;
}

.accordion-header:hover {
  background: var(--color-surface-hover);
}

.accordion-icon {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  transition: transform 0.2s;
}

.accordion-item.expanded .accordion-icon {
  color: var(--color-accent-highlight);
}

.accordion-emoji {
  font-size: 1.125rem;
}

.accordion-title {
  flex: 1;
  font-family: var(--font-display);
}

.accordion-count {
  padding: 0.25rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: var(--font-mono);
  color: var(--color-text-tertiary);
  background: var(--color-surface-hover);
  border-radius: 1rem;
}

.accordion-content {
  padding: 0 0.75rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Top Pick */
.top-pick-banner {
  padding: 0.5rem 0.75rem;
}

.top-pick-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-accent-highlight);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.top-pick-card {
  border: 1px solid var(--color-accent-highlight) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   LOADING SKELETONS
   ═══════════════════════════════════════════════════════════════════════════ */

.paper-skeleton {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.paper-skeleton-badges {
  height: 1.25rem;
  width: 40%;
  background: var(--color-border);
  border-radius: 0.25rem;
  animation: pulse 1.5s infinite;
}

.paper-skeleton-title {
  height: 1.5rem;
  width: 80%;
  background: var(--color-border);
  border-radius: 0.25rem;
  animation: pulse 1.5s infinite;
}

.paper-skeleton-meta {
  height: 1rem;
  width: 50%;
  background: var(--color-border);
  border-radius: 0.25rem;
  animation: pulse 1.5s infinite;
}

.paper-skeleton-summary {
  height: 4rem;
  width: 100%;
  background: var(--color-border);
  border-radius: 0.25rem;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 0.3;
  }
}

/* ═══════════════════════════════════════════════════════════════════════════
   ERROR STATE
   ═══════════════════════════════════════════════════════════════════════════ */

.error-state {
  background: var(--color-surface-elevated);
  border: 1px solid var(--stat-danger);
  border-radius: 0.75rem;
  padding: 3rem 2rem;
  text-align: center;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--stat-danger);
  margin-bottom: 0.5rem;
}

.error-message {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: 1.5rem;
}

.retry-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
  background: var(--color-accent-highlight);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: opacity 0.15s;
}

.retry-btn:hover {
  opacity: 0.9;
}

.retry-icon {
  width: 1rem;
  height: 1rem;
}

/* ═══════════════════════════════════════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════════════════════════════════════ */

.empty-state {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 3rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.empty-desc {
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
}
</style>
