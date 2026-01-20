<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import TopStoriesSection from '@/components/sections/TopStoriesSection.vue'
  import PapersSection from '@/components/sections/PapersSection.vue'
  import ModelsSection from '@/components/sections/ModelsSection.vue'
  import RadarSection from '@/components/sections/RadarSection.vue'

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
          class="text-[var(--color-primary-600)] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] focus-visible:outline-offset-2 rounded"
        >
          Permanent link
        </RouterLink>
      </p>
    </div>

    <!-- Loading State -->
    <div
      v-if="isLoading"
      class="flex items-center justify-center py-20"
      data-testid="loading-state"
    >
      <div class="flex flex-col items-center gap-4">
        <div
          class="w-10 h-10 border-3 border-[var(--color-primary-200)] border-t-[var(--color-primary-600)] rounded-full animate-spin"
        />
        <p class="text-[var(--color-text-muted)]">
          Loading digest...
        </p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="hasError"
      class="bg-[var(--color-error)]/10 border border-[var(--color-error)]/20 rounded-xl p-6 text-center"
      data-testid="error-state"
    >
      <p class="text-[var(--color-error)] font-medium">
        Failed to load digest
      </p>
      <p class="text-sm text-[var(--color-text-muted)] mt-1">
        {{ errorMessage }}
      </p>
      <button
        class="mt-4 px-4 py-2 bg-[var(--color-primary-600)] text-white rounded-lg font-medium hover:bg-[var(--color-primary-700)] transition-colors duration-[var(--duration-fast)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] focus-visible:outline-offset-2"
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
