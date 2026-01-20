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
    class="border-t border-[var(--color-border-light)] bg-[var(--color-surface-secondary)]/50 py-4"
  >
    <div class="max-w-4xl mx-auto px-4 sm:px-6">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <div
          class="flex items-center gap-1.5 text-[var(--color-text-muted)] transition-colors duration-[var(--duration-fast)] hover:text-[var(--color-text-secondary)]"
        >
          <IconBook
            :size="14"
            class="transition-transform duration-[var(--duration-base)]"
          />
          <span>Daily Paper Report</span>
        </div>

        <div
          v-if="runInfo"
          class="flex items-center gap-3 text-[var(--color-text-subtle)]"
        >
          <span class="tabular-nums">Last updated: {{ formatDate(runInfo.finished_at) }}</span>
          <span
            v-if="runInfo.success"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[var(--color-success)]/10 text-[var(--color-success)] text-[10px] font-medium"
          >
            <span class="w-1 h-1 rounded-full bg-current animate-pulse-subtle" />
            Healthy
          </span>
        </div>
      </div>
    </div>
  </footer>
</template>
