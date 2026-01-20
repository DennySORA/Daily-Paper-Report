import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DigestData, Story } from '@/types/digest'

export const useDigestStore = defineStore('digest', () => {
  // State
  const data = ref<DigestData | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

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
    // Actions
    fetchDigest,
    setData,
    getStoriesByEntity,
  }
})
