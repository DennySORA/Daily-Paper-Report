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
  <div class="mb-6 animate-fade-in-up">
    <div class="flex items-center gap-3 mb-3">
      <span
        class="w-11 h-11 flex items-center justify-center rounded-xl transition-all duration-[var(--duration-base)]"
        :style="{
          backgroundColor: `color-mix(in oklch, var(${accentVar}), transparent 85%)`,
          color: `var(${accentVar})`,
        }"
      >
        <component
          :is="IconComponent"
          :size="22"
        />
      </span>
      <h2
        class="text-xl font-semibold tracking-tight"
        :style="{ color: `var(${accentVar})` }"
        :data-testid="`section-title-${config.type}`"
      >
        {{ config.title }}
      </h2>
    </div>
    <p
      class="text-sm text-[var(--color-text-muted)] leading-relaxed pl-14 border-l-2 transition-colors duration-[var(--duration-base)]"
      :style="{ borderColor: `color-mix(in oklch, var(${accentVar}), transparent 60%)` }"
    >
      {{ config.description }}
    </p>
  </div>
</template>
