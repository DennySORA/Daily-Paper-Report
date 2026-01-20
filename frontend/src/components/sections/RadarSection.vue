<script setup lang="ts">
  import { computed, ref } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import type { Story } from '@/types/digest'
  import StoryCard from '@/components/ui/StoryCard.vue'
  import EmptyState from '@/components/ui/EmptyState.vue'
  import { IconGlobe } from '@/components/icons'

  const digestStore = useDigestStore()
  const stories = computed(() => digestStore.filteredRadar)
  const sourceNames = computed(() => digestStore.sourceNames)

  // View mode: 'all' or 'by-source'
  const viewMode = ref<'all' | 'by-source'>('by-source')

  // Selected source for filter (null = show all)
  const selectedSource = ref<string | null>(null)

  // Get radar stories grouped by source
  const radarBySource = computed(() => {
    const grouped: Record<string, Story[]> = {}
    for (const story of stories.value) {
      const sourceId = story.primary_link.source_id
      if (!grouped[sourceId]) {
        grouped[sourceId] = []
      }
      grouped[sourceId].push(story)
    }
    return grouped
  })

  // Sort sources by story count
  const radarSourceIds = computed(() =>
    Object.keys(radarBySource.value).sort(
      (a, b) => (radarBySource.value[b]?.length ?? 0) - (radarBySource.value[a]?.length ?? 0),
    ),
  )

  const filteredStories = computed(() => {
    if (viewMode.value === 'all' || !selectedSource.value) {
      return stories.value
    }
    return radarBySource.value[selectedSource.value] ?? []
  })

  const getSourceDisplayName = (sourceId: string): string => {
    return sourceNames.value[sourceId] ?? formatSourceId(sourceId)
  }

  // Format source ID to readable name
  const formatSourceId = (sourceId: string): string => {
    return sourceId
      .replace(/-/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase())
  }

  // Get source icon color based on source type
  const getSourceColor = (sourceId: string): string => {
    if (sourceId.includes('aws')) return 'oklch(0.7 0.15 40)'
    if (sourceId.includes('google')) return 'oklch(0.65 0.18 145)'
    if (sourceId.includes('nvidia')) return 'oklch(0.7 0.2 130)'
    if (sourceId.includes('microsoft')) return 'oklch(0.6 0.15 220)'
    if (sourceId.includes('meta')) return 'oklch(0.6 0.18 250)'
    return 'var(--color-accent-radar)'
  }
</script>

<template>
  <div data-testid="section-radar">
    <!-- Section description -->
    <p class="text-sm text-[var(--color-text-muted)] mb-5">
      AI ecosystem updates from leading tech companies: blog posts, tools, datasets, and industry
      news worth tracking.
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
          :class="{ active: viewMode === 'by-source' }"
          @click="viewMode = 'by-source'"
        >
          By Source
        </button>
        <button
          class="filter-toggle-btn"
          :class="{ active: viewMode === 'all' }"
          @click="viewMode = 'all'"
        >
          All Items
        </button>
      </div>

      <!-- Source Filter Pills (when in by-source mode) -->
      <div
        v-if="viewMode === 'by-source' && radarSourceIds.length > 1"
        class="flex flex-wrap gap-2"
      >
        <button
          class="badge badge-default press-effect"
          :class="{
            '!bg-[var(--color-accent-radar)] !text-white': selectedSource === null,
          }"
          @click="selectedSource = null"
        >
          All ({{ stories.length }})
        </button>
        <button
          v-for="sourceId in radarSourceIds"
          :key="sourceId"
          class="badge badge-default press-effect"
          :class="{
            '!bg-[var(--color-accent-radar)] !text-white': selectedSource === sourceId,
          }"
          @click="selectedSource = sourceId"
        >
          {{ getSourceDisplayName(sourceId) }} ({{ radarBySource[sourceId]?.length ?? 0 }})
        </button>
      </div>
    </div>

    <!-- Radar List - Grouped by Source -->
    <div
      v-if="stories.length > 0 && viewMode === 'by-source' && selectedSource === null"
      class="space-y-6"
    >
      <div
        v-for="(sourceId, index) in radarSourceIds"
        :key="sourceId"
        class="source-group animate-fade-in-up"
        :class="`stagger-${Math.min(index + 1, 5)}`"
      >
        <!-- Source Header -->
        <div class="source-group-header">
          <div
            class="source-group-icon"
            :style="{ color: getSourceColor(sourceId) }"
          >
            <IconGlobe :size="20" />
          </div>
          <div class="flex-1 min-w-0">
            <h3
              class="font-semibold text-[var(--color-text-primary)] truncate"
              style="font-family: var(--font-display)"
            >
              {{ getSourceDisplayName(sourceId) }}
            </h3>
            <p class="text-xs text-[var(--color-text-muted)]">
              {{ radarBySource[sourceId]?.length ?? 0 }} item{{
                (radarBySource[sourceId]?.length ?? 0) !== 1 ? 's' : ''
              }}
            </p>
          </div>
        </div>

        <!-- Source Stories -->
        <div class="source-group-content space-y-3">
          <StoryCard
            v-for="story in radarBySource[sourceId]"
            :key="story.story_id"
            :story="story"
            :show-summary="true"
            :show-authors="true"
            accent-class="accent-radar"
          />
        </div>
      </div>
    </div>

    <!-- Radar List - Flat or Filtered -->
    <div
      v-else-if="stories.length > 0"
      class="space-y-3"
    >
      <StoryCard
        v-for="(story, index) in filteredStories"
        :key="story.story_id"
        :story="story"
        :show-summary="true"
        :show-authors="true"
        accent-class="accent-radar"
        :class="`stagger-${Math.min(index + 1, 8)}`"
      />
    </div>

    <EmptyState
      v-else
      title="No radar items"
      description="No updates from tracked sources in this time period."
    />
  </div>
</template>
