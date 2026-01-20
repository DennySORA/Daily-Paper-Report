<script setup lang="ts">
  import SkeletonCard from './SkeletonCard.vue'

  interface Props {
    cardCount?: number
    showRanks?: boolean
  }

  withDefaults(defineProps<Props>(), {
    cardCount: 3,
    showRanks: false,
  })
</script>

<template>
  <div
    class="space-y-4"
    data-testid="skeleton-section"
  >
    <!-- Section header skeleton -->
    <div class="mb-6 animate-pulse">
      <div class="flex items-center gap-3 mb-3">
        <div class="w-11 h-11 rounded-xl bg-[var(--color-surface-tertiary)]" />
        <div class="h-6 bg-[var(--color-surface-tertiary)] rounded-md w-40" />
      </div>
      <div class="h-4 bg-[var(--color-surface-tertiary)] rounded w-3/4 ml-14" />
    </div>

    <!-- Cards skeleton -->
    <div class="space-y-3">
      <SkeletonCard
        v-for="i in cardCount"
        :key="i"
        :show-rank="showRanks"
      />
    </div>
  </div>
</template>
