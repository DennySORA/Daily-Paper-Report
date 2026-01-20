<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'

  const digestStore = useDigestStore()
  const sources = computed(() => digestStore.sourcesStatus)

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'HAS_UPDATE':
        return 'bg-[var(--color-success)]/10 text-[var(--color-success)]'
      case 'NO_UPDATE':
        return 'bg-[var(--color-info)]/10 text-[var(--color-info)]'
      case 'FETCH_FAILED':
      case 'PARSE_FAILED':
        return 'bg-[var(--color-error)]/10 text-[var(--color-error)]'
      default:
        return 'bg-[var(--color-warning)]/10 text-[var(--color-warning)]'
    }
  }

  const getStatusLabel = (status: string): string => {
    switch (status) {
      case 'HAS_UPDATE':
        return 'Updated'
      case 'NO_UPDATE':
        return 'No Changes'
      case 'FETCH_FAILED':
        return 'Fetch Failed'
      case 'PARSE_FAILED':
        return 'Parse Failed'
      default:
        return status
    }
  }

  const getTierLabel = (tier: number): string => {
    switch (tier) {
      case 0:
        return 'Primary'
      case 1:
        return 'Secondary'
      default:
        return 'Tertiary'
    }
  }
</script>

<template>
  <div data-testid="sources-page">
    <div class="mb-8 animate-fade-in-up">
      <h1 class="text-2xl font-bold text-[var(--color-text-primary)] tracking-tight">Sources</h1>
      <p class="text-[var(--color-text-muted)] mt-1">Data sources and their current status</p>
    </div>

    <div v-if="sources.length > 0" class="space-y-3">
      <div
        v-for="(source, index) in sources"
        :key="source.source_id"
        class="card p-4 animate-fade-in-up hover-lift"
        :class="`stagger-${Math.min(index + 1, 5)}`"
        :data-testid="`source-card-${source.source_id}`"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <h3 class="font-medium text-[var(--color-text-primary)]">
                {{ source.name }}
              </h3>
              <span
                class="px-2 py-0.5 text-xs font-medium rounded-full transition-all duration-[var(--duration-fast)] hover:scale-105"
                :class="getStatusColor(source.status)"
              >
                {{ getStatusLabel(source.status) }}
              </span>
            </div>

            <div class="flex flex-wrap items-center gap-2 text-sm text-[var(--color-text-muted)]">
              <span
                class="px-2 py-0.5 bg-[var(--color-surface-tertiary)] rounded text-xs font-medium transition-colors duration-[var(--duration-fast)] hover:bg-[var(--color-primary-50)] hover:text-[var(--color-primary-600)]"
              >
                {{ source.method }}
              </span>
              <span class="text-[var(--color-border-strong)]">·</span>
              <span>{{ getTierLabel(source.tier) }}</span>
              <template v-if="source.items_new > 0">
                <span class="text-[var(--color-border-strong)]">·</span>
                <span class="text-[var(--color-success)]">+{{ source.items_new }} new</span>
              </template>
            </div>

            <p v-if="source.reason_text" class="text-sm text-[var(--color-text-subtle)] mt-2">
              {{ source.reason_text }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <div
      v-else
      class="flex flex-col items-center justify-center py-20 bg-[var(--color-surface-secondary)] rounded-xl border border-dashed border-[var(--color-border-default)] animate-fade-in-scale transition-all duration-[var(--duration-base)] hover:border-[var(--color-border-strong)]"
    >
      <span class="text-5xl mb-4 animate-float" aria-hidden="true">📡</span>
      <p class="text-[var(--color-text-secondary)] font-medium">No source data available</p>
    </div>
  </div>
</template>
