<script setup lang="ts">
  import { IconStar, IconDocument, IconCpu, IconGlobe } from '@/components/icons'

  export interface Tab {
    id: string
    label: string
    count: number
    icon: 'star' | 'document' | 'cpu' | 'globe'
  }

  interface Props {
    tabs: Tab[]
    activeTab: string
  }

  interface Emits {
    (e: 'update:activeTab', value: string): void
  }

  defineProps<Props>()
  const emit = defineEmits<Emits>()

  const iconComponents = {
    star: IconStar,
    document: IconDocument,
    cpu: IconCpu,
    globe: IconGlobe,
  }

  const handleTabClick = (tabId: string) => {
    emit('update:activeTab', tabId)
  }
</script>

<template>
  <nav
    class="tab-bar overflow-x-auto"
    role="tablist"
    aria-label="Content sections"
  >
    <button
      v-for="tab in tabs"
      :key="tab.id"
      :data-tab="tab.id"
      role="tab"
      :aria-selected="activeTab === tab.id"
      :aria-controls="`panel-${tab.id}`"
      :class="['tab-button', { active: activeTab === tab.id }]"
      @click="handleTabClick(tab.id)"
    >
      <component
        :is="iconComponents[tab.icon]"
        :size="16"
        class="flex-shrink-0 opacity-70"
      />
      <span>{{ tab.label }}</span>
      <span class="tab-badge">{{ tab.count }}</span>
    </button>
  </nav>
</template>
