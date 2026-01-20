<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import { IconBook } from '@/components/icons'

  const digestStore = useDigestStore()
  const runInfo = computed(() => digestStore.runInfo)

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return 'N/A'
    return new Date(dateStr).toLocaleString()
  }
</script>

<template>
  <footer
    class="border-t border-[var(--color-border-light)] bg-[var(--color-surface-secondary)] py-6"
  >
    <div class="max-w-4xl mx-auto px-4 sm:px-6">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm">
        <div
          class="flex items-center gap-2 text-[var(--color-text-muted)] transition-colors duration-[var(--duration-fast)] hover:text-[var(--color-text-secondary)]"
        >
          <IconBook
            :size="16"
            class="transition-transform duration-[var(--duration-base)] ease-[var(--ease-spring)] hover:scale-110"
          />
          <span>Daily Paper Report</span>
        </div>

        <div
          v-if="runInfo"
          class="flex items-center gap-4 text-[var(--color-text-subtle)]"
        >
          <span class="tabular-nums">Last updated: {{ formatDate(runInfo.finished_at) }}</span>
          <span
            v-if="runInfo.success"
            class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--color-success)]/10 text-[var(--color-success)] text-xs font-medium transition-all duration-[var(--duration-fast)] hover:bg-[var(--color-success)]/15"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-current animate-pulse-subtle" />
            Healthy
          </span>
        </div>
      </div>
    </div>
  </footer>
</template>
