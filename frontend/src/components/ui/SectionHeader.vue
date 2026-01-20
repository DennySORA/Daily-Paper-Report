<script setup lang="ts">
  import type { SectionConfig, IconName } from '@/types/digest'
  import { IconStar, IconDocument, IconRocket, IconRadar } from '@/components/icons'
  import { computed, type Component } from 'vue'

  interface Props {
    config: SectionConfig
  }

  const props = defineProps<Props>()

  const iconComponents: Record<IconName, Component> = {
    star: IconStar,
    document: IconDocument,
    rocket: IconRocket,
    radar: IconRadar,
    cpu: IconStar,
    inbox: IconStar,
  }

  const IconComponent = computed(() => iconComponents[props.config.iconName])

  const accentVarMap: Record<string, string> = {
    amber: '--color-accent-top5',
    purple: '--color-accent-papers',
    cyan: '--color-accent-models',
    emerald: '--color-accent-radar',
  }

  const accentVar = computed(() => accentVarMap[props.config.accentColor])
</script>

<template>
  <div class="mb-5 animate-fade-in-up group">
    <div class="flex items-center gap-3 mb-2.5">
      <span
        class="w-10 h-10 flex items-center justify-center rounded-lg transition-all duration-[var(--duration-base)] ease-[var(--ease-out)] group-hover:scale-105"
        :style="{
          backgroundColor: `color-mix(in oklch, var(${accentVar}), transparent 88%)`,
          color: `var(${accentVar})`,
        }"
      >
        <component
          :is="IconComponent"
          :size="20"
          class="transition-transform duration-[var(--duration-slow)] ease-[var(--ease-spring)]"
        />
      </span>
      <h2
        class="text-lg font-semibold tracking-tight"
        :style="{ color: `var(${accentVar})` }"
        :data-testid="`section-title-${config.type}`"
      >
        {{ config.title }}
      </h2>
    </div>
    <p
      class="text-sm text-[var(--color-text-muted)] leading-relaxed pl-[52px] border-l border-[var(--color-border-light)] transition-colors duration-[var(--duration-base)]"
    >
      {{ config.description }}
    </p>
  </div>
</template>
