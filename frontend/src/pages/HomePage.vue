<script setup lang="ts">
  import { computed, ref } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import TabNavigation, { type Tab } from '@/components/ui/TabNavigation.vue'
  import TopStoriesSection from '@/components/sections/TopStoriesSection.vue'
  import PapersSection from '@/components/sections/PapersSection.vue'
  import ModelsSection from '@/components/sections/ModelsSection.vue'
  import RadarSection from '@/components/sections/RadarSection.vue'
  import SkeletonSection from '@/components/ui/SkeletonSection.vue'

  const digestStore = useDigestStore()

  const isLoading = computed(() => digestStore.isLoading)
  const hasError = computed(() => digestStore.error !== null)
  const errorMessage = computed(() => digestStore.error)
  const runDate = computed(() => digestStore.runDate)
  const runInfo = computed(() => digestStore.runInfo)

  // Active tab state
  const activeTab = ref<string>('top5')

  // Tab configuration with counts
  const tabs = computed<Tab[]>(() => {
    const modelCount = Object.values(digestStore.modelReleases).reduce(
      (sum, stories) => sum + stories.length,
      0,
    )
    return [
      { id: 'top5', label: 'Top Stories', count: digestStore.top5.length, icon: 'star' },
      { id: 'papers', label: 'Papers', count: digestStore.papers.length, icon: 'document' },
      { id: 'models', label: 'Models', count: modelCount, icon: 'cpu' },
      { id: 'radar', label: 'Radar', count: digestStore.radar.length, icon: 'globe' },
    ]
  })

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

  // Total story count
  const totalStories = computed(() => digestStore.totalStories)
</script>

<template>
  <div data-testid="home-page">
    <!-- Page Header -->
    <header class="mb-6 animate-fade-in-up">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1
            class="text-2xl font-bold text-[var(--color-text-primary)] tracking-tight"
            style="font-family: var(--font-display)"
          >
            Daily Digest
          </h1>
          <p
            v-if="runDate"
            class="text-sm text-[var(--color-text-secondary)] mt-1"
          >
            {{ runDate }} ·
            <RouterLink
              :to="`/day/${runDate}`"
              class="text-[var(--color-primary-500)] hover:text-[var(--color-primary-400)] hover:underline transition-colors"
            >
              Permanent link
            </RouterLink>
          </p>
          <p
            v-else-if="isLoading"
            class="h-5 bg-[var(--color-surface-tertiary)] rounded w-40 mt-1 animate-shimmer"
          />
        </div>

        <!-- Stats badges -->
        <div
          v-if="!isLoading && !hasError"
          class="flex flex-wrap items-center gap-2"
        >
          <div
            class="px-3 py-1.5 bg-[var(--color-surface-secondary)] rounded-lg border border-[var(--color-border-light)] text-sm"
          >
            <span class="text-[var(--color-text-muted)]">Stories</span>
            <span
              class="ml-1.5 font-semibold text-[var(--color-text-primary)]"
              style="font-family: var(--font-mono)"
            >
              {{ totalStories }}
            </span>
          </div>

          <div
            v-if="lastUpdated"
            class="px-3 py-1.5 bg-[var(--color-surface-secondary)] rounded-lg border border-[var(--color-border-light)] text-sm"
          >
            <span class="text-[var(--color-text-muted)]">Updated</span>
            <span class="ml-1.5 text-[var(--color-text-secondary)]">
              {{ lastUpdated }}
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
      <div class="tab-bar">
        <div
          v-for="i in 4"
          :key="i"
          class="h-10 w-28 rounded-md bg-[var(--color-surface-tertiary)] animate-shimmer"
        />
      </div>
      <SkeletonSection
        :card-count="5"
        :show-ranks="true"
      />
    </div>

    <!-- Error State -->
    <div
      v-else-if="hasError"
      class="bg-[var(--color-error)]/10 border border-[var(--color-error)]/20 rounded-xl p-6 text-center animate-fade-in"
      data-testid="error-state"
    >
      <p class="text-[var(--color-error)] font-semibold">
        Failed to load digest
      </p>
      <p class="text-sm text-[var(--color-text-muted)] mt-1">
        {{ errorMessage }}
      </p>
      <button
        class="btn btn-primary mt-4"
        data-testid="retry-button"
        @click="digestStore.fetchDigest()"
      >
        Retry
      </button>
    </div>

    <!-- Main Content with Tabs -->
    <template v-else>
      <!-- Tab Navigation -->
      <TabNavigation
        v-model:active-tab="activeTab"
        :tabs="tabs"
        class="mb-6 animate-fade-in stagger-1"
      />

      <!-- Tab Panels -->
      <div class="animate-fade-in stagger-2">
        <!-- Top Stories Panel -->
        <div
          v-show="activeTab === 'top5'"
          id="panel-top5"
          role="tabpanel"
          aria-labelledby="tab-top5"
        >
          <TopStoriesSection />
        </div>

        <!-- Papers Panel -->
        <div
          v-show="activeTab === 'papers'"
          id="panel-papers"
          role="tabpanel"
          aria-labelledby="tab-papers"
        >
          <PapersSection />
        </div>

        <!-- Models Panel -->
        <div
          v-show="activeTab === 'models'"
          id="panel-models"
          role="tabpanel"
          aria-labelledby="tab-models"
        >
          <ModelsSection />
        </div>

        <!-- Radar Panel -->
        <div
          v-show="activeTab === 'radar'"
          id="panel-radar"
          role="tabpanel"
          aria-labelledby="tab-radar"
        >
          <RadarSection />
        </div>
      </div>
    </template>
  </div>
</template>
