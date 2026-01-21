<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useDigestStore } from '@/stores/digest'
import StoryCard from '@/components/ui/StoryCard.vue'
import type { Story } from '@/types/digest'

const digestStore = useDigestStore()

// Core state
const isLoading = computed(() => digestStore.isLoading)
const hasError = computed(() => digestStore.error !== null)
const errorMessage = computed(() => digestStore.error)
const runDate = computed(() => digestStore.runDate)
const runInfo = computed(() => digestStore.runInfo)
const timeFilter = computed(() => digestStore.timeFilter)

// Tab state
type TabView = 'all' | 'category' | 'source'
const activeTab = ref<TabView>('all')

// Accordion state
const expandedCategories = ref<Set<string>>(new Set())
const expandedSources = ref<Set<string>>(new Set())

// Time filter handler
function setTimeFilter(filter: 'all' | '24h') {
  digestStore.setTimeFilter(filter)
}

// Stats computation
const stats = computed(() => {
  const sourceStats = digestStore.sourcesByStatus
  const working = sourceStats.healthy.length + sourceStats.noUpdate.length
  const failed = sourceStats.failed.length

  return {
    papers: digestStore.filteredTotalStories,
    categories: Object.keys(digestStore.papersByCategoryWithPicks).length,
    sourcesOk: working,
    sourcesFailed: failed,
    lastUpdated: runInfo.value?.finished_at
      ? new Date(runInfo.value.finished_at).toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true,
        })
      : null,
  }
})

// All papers combined
const allPapers = computed(() => {
  const seen = new Set<string>()
  const result: Story[] = []

  const addStories = (stories: Story[]) => {
    for (const story of stories) {
      if (!seen.has(story.story_id)) {
        seen.add(story.story_id)
        result.push(story)
      }
    }
  }

  addStories(digestStore.filteredTop5)
  addStories(digestStore.filteredPapers)
  addStories(digestStore.filteredRadar)

  for (const stories of Object.values(digestStore.filteredModelReleases)) {
    addStories(stories)
  }

  return result
})

// Papers by category
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

// Papers by source
const sourceGroups = computed(() => {
  const groups = digestStore.allStoriesBySourceCategory
  const labels: Record<string, string> = {
    arxiv: 'arXiv Papers',
    huggingface: 'Hugging Face',
    blog: 'Blog Posts',
    github: 'GitHub',
    news: 'News',
  }
  const icons: Record<string, string> = {
    arxiv: '📄',
    huggingface: '🤗',
    blog: '📝',
    github: '🐙',
    news: '📰',
  }

  return Object.entries(groups)
    .filter(([_, sourceList]) => sourceList.length > 0)
    .map(([sourceType, sourceList]) => {
      const allStories = sourceList.flatMap(source => source.stories)
      return {
        sourceType,
        stories: allStories,
        count: allStories.length,
        label: labels[sourceType] || sourceType,
        icon: icons[sourceType] || '📌',
      }
    })
    .filter(group => group.count > 0)
    .sort((a, b) => b.count - a.count)
})

// Toggle handlers
function toggleCategory(category: string) {
  const newSet = new Set(expandedCategories.value)
  if (newSet.has(category)) {
    newSet.delete(category)
  } else {
    newSet.add(category)
  }
  expandedCategories.value = newSet
}

function toggleSource(sourceType: string) {
  const newSet = new Set(expandedSources.value)
  if (newSet.has(sourceType)) {
    newSet.delete(sourceType)
  } else {
    newSet.add(sourceType)
  }
  expandedSources.value = newSet
}

// Auto-expand ALL categories and first source on mount for faster scanning
onMounted(() => {
  // Expand all categories by default - researchers need to scan quickly
  for (const cat of categoriesWithPapers.value) {
    expandedCategories.value.add(cat.category)
  }
  // Expand all sources by default
  for (const group of sourceGroups.value) {
    expandedSources.value.add(group.sourceType)
  }
})

// When switching tabs, expand all items for fast scanning
watch(activeTab, newTab => {
  expandedCategories.value = new Set()
  expandedSources.value = new Set()

  setTimeout(() => {
    if (newTab === 'category') {
      // Expand all categories
      for (const cat of categoriesWithPapers.value) {
        expandedCategories.value.add(cat.category)
      }
    }
    if (newTab === 'source') {
      // Expand all sources
      for (const group of sourceGroups.value) {
        expandedSources.value.add(group.sourceType)
      }
    }
  }, 50)
})

// Tab definitions
const tabs = [
  { id: 'all' as const, label: 'All Papers', icon: '📄' },
  { id: 'category' as const, label: 'By Category', icon: '📁' },
  { id: 'source' as const, label: 'By Source', icon: '🔗' },
]

function getTabCount(tabId: TabView): number {
  switch (tabId) {
    case 'all':
      return allPapers.value.length
    case 'category':
      return categoriesWithPapers.value.length
    case 'source':
      return sourceGroups.value.length
  }
}
</script>

<template>
  <div
    data-testid="home-page"
    class="dashboard"
  >
    <!-- ═══════════════════════════════════════════════════════════════
         DASHBOARD HEADER - Title + Date + Time Filter
         ═══════════════════════════════════════════════════════════════ -->
    <header class="dashboard-header">
      <div class="header-title-group">
        <h1 class="header-title">
          Daily Paper Report
        </h1>
        <div
          v-if="runDate"
          class="header-meta"
        >
          <span class="header-date">{{ runDate }}</span>
          <span class="header-separator">·</span>
          <RouterLink
            :to="`/day/${runDate}`"
            class="header-link"
          >
            Permalink
          </RouterLink>
        </div>
        <div
          v-else-if="isLoading"
          class="header-meta-skeleton"
        />
      </div>

      <!-- Time Filter -->
      <div
        v-if="!isLoading && !hasError"
        class="time-filter"
      >
        <button
          class="time-filter-btn"
          :class="{ active: timeFilter === 'all' }"
          @click="setTimeFilter('all')"
        >
          All
        </button>
        <button
          class="time-filter-btn"
          :class="{ active: timeFilter === '24h' }"
          @click="setTimeFilter('24h')"
        >
          24h
        </button>
      </div>
    </header>

    <!-- ═══════════════════════════════════════════════════════════════
         STATS DASHBOARD - Prominent metrics with clear visual hierarchy
         ═══════════════════════════════════════════════════════════════ -->
    <section
      v-if="!isLoading && !hasError"
      class="stats-dashboard"
    >
      <div class="stat-card stat-papers">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.papers }}
          </div>
          <div class="stat-label">
            Papers
          </div>
        </div>
      </div>

      <div class="stat-card stat-categories">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.categories }}
          </div>
          <div class="stat-label">
            Categories
          </div>
        </div>
      </div>

      <div class="stat-card stat-sources-ok">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.sourcesOk }}
          </div>
          <div class="stat-label">
            Sources OK
          </div>
        </div>
      </div>

      <div
        class="stat-card"
        :class="stats.sourcesFailed > 0 ? 'stat-sources-failed' : 'stat-muted'"
      >
        <div class="stat-icon">
          <svg v-if="stats.sourcesFailed > 0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.sourcesFailed }}
          </div>
          <div class="stat-label">
            Failed
          </div>
        </div>
      </div>

      <div class="stat-card stat-updated">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value stat-value-time">
            {{ stats.lastUpdated || '—' }}
          </div>
          <div class="stat-label">
            Updated
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Skeleton -->
    <section
      v-else-if="isLoading"
      class="stats-dashboard"
    >
      <div
        v-for="i in 5"
        :key="i"
        class="stat-card stat-skeleton"
      >
        <div class="stat-icon-skeleton" />
        <div class="stat-content">
          <div class="stat-value-skeleton" />
          <div class="stat-label-skeleton" />
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════════════════
         TAB NAVIGATION - Clear view selection
         ═══════════════════════════════════════════════════════════════ -->
    <nav
      v-if="!isLoading && !hasError"
      class="tabs-nav"
    >
      <div class="tabs-container">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
          <span class="tab-count">{{ getTabCount(tab.id) }}</span>
        </button>
      </div>
    </nav>

    <!-- Tab Skeleton -->
    <nav
      v-else-if="isLoading"
      class="tabs-nav"
    >
      <div class="tabs-container">
        <div
          v-for="i in 3"
          :key="i"
          class="tab-skeleton"
        />
      </div>
    </nav>

    <!-- ═══════════════════════════════════════════════════════════════
         CONTENT AREA
         ═══════════════════════════════════════════════════════════════ -->

    <!-- Loading State -->
    <div
      v-if="isLoading"
      class="content-loading"
    >
      <div
        v-for="i in 5"
        :key="i"
        class="card-skeleton"
      >
        <div class="card-skeleton-header" />
        <div class="card-skeleton-title" />
        <div class="card-skeleton-meta" />
        <div class="card-skeleton-body" />
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="hasError"
      class="error-panel"
    >
      <div class="error-icon">
        ⚠
      </div>
      <h3 class="error-title">
        Failed to load digest
      </h3>
      <p class="error-message">
        {{ errorMessage }}
      </p>
      <button
        class="error-retry"
        @click="digestStore.fetchDigest()"
      >
        <svg
          class="retry-icon"
          viewBox="0 0 24 24"
          fill="none"
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
      class="content-main"
    >
      <!-- ALL PAPERS VIEW -->
      <div
        v-show="activeTab === 'all'"
        class="content-panel"
      >
        <div
          v-if="allPapers.length > 0"
          class="papers-grid"
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
            class="paper-item"
            :style="{ '--index': Math.min(index, 10) }"
          />
        </div>

        <div
          v-else
          class="empty-panel"
        >
          <div class="empty-icon">
            📭
          </div>
          <h3 class="empty-title">
            No papers found
          </h3>
          <p class="empty-desc">
            Try selecting "All" in the time filter above.
          </p>
        </div>
      </div>

      <!-- BY CATEGORY VIEW -->
      <div
        v-show="activeTab === 'category'"
        class="content-panel"
      >
        <div
          v-if="categoriesWithPapers.length > 0"
          class="accordion-list"
        >
          <div
            v-for="cat in categoriesWithPapers"
            :key="cat.category"
            class="accordion-item"
            :class="{ expanded: expandedCategories.has(cat.category) }"
          >
            <button
              class="accordion-trigger"
              @click="toggleCategory(cat.category)"
            >
              <span class="accordion-arrow">
                {{ expandedCategories.has(cat.category) ? '▼' : '▶' }}
              </span>
              <span class="accordion-title">{{ cat.category }}</span>
              <span class="accordion-count">{{ cat.count }}</span>
            </button>

            <div
              v-show="expandedCategories.has(cat.category)"
              class="accordion-body"
            >
              <!-- Top Pick -->
              <div
                v-if="cat.topPick"
                class="top-pick-section"
              >
                <div class="top-pick-label">
                  ⭐ Top Pick
                </div>
                <StoryCard
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
              </div>

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
                class="paper-item"
                :style="{ '--index': idx }"
              />
            </div>
          </div>
        </div>

        <div
          v-else
          class="empty-panel"
        >
          <div class="empty-icon">
            📁
          </div>
          <h3 class="empty-title">
            No categories found
          </h3>
          <p class="empty-desc">
            No categorized papers for this time range.
          </p>
        </div>
      </div>

      <!-- BY SOURCE VIEW -->
      <div
        v-show="activeTab === 'source'"
        class="content-panel"
      >
        <div
          v-if="sourceGroups.length > 0"
          class="accordion-list"
        >
          <div
            v-for="group in sourceGroups"
            :key="group.sourceType"
            class="accordion-item"
            :class="{ expanded: expandedSources.has(group.sourceType) }"
          >
            <button
              class="accordion-trigger"
              @click="toggleSource(group.sourceType)"
            >
              <span class="accordion-arrow">
                {{ expandedSources.has(group.sourceType) ? '▼' : '▶' }}
              </span>
              <span class="accordion-emoji">{{ group.icon }}</span>
              <span class="accordion-title">{{ group.label }}</span>
              <span class="accordion-count">{{ group.count }}</span>
            </button>

            <div
              v-show="expandedSources.has(group.sourceType)"
              class="accordion-body"
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
                class="paper-item"
                :style="{ '--index': idx }"
              />
            </div>
          </div>
        </div>

        <div
          v-else
          class="empty-panel"
        >
          <div class="empty-icon">
            🔗
          </div>
          <h3 class="empty-title">
            No sources found
          </h3>
          <p class="empty-desc">
            No content from any source for this time range.
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   RESEARCH TERMINAL DESIGN
   A clean, data-focused dashboard for daily paper tracking
   ═══════════════════════════════════════════════════════════════════════════ */

.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  animation: dashboardFadeIn 0.4s ease-out;
}

@keyframes dashboardFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* ═══════════════════════════════════════════════════════════════════════════
   HEADER - Compact title bar
   ═══════════════════════════════════════════════════════════════════════════ */

.dashboard-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

@media (min-width: 640px) {
  .dashboard-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.header-title-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.header-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.025em;
}

@media (min-width: 640px) {
  .header-title {
    font-size: 1.75rem;
  }
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-tertiary);
}

.header-date {
  font-family: var(--font-mono);
  color: var(--color-text-secondary);
}

.header-separator {
  opacity: 0.4;
}

.header-link {
  color: var(--color-accent-primary);
  text-decoration: none;
  transition: color 0.15s ease;
}

.header-link:hover {
  color: var(--color-accent-primary-hover);
  text-decoration: underline;
}

.header-meta-skeleton {
  height: 1rem;
  width: 10rem;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  animation: shimmer 1.5s ease-in-out infinite;
}

/* Time Filter */
.time-filter {
  display: flex;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border-subtle);
  border-radius: 0.5rem;
  padding: 0.1875rem;
}

.time-filter-btn {
  padding: 0.4375rem 0.875rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-tertiary);
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.time-filter-btn:hover:not(.active) {
  color: var(--color-text-secondary);
  background: var(--color-surface-overlay);
}

.time-filter-btn.active {
  color: #fff;
  background: var(--color-accent-primary);
}

/* ═══════════════════════════════════════════════════════════════════════════
   STATS DASHBOARD - The main focus area
   ═══════════════════════════════════════════════════════════════════════════ */

.stats-dashboard {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .stats-dashboard {
    grid-template-columns: repeat(5, 1fr);
  }
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1rem;
  background: var(--color-surface-primary);
  border: 1px solid var(--color-border-subtle);
  border-radius: 0.75rem;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: currentColor;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: currentColor;
}

.stat-card:hover::after {
  opacity: 0.5;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.625rem;
  flex-shrink: 0;
  background: linear-gradient(135deg, currentColor 0%, color-mix(in srgb, currentColor 70%, black) 100%);
}

.stat-icon svg {
  width: 1.25rem;
  height: 1.25rem;
  stroke: #fff;
}

.stat-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.1;
  color: var(--color-text-primary);
}

.stat-value-time {
  font-size: 1rem;
}

.stat-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.125rem;
}

/* Stat colors */
.stat-papers {
  color: #60a5fa;
}

.stat-categories {
  color: #a78bfa;
}

.stat-sources-ok {
  color: #4ade80;
}

.stat-sources-failed {
  color: #f87171;
}

.stat-muted {
  color: var(--color-text-muted);
}

.stat-updated {
  color: #94a3b8;
}

/* Stat skeleton */
.stat-skeleton {
  color: var(--color-border-subtle);
}

.stat-icon-skeleton {
  width: 2.5rem;
  height: 2.5rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  animation: shimmer 1.5s ease-in-out infinite;
}

.stat-value-skeleton {
  height: 1.5rem;
  width: 2.5rem;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  animation: shimmer 1.5s ease-in-out infinite;
}

.stat-label-skeleton {
  height: 0.75rem;
  width: 3.5rem;
  margin-top: 0.25rem;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  animation: shimmer 1.5s ease-in-out infinite;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TAB NAVIGATION - Clean underline style tabs
   ═══════════════════════════════════════════════════════════════════════════ */

.tabs-nav {
  border-bottom: 1px solid var(--color-border-subtle);
}

.tabs-container {
  display: flex;
  gap: 0;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-tertiary);
  background: transparent;
  border: none;
  cursor: pointer;
  position: relative;
  transition: color 0.15s ease;
}

.tab-btn::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-accent-primary);
  transform: scaleX(0);
  transition: transform 0.2s ease;
}

.tab-btn:hover {
  color: var(--color-text-secondary);
}

.tab-btn.active {
  color: var(--color-text-primary);
  font-weight: 600;
}

.tab-btn.active::after {
  transform: scaleX(1);
}

.tab-icon {
  font-size: 1rem;
}

.tab-label {
  display: none;
}

@media (min-width: 480px) {
  .tab-label {
    display: inline;
  }
}

.tab-count {
  padding: 0.125rem 0.5rem;
  font-size: 0.6875rem;
  font-weight: 700;
  font-family: var(--font-mono);
  background: var(--color-surface-secondary);
  color: var(--color-text-muted);
  border-radius: 1rem;
  transition: all 0.15s ease;
}

.tab-btn.active .tab-count {
  background: var(--color-accent-primary);
  color: #fff;
}

.tab-skeleton {
  height: 2.5rem;
  width: 6rem;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  margin: 0.5rem;
  animation: shimmer 1.5s ease-in-out infinite;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CONTENT AREA
   ═══════════════════════════════════════════════════════════════════════════ */

.content-main {
  min-height: 300px;
}

.content-panel {
  animation: panelFadeIn 0.3s ease-out;
}

@keyframes panelFadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.papers-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.paper-item {
  animation: paperSlideIn 0.4s ease-out both;
  animation-delay: calc(var(--index, 0) * 30ms);
}

@keyframes paperSlideIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ═══════════════════════════════════════════════════════════════════════════
   ACCORDION - For category/source views
   ═══════════════════════════════════════════════════════════════════════════ */

.accordion-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.accordion-item {
  background: var(--color-surface-primary);
  border: 1px solid var(--color-border-subtle);
  border-radius: 0.75rem;
  overflow: hidden;
  transition: border-color 0.2s ease;
}

.accordion-item.expanded {
  border-color: var(--color-accent-primary);
}

.accordion-trigger {
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
  transition: background-color 0.15s ease;
}

.accordion-trigger:hover {
  background: var(--color-surface-secondary);
}

.accordion-arrow {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  transition: color 0.2s ease;
}

.accordion-item.expanded .accordion-arrow {
  color: var(--color-accent-primary);
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
  font-size: 0.6875rem;
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  background: var(--color-surface-secondary);
  border-radius: 1rem;
}

.accordion-body {
  padding: 0 0.75rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Top Pick */
.top-pick-section {
  margin-bottom: 0.5rem;
}

.top-pick-label {
  padding: 0.5rem 0.5rem 0.25rem;
  font-size: 0.6875rem;
  font-weight: 700;
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

.content-loading {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card-skeleton {
  background: var(--color-surface-primary);
  border: 1px solid var(--color-border-subtle);
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card-skeleton-header {
  height: 1.25rem;
  width: 35%;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  animation: shimmer 1.5s ease-in-out infinite;
}

.card-skeleton-title {
  height: 1.5rem;
  width: 75%;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  animation: shimmer 1.5s ease-in-out infinite;
}

.card-skeleton-meta {
  height: 1rem;
  width: 50%;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  animation: shimmer 1.5s ease-in-out infinite;
}

.card-skeleton-body {
  height: 4rem;
  width: 100%;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 0.8;
  }
}

/* ═══════════════════════════════════════════════════════════════════════════
   ERROR STATE
   ═══════════════════════════════════════════════════════════════════════════ */

.error-panel {
  background: var(--color-surface-primary);
  border: 1px solid var(--color-accent-error);
  border-radius: 0.75rem;
  padding: 3rem 2rem;
  text-align: center;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--color-accent-error);
}

.error-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-accent-error);
  margin-bottom: 0.5rem;
}

.error-message {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: 1.5rem;
}

.error-retry {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
  background: var(--color-accent-primary);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.error-retry:hover {
  background: var(--color-accent-primary-hover);
}

.retry-icon {
  width: 1rem;
  height: 1rem;
}

/* ═══════════════════════════════════════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════════════════════════════════════ */

.empty-panel {
  background: var(--color-surface-secondary);
  border: 2px dashed var(--color-border-default);
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
  margin-bottom: 0.25rem;
}

.empty-desc {
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
}
</style>
