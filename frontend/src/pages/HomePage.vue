<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'
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
</script>

<template>
  <div data-testid="home-page">
    <!-- Page Header -->
    <div class="mb-8 animate-fade-in-up">
      <h1 class="text-2xl font-bold text-[var(--color-text-primary)] tracking-tight">
        Daily Digest
      </h1>
      <p
        v-if="runDate"
        class="text-[var(--color-text-muted)] mt-1"
      >
        {{ runDate }} ·
        <RouterLink
          :to="`/day/${runDate}`"
          class="text-[var(--color-primary-600)] hover:text-[var(--color-primary-700)] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] focus-visible:outline-offset-2 rounded transition-colors duration-[var(--duration-fast)]"
        >
          Permanent link
        </RouterLink>
      </p>
      <p
        v-else-if="isLoading"
        class="h-5 bg-[var(--color-surface-tertiary)] rounded w-32 mt-1 animate-pulse"
      />
    </div>

    <!-- Loading State with Skeleton -->
    <div
      v-if="isLoading"
      class="space-y-10"
      data-testid="loading-state"
    >
      <SkeletonSection
        :card-count="5"
        :show-ranks="true"
      />
      <SkeletonSection :card-count="2" />
      <SkeletonSection :card-count="3" />
      <SkeletonSection :card-count="2" />
    </div>

    <!-- Error State -->
    <div
      v-else-if="hasError"
      class="bg-[var(--color-error)]/10 border border-[var(--color-error)]/20 rounded-xl p-6 text-center animate-fade-in"
      data-testid="error-state"
    >
      <p class="text-[var(--color-error)] font-medium">
        Failed to load digest
      </p>
      <p class="text-sm text-[var(--color-text-muted)] mt-1">
        {{ errorMessage }}
      </p>
      <button
        class="mt-4 px-4 py-2 bg-[var(--color-primary-600)] text-white rounded-lg font-medium hover:bg-[var(--color-primary-700)] active:bg-[var(--color-primary-800)] transition-all duration-[var(--duration-fast)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] focus-visible:outline-offset-2 active:scale-[0.98]"
        data-testid="retry-button"
        @click="digestStore.fetchDigest()"
      >
        Retry
      </button>
    </div>

    <!-- Content -->
    <template v-else>
      <TopStoriesSection />
      <ModelsSection />
      <PapersSection />
      <RadarSection />
    </template>
  </div>
</template>
