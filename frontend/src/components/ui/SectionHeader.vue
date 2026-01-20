<script setup lang="ts">
  import type { SectionConfig } from '@/types/digest'

  interface Props {
    config: SectionConfig
  }

  defineProps<Props>()

  const accentColorClasses: Record<string, string> = {
    amber:
      'bg-[var(--color-accent-top5)]/10 text-[var(--color-accent-top5)] border-[var(--color-accent-top5)]',
    purple:
      'bg-[var(--color-accent-papers)]/10 text-[var(--color-accent-papers)] border-[var(--color-accent-papers)]',
    cyan: 'bg-[var(--color-accent-models)]/10 text-[var(--color-accent-models)] border-[var(--color-accent-models)]',
    emerald:
      'bg-[var(--color-accent-radar)]/10 text-[var(--color-accent-radar)] border-[var(--color-accent-radar)]',
  }
</script>

<template>
  <div class="mb-6 animate-fade-in-up">
    <div class="flex items-center gap-3 mb-2">
      <span
        class="w-10 h-10 flex items-center justify-center rounded-xl text-lg"
        :class="accentColorClasses[config.accentColor]"
        aria-hidden="true"
      >
        {{ config.icon }}
      </span>
      <h2
        class="text-xl font-semibold tracking-tight"
        :style="{
          color: `var(--color-accent-${config.accentColor === 'amber' ? 'top5' : config.accentColor === 'purple' ? 'papers' : config.accentColor === 'cyan' ? 'models' : 'radar'})`,
        }"
        :data-testid="`section-title-${config.type}`"
      >
        {{ config.title }}
      </h2>
    </div>
    <p
      class="text-sm text-[var(--color-text-muted)] leading-relaxed pl-13 border-l-2 ml-5"
      :class="`border-[var(--color-accent-${config.accentColor === 'amber' ? 'top5' : config.accentColor === 'purple' ? 'papers' : config.accentColor === 'cyan' ? 'models' : 'radar'})]`"
      style="padding-left: 1.25rem"
    >
      {{ config.description }}
    </p>
  </div>
</template>
