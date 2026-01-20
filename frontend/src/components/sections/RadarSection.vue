<script setup lang="ts">
  import { computed, ref } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import { SECTION_CONFIGS, type Story } from '@/types/digest'
  import SectionHeader from '@/components/ui/SectionHeader.vue'
  import StoryCard from '@/components/ui/StoryCard.vue'
  import EmptyState from '@/components/ui/EmptyState.vue'

  const digestStore = useDigestStore()
  const stories = computed(() => digestStore.radar)
  const sourceNames = computed(() => digestStore.sourceNames)
  const config = SECTION_CONFIGS.radar

  // View mode: 'all' or 'by-source'
  const viewMode = ref<'all' | 'by-source'>('all')

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

  const radarSourceIds = computed(() => Object.keys(radarBySource.value).sort())

  const filteredStories = computed(() => {
    if (viewMode.value === 'all' || !selectedSource.value) {
      return stories.value
    }
    return radarBySource.value[selectedSource.value] ?? []
  })

  const getSourceDisplayName = (sourceId: string): string => {
    return sourceNames.value[sourceId] ?? sourceId
  }
</script>

<template>
  <section
    class="mb-10"
    data-testid="section-radar"
  >
    <SectionHeader :config="config" />

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
          class="px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-[var(--duration-fast)]"
          :class="
            viewMode === 'all'
              ? 'bg-[var(--color-surface-elevated)] text-[var(--color-text-primary)] shadow-[var(--shadow-sm)]'
              : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'
          "
          @click="viewMode = 'all'; selectedSource = null"
        >
          All Items
        </button>
        <button
          class="px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-[var(--duration-fast)]"
          :class="
            viewMode === 'by-source'
              ? 'bg-[var(--color-surface-elevated)] text-[var(--color-text-primary)] shadow-[var(--shadow-sm)]'
              : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'
          "
          @click="viewMode = 'by-source'"
        >
          By Source
        </button>
      </div>

      <!-- Source Filter Pills (when in by-source mode) -->
      <div
        v-if="viewMode === 'by-source' && radarSourceIds.length > 1"
        class="flex flex-wrap gap-2"
      >
        <button
          class="px-2.5 py-1 text-xs font-medium rounded-full transition-all duration-[var(--duration-fast)] border"
          :class="
            selectedSource === null
              ? 'bg-[var(--color-accent-radar)] text-white border-[var(--color-accent-radar)]'
              : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border-[var(--color-border-default)] hover:border-[var(--color-accent-radar)]/50 hover:text-[var(--color-accent-radar)]'
          "
          @click="selectedSource = null"
        >
          All ({{ stories.length }})
        </button>
        <button
          v-for="sourceId in radarSourceIds"
          :key="sourceId"
          class="px-2.5 py-1 text-xs font-medium rounded-full transition-all duration-[var(--duration-fast)] border"
          :class="
            selectedSource === sourceId
              ? 'bg-[var(--color-accent-radar)] text-white border-[var(--color-accent-radar)]'
              : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border-[var(--color-border-default)] hover:border-[var(--color-accent-radar)]/50 hover:text-[var(--color-accent-radar)]'
          "
          @click="selectedSource = sourceId"
        >
          {{ getSourceDisplayName(sourceId) }} ({{ radarBySource[sourceId]?.length ?? 0 }})
        </button>
      </div>
    </div>

    <!-- Radar List - Grouped by Source -->
    <div
      v-if="stories.length > 0 && viewMode === 'by-source' && selectedSource === null"
      class="space-y-8"
    >
      <div
        v-for="sourceId in radarSourceIds"
        :key="sourceId"
        class="animate-fade-in-up"
      >
        <h3
          class="flex items-center gap-2 text-sm font-semibold text-[var(--color-text-secondary)] mb-3 pb-2 border-b border-[var(--color-border-light)]"
        >
          <span class="w-2 h-2 rounded-full bg-[var(--color-accent-radar)]" />
          {{ getSourceDisplayName(sourceId) }}
          <span class="text-[var(--color-text-muted)] font-normal">
            ({{ radarBySource[sourceId]?.length ?? 0 }})
          </span>
        </h3>
        <div class="space-y-3">
          <StoryCard
            v-for="story in radarBySource[sourceId]"
            :key="story.story_id"
            :story="story"
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
        v-for="story in filteredStories"
        :key="story.story_id"
        :story="story"
        accent-class="accent-radar"
      />
    </div>

    <EmptyState
      v-else
      title="No radar items today"
      description="Check back tomorrow!"
    />
  </section>
</template>
