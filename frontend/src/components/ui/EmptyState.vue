<script setup lang="ts">
  interface Props {
    icon?: string
    title: string
    description?: string
  }

  withDefaults(defineProps<Props>(), {
    icon: '📭',
    description: undefined,
  })
</script>

<template>
  <div
    class="flex flex-col items-center justify-center py-12 px-6 bg-[var(--color-surface-secondary)] border border-dashed border-[var(--color-border-default)] rounded-xl text-center animate-fade-in"
    data-testid="empty-state"
  >
    <span
      class="text-4xl mb-3 opacity-60"
      aria-hidden="true"
    >{{ icon }}</span>
    <p class="text-[var(--color-text-secondary)] font-medium">
      {{ title }}
    </p>
    <p
      v-if="description"
      class="text-sm text-[var(--color-text-muted)] mt-1"
    >
      {{ description }}
    </p>
  </div>
</template>
