import { ref, computed, type Ref } from 'vue'
import type { Story } from '@/shared/types'

/**
 * Check if a story matches a search query
 */
export function matchesSearch(story: Story, query: string): boolean {
  if (!query.trim()) return true
  const lowerQuery = query.toLowerCase()
  const titleMatch = story.title.toLowerCase().includes(lowerQuery)
  const authorMatch =
    story.authors?.some((a) => a.toLowerCase().includes(lowerQuery)) ?? false
  const summaryMatch = story.summary?.toLowerCase().includes(lowerQuery) ?? false
  return titleMatch || authorMatch || summaryMatch
}

/**
 * Filter stories by search query
 */
export function filterStoriesBySearch(stories: Story[], query: string): Story[] {
  if (!query.trim()) return stories
  return stories.filter((story) => matchesSearch(story, query))
}

/**
 * Composable for search functionality with reactive state
 */
export function useSearch(initialQuery = '') {
  const searchQuery: Ref<string> = ref(initialQuery)
  const isSearchFocused = ref(false)

  const hasQuery = computed(() => searchQuery.value.trim().length > 0)

  function clearSearch(): void {
    searchQuery.value = ''
  }

  function setFocus(focused: boolean): void {
    isSearchFocused.value = focused
  }

  return {
    searchQuery,
    isSearchFocused,
    hasQuery,
    clearSearch,
    setFocus,
    matchesSearch,
    filterStoriesBySearch,
  }
}
