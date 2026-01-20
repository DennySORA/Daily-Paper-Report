<script setup lang="ts">
  import { computed } from 'vue'
  import { useRoute } from 'vue-router'
  import { useDigestStore } from '@/stores/digest'
  import { IconBook } from '@/components/icons'

  const digestStore = useDigestStore()
  const route = useRoute()
  const runDate = computed(() => digestStore.runDate)

  const navLinks = [
    { to: '/', label: 'Today', testId: 'today' },
    { to: '/archive', label: 'Archive', testId: 'archive' },
    { to: '/sources', label: 'Sources', testId: 'sources' },
    { to: '/status', label: 'Status', testId: 'status' },
  ]

  const isActiveRoute = (to: string) => {
    if (to === '/') {
      return route.path === '/' || route.path.startsWith('/day/')
    }
    return route.path === to
  }
</script>

<template>
  <header
    class="sticky top-0 z-50 bg-[var(--color-surface-elevated)]/90 backdrop-blur-md border-b border-[var(--color-border-light)]"
  >
    <div class="max-w-4xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-14">
        <RouterLink
          to="/"
          class="flex items-center gap-2.5 group focus-ring rounded-lg"
          data-testid="logo-link"
        >
          <span
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-[var(--color-primary-100)] text-[var(--color-primary-600)] group-hover:bg-[var(--color-primary-200)] transition-colors duration-[var(--duration-fast)]"
          >
            <IconBook :size="18" />
          </span>
          <div class="flex flex-col">
            <span
              class="text-sm font-semibold text-[var(--color-text-primary)] group-hover:text-[var(--color-primary-600)] transition-colors duration-[var(--duration-fast)]"
            >
              Daily Paper Report
            </span>
            <span
              v-if="runDate"
              class="text-[10px] text-[var(--color-text-muted)] -mt-0.5"
            >
              {{ runDate }}
            </span>
          </div>
        </RouterLink>

        <nav class="flex items-center gap-0.5">
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="px-3 py-1.5 text-[13px] font-medium rounded-md transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-primary-500)] focus-visible:outline-offset-2"
            :class="[
              isActiveRoute(link.to)
                ? 'text-[var(--color-primary-600)] bg-[var(--color-primary-50)]'
                : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-tertiary)]',
            ]"
            :data-testid="`nav-${link.testId}`"
          >
            {{ link.label }}
          </RouterLink>
        </nav>
      </div>
    </div>
  </header>
</template>
