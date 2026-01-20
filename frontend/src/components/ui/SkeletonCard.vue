<script setup lang="ts">
  interface Props {
    showRank?: boolean
  }

  withDefaults(defineProps<Props>(), {
    showRank: false,
  })
</script>

<template>
  <div
    class="card p-5 animate-pulse"
    data-testid="skeleton-card"
  >
    <div class="flex items-start gap-4">
      <!-- Rank skeleton -->
      <div
        v-if="showRank"
        class="flex-shrink-0 w-9 h-9 rounded-full bg-[var(--color-surface-tertiary)]"
      />

      <div class="flex-1 space-y-3">
        <!-- Title skeleton -->
        <div class="h-5 bg-[var(--color-surface-tertiary)] rounded-md w-3/4" />

        <!-- Meta skeleton -->
        <div class="flex items-center gap-2">
          <div class="h-4 bg-[var(--color-surface-tertiary)] rounded w-24" />
          <div class="h-4 bg-[var(--color-surface-tertiary)] rounded w-16" />
        </div>
      </div>
    </div>
  </div>
</template>
