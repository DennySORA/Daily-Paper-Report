<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useDigestStore } from '@/stores/digest'
import { useLanguage } from '@/shared/composables/useLanguage'
import IconGithub from '@/components/icons/IconGithub.vue'

const digestStore = useDigestStore()
const { locale, toggleLocale } = useLanguage()
const route = useRoute()
const runDate = computed(() => digestStore.runDate)

const githubRepoUrl = 'https://github.com/DennySORA/Daily-Paper-Report'

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
    class="sticky top-0 z-50 bg-[var(--color-surface-raised)]/95 backdrop-blur-lg border-b border-[var(--color-border-subtle)]"
    role="banner"
  >
    <div class="container-app">
      <div class="flex items-center justify-between h-14">
        <RouterLink
          to="/"
          class="flex items-center gap-2.5 group focus-ring rounded-lg"
          data-testid="logo-link"
          aria-label="Daily Paper Report - Home"
        >
          <span
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-[oklch(0.55_0.20_264/0.1)] text-[oklch(0.55_0.20_264)] group-hover:bg-[oklch(0.55_0.20_264/0.15)] transition-colors duration-[var(--duration-fast)]"
          >
            <svg
              class="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
          </span>
          <div class="flex flex-col">
            <span
              class="text-sm font-semibold text-[var(--color-text-primary)] group-hover:text-[oklch(0.55_0.20_264)] transition-colors duration-[var(--duration-fast)]"
              style="font-family: var(--font-display)"
            >
              Daily Paper Report
            </span>
            <span
              v-if="runDate"
              class="text-[10px] text-[var(--color-text-quaternary)] -mt-0.5"
              style="font-family: var(--font-mono)"
            >
              {{ runDate }}
            </span>
          </div>
        </RouterLink>

        <nav
          class="flex items-center gap-0.5"
          aria-label="Main navigation"
        >
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="px-3 py-1.5 text-[13px] font-medium rounded-md transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] focus-outline"
            :class="[
              isActiveRoute(link.to)
                ? 'text-[var(--color-text-inverse)] bg-[oklch(0.55_0.20_264)]'
                : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-sunken)]',
            ]"
            :data-testid="`nav-${link.testId}`"
            :aria-current="isActiveRoute(link.to) ? 'page' : undefined"
          >
            {{ link.label }}
          </RouterLink>

          <button
            class="ml-2 px-2.5 py-1 text-[11px] font-semibold rounded-full border transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] focus-outline"
            :class="[
              locale === 'zh-TW'
                ? 'bg-[oklch(0.55_0.20_264/0.15)] text-[oklch(0.70_0.15_264)] border-[oklch(0.55_0.20_264/0.3)]'
                : 'bg-transparent text-[var(--color-text-tertiary)] border-[var(--color-border-subtle)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-border-default)]',
            ]"
            :title="locale === 'en' ? 'Switch to Traditional Chinese' : 'Switch to English'"
            :aria-label="locale === 'en' ? 'Switch to Traditional Chinese' : 'Switch to English'"
            data-testid="locale-toggle"
            @click="toggleLocale"
          >
            {{ locale === 'en' ? '繁中' : 'EN' }}
          </button>

          <a
            :href="githubRepoUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="ml-1 p-2 text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-sunken)] rounded-md transition-all duration-[var(--duration-fast)] ease-[var(--ease-out)] focus-outline"
            title="View source on GitHub"
            aria-label="View source on GitHub (opens in new tab)"
            data-testid="github-link"
          >
            <IconGithub :size="18" />
          </a>
        </nav>
      </div>
    </div>
  </header>
</template>
