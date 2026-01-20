import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DigestData, Story, SourceStatus } from '@/types/digest'

export const useDigestStore = defineStore('digest', () => {
  // State
  const data = ref<DigestData | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const timeFilter = ref<'all' | '24h'>('all')

  // Getters
  const hasData = computed(() => data.value !== null)

  const top5 = computed(() => data.value?.top5 ?? [])

  const papers = computed(() => data.value?.papers ?? [])

  const modelReleases = computed(() => data.value?.model_releases_by_entity ?? {})

  const hasModelReleases = computed(() => Object.keys(modelReleases.value).length > 0)

  const radar = computed(() => data.value?.radar ?? [])

  const sourcesStatus = computed(() => data.value?.sources_status ?? [])

  const runDate = computed(() => data.value?.run_date ?? '')

  const runInfo = computed(() => data.value?.run_info ?? null)

  const totalStories = computed(() => {
    if (!data.value) return 0
    const modelStoriesCount = Object.values(data.value.model_releases_by_entity).reduce(
      (sum, stories) => sum + stories.length,
      0,
    )
    return (
      data.value.top5.length +
      data.value.papers.length +
      modelStoriesCount +
      data.value.radar.length
    )
  })

  // Group papers by category (arXiv category or first category tag)
  const papersByCategory = computed(() => {
    const grouped: Record<string, Story[]> = {}
    for (const paper of papers.value) {
      const category = paper.categories?.[0] ?? 'Uncategorized'
      if (!grouped[category]) {
        grouped[category] = []
      }
      grouped[category].push(paper)
    }
    return grouped
  })

  // Get all unique categories from papers
  const paperCategories = computed(() => Object.keys(papersByCategory.value).sort())

  // Group stories by source (source_id from primary_link)
  const allStoriesBySource = computed(() => {
    const allStories = [
      ...top5.value,
      ...papers.value,
      ...radar.value,
      ...Object.values(modelReleases.value).flat(),
    ]

    const grouped: Record<string, Story[]> = {}
    for (const story of allStories) {
      const sourceId = story.primary_link.source_id
      if (!grouped[sourceId]) {
        grouped[sourceId] = []
      }
      grouped[sourceId].push(story)
    }
    return grouped
  })

  // Get source names from sources_status
  const sourceNames = computed(() => {
    const names: Record<string, string> = {}
    for (const source of sourcesStatus.value) {
      names[source.source_id] = source.name
    }
    return names
  })

  // Get all unique source IDs with stories
  const sourceIdsWithStories = computed(() => Object.keys(allStoriesBySource.value).sort())

  // Filter stories within last 24 hours (based on report generation time, not current time)
  // Uses first_seen_at (when crawler first saw the item) for accurate filtering
  const storiesLast24Hours = computed(() => {
    // Use report generation time as baseline, fallback to current time
    const baseTime = runInfo.value?.finished_at
      ? new Date(runInfo.value.finished_at)
      : new Date()
    const cutoff = new Date(baseTime.getTime() - 24 * 60 * 60 * 1000)

    const filterRecent = (stories: Story[]) =>
      stories.filter((s) => {
        // Use first_seen_at (crawler discovery time) as primary filter
        // Fall back to published_at if first_seen_at is not available
        const timeStr = s.first_seen_at || s.published_at
        if (!timeStr) return false
        return new Date(timeStr) >= cutoff
      })

    return {
      top5: filterRecent(top5.value),
      papers: filterRecent(papers.value),
      radar: filterRecent(radar.value),
      modelReleases: Object.fromEntries(
        Object.entries(modelReleases.value).map(([key, stories]) => [key, filterRecent(stories)]),
      ),
    }
  })

  // Filtered getters based on time filter setting
  const filteredTop5 = computed(() =>
    timeFilter.value === '24h' ? storiesLast24Hours.value.top5 : top5.value,
  )

  const filteredPapers = computed(() =>
    timeFilter.value === '24h' ? storiesLast24Hours.value.papers : papers.value,
  )

  const filteredRadar = computed(() =>
    timeFilter.value === '24h' ? storiesLast24Hours.value.radar : radar.value,
  )

  const filteredModelReleases = computed(() =>
    timeFilter.value === '24h' ? storiesLast24Hours.value.modelReleases : modelReleases.value,
  )

  // Filtered papers by category
  const filteredPapersByCategory = computed(() => {
    const papersToGroup = filteredPapers.value
    const grouped: Record<string, Story[]> = {}
    for (const paper of papersToGroup) {
      const category = paper.categories?.[0] ?? 'Uncategorized'
      if (!grouped[category]) {
        grouped[category] = []
      }
      grouped[category].push(paper)
    }
    return grouped
  })

  const filteredPaperCategories = computed(() => Object.keys(filteredPapersByCategory.value).sort())

  // Filtered total count
  const filteredTotalStories = computed(() => {
    const modelStoriesCount = Object.values(filteredModelReleases.value).reduce(
      (sum, stories) => sum + stories.length,
      0,
    )
    return (
      filteredTop5.value.length +
      filteredPapers.value.length +
      modelStoriesCount +
      filteredRadar.value.length
    )
  })

  // Action to toggle time filter
  function setTimeFilter(filter: 'all' | '24h'): void {
    timeFilter.value = filter
  }

  // Get sources grouped by status
  const sourcesByStatus = computed(() => {
    const healthy: SourceStatus[] = []
    const failed: SourceStatus[] = []
    const noUpdate: SourceStatus[] = []

    for (const source of sourcesStatus.value) {
      if (source.status === 'HAS_UPDATE') {
        healthy.push(source)
      } else if (source.status === 'FETCH_FAILED' || source.status === 'PARSE_FAILED') {
        failed.push(source)
      } else {
        noUpdate.push(source)
      }
    }

    return { healthy, failed, noUpdate }
  })

  // Actions
  async function fetchDigest(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/daily.json')
      if (!response.ok) {
        throw new Error(`Failed to fetch digest: ${response.status} ${response.statusText}`)
      }
      data.value = await response.json()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error occurred'
      console.error('Failed to fetch digest:', err)
    } finally {
      isLoading.value = false
    }
  }

  function setData(newData: DigestData): void {
    data.value = newData
  }

  function getStoriesByEntity(entityId: string): Story[] {
    return modelReleases.value[entityId] ?? []
  }

  return {
    // State
    data,
    isLoading,
    error,
    timeFilter,
    // Getters
    hasData,
    top5,
    papers,
    modelReleases,
    hasModelReleases,
    radar,
    sourcesStatus,
    runDate,
    runInfo,
    totalStories,
    // New grouping getters
    papersByCategory,
    paperCategories,
    allStoriesBySource,
    sourceNames,
    sourceIdsWithStories,
    storiesLast24Hours,
    sourcesByStatus,
    // Filtered getters (based on time filter)
    filteredTop5,
    filteredPapers,
    filteredRadar,
    filteredModelReleases,
    filteredPapersByCategory,
    filteredPaperCategories,
    filteredTotalStories,
    // Actions
    fetchDigest,
    setData,
    getStoriesByEntity,
    setTimeFilter,
  }
})
