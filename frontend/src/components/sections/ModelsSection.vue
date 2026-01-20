<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import { SECTION_CONFIGS } from '@/types/digest'
  import SectionHeader from '@/components/ui/SectionHeader.vue'
  import StoryCard from '@/components/ui/StoryCard.vue'
  import EmptyState from '@/components/ui/EmptyState.vue'

  const digestStore = useDigestStore()
  const modelReleases = computed(() => digestStore.modelReleases)
  const hasModels = computed(() => digestStore.hasModelReleases)
  const config = SECTION_CONFIGS.models
</script>

<template>
  <section
    class="mb-10"
    data-testid="section-models"
  >
    <SectionHeader :config="config" />

    <div
      v-if="hasModels"
      class="space-y-6"
    >
      <div
        v-for="(stories, entityId) in modelReleases"
        :key="entityId"
        class="bg-[var(--color-surface-secondary)] rounded-xl p-4"
      >
        <div class="flex items-center gap-2 mb-3 pb-3 border-b border-[var(--color-border-light)]">
          <span
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-[var(--color-accent-models)]/10 text-[var(--color-accent-models)]"
          >
            🤖
          </span>
          <h3 class="font-medium text-[var(--color-text-primary)]">
            {{ entityId }}
          </h3>
        </div>

        <div class="space-y-2">
          <StoryCard
            v-for="story in stories"
            :key="story.story_id"
            :story="story"
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
  </section>
</template>
