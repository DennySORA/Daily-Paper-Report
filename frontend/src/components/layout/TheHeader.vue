<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'

  const digestStore = useDigestStore()
  const runDate = computed(() => digestStore.runDate)
</script>

<template>
  <header
    class="sticky top-0 z-50 bg-[var(--color-surface-elevated)]/95 backdrop-blur-sm border-b border-[var(--color-border-light)]"
  >
    <div class="max-w-4xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-16">
        <RouterLink
          to="/"
          class="flex items-center gap-3 group"
          data-testid="logo-link"
        >
          <span
            class="text-2xl"
            aria-hidden="true"
          >📚</span>
          <div class="flex flex-col">
            <span
              class="font-semibold text-[var(--color-text-primary)] group-hover:text-[var(--color-primary-600)] transition-colors duration-[var(--duration-fast)]"
            >
              Daily Paper Report
            </span>
            <span
              v-if="runDate"
              class="text-xs text-[var(--color-text-muted)]"
            >
              {{ runDate }}
            </span>
          </div>
        </RouterLink>

        <nav class="flex items-center gap-1">
          <RouterLink
            v-for="link in [
              { to: '/', label: 'Today' },
              { to: '/archive', label: 'Archive' },
              { to: '/sources', label: 'Sources' },
              { to: '/status', label: 'Status' },
            ]"
            :key="link.to"
            :to="link.to"
            class="px-3 py-2 text-sm font-medium text-[var(--color-text-secondary)] rounded-lg hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-tertiary)] transition-all duration-[var(--duration-fast)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] focus-visible:outline-offset-2"
            :data-testid="`nav-${link.label.toLowerCase()}`"
          >
            {{ link.label }}
          </RouterLink>
        </nav>
      </div>
    </div>
  </header>
</template>
