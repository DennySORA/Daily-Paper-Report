<script setup lang="ts">
  import { IconInbox } from '@/components/icons'

  interface Props {
    title: string
    description?: string
  }

  withDefaults(defineProps<Props>(), {
    description: undefined,
  })
</script>

<template>
  <div
    class="flex flex-col items-center justify-center py-14 px-6 bg-[var(--color-surface-secondary)] border border-dashed border-[var(--color-border-default)] rounded-xl text-center animate-fade-in-scale transition-all duration-[var(--duration-base)] hover:border-[var(--color-border-strong)] hover:bg-[var(--color-surface-tertiary)]/50"
    data-testid="empty-state"
  >
    <span
      class="w-14 h-14 flex items-center justify-center rounded-full bg-[var(--color-surface-tertiary)] text-[var(--color-text-subtle)] mb-4 animate-float"
    >
      <IconInbox :size="28" />
    </span>
    <p class="text-[var(--color-text-secondary)] font-medium">
      {{ title }}
    </p>
    <p v-if="description" class="text-sm text-[var(--color-text-muted)] mt-1">
      {{ description }}
    </p>
  </div>
</template>
