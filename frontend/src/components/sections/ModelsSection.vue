<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import StoryCard from '@/components/ui/StoryCard.vue'
  import EmptyState from '@/components/ui/EmptyState.vue'
  import { IconCpu } from '@/components/icons'

  const digestStore = useDigestStore()
  const modelReleases = computed(() => digestStore.filteredModelReleases)
  const hasModels = computed(() => Object.keys(modelReleases.value).length > 0)

  // Format entity name for display
  const formatEntityName = (entityId: string): string => {
    return entityId
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }
</script>

<template>
  <div data-testid="section-models">
    <!-- Section description -->
    <p class="text-sm text-[var(--color-text-muted)] mb-4">
      New model releases and updates from leading AI labs and the open-source community.
    </p>

    <div
      v-if="hasModels"
      class="space-y-6"
    >
      <div
        v-for="(stories, entityId) in modelReleases"
        :key="entityId"
        class="bg-[var(--color-surface-secondary)] rounded-xl p-5 border border-[var(--color-border-light)]"
      >
        <!-- Entity header -->
        <div class="flex items-center gap-3 mb-4 pb-3 border-b border-[var(--color-border-light)]">
          <span
            class="w-10 h-10 flex items-center justify-center rounded-lg bg-[var(--color-accent-models)]/15 text-[var(--color-accent-models)]"
          >
            <IconCpu :size="20" />
          </span>
          <div>
            <h3
              class="font-semibold text-[var(--color-text-primary)]"
              style="font-family: var(--font-display)"
            >
              {{ formatEntityName(entityId) }}
            </h3>
            <p class="text-xs text-[var(--color-text-muted)]">
              {{ stories.length }} release{{ stories.length !== 1 ? 's' : '' }}
            </p>
          </div>
        </div>

        <!-- Model cards -->
        <div class="space-y-3">
          <StoryCard
            v-for="story in stories"
            :key="story.story_id"
            :story="story"
            :show-summary="true"
            :show-authors="true"
            accent-class="accent-models"
          />
        </div>
      </div>
    </div>

    <EmptyState
      v-else
      title="No new model releases today"
      description="Check back tomorrow!"
    />
  </div>
</template>
