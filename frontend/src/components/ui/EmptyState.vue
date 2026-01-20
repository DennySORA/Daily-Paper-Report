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
    class="relative flex flex-col items-center justify-center py-12 px-6 bg-[var(--color-surface-secondary)]/60 border border-[var(--color-border-light)] rounded-xl text-center animate-fade-in-scale transition-all duration-[var(--duration-base)] hover:bg-[var(--color-surface-secondary)] group overflow-hidden"
    data-testid="empty-state"
  >
    <!-- Subtle background pattern -->
    <div
      class="absolute inset-0 opacity-[0.02] pointer-events-none"
      style="
        background-image: radial-gradient(circle at 1px 1px, currentColor 1px, transparent 1px);
        background-size: 24px 24px;
      "
    />

    <span
      class="relative w-12 h-12 flex items-center justify-center rounded-xl bg-[var(--color-surface-tertiary)] text-[var(--color-text-subtle)] mb-4 transition-all duration-[var(--duration-slow)] ease-[var(--ease-spring)] group-hover:scale-105 group-hover:bg-[var(--color-surface-primary)]"
    >
      <IconInbox :size="24" />
    </span>
    <p class="relative text-[var(--color-text-secondary)] font-medium text-sm">
      {{ title }}
    </p>
    <p
      v-if="description"
      class="relative text-xs text-[var(--color-text-muted)] mt-1.5"
    >
      {{ description }}
    </p>
  </div>
</template>
