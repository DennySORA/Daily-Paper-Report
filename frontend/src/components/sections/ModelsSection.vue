<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import { SECTION_CONFIGS } from '@/types/digest'
  import SectionHeader from '@/components/ui/SectionHeader.vue'
  import StoryCard from '@/components/ui/StoryCard.vue'
  import EmptyState from '@/components/ui/EmptyState.vue'
  import { IconCpu } from '@/components/icons'

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
        class="bg-[var(--color-surface-secondary)] rounded-xl p-5 border border-[var(--color-border-light)] transition-all duration-[var(--duration-base)] hover:border-[var(--color-border-default)]"
      >
        <div class="flex items-center gap-3 mb-4 pb-4 border-b border-[var(--color-border-light)]">
          <span
            class="w-9 h-9 flex items-center justify-center rounded-lg bg-[var(--color-accent-models)]/15 text-[var(--color-accent-models)]"
          >
            <IconCpu :size="18" />
          </span>
          <h3 class="font-semibold text-[var(--color-text-primary)]">
            {{ entityId }}
          </h3>
        </div>

        <div class="space-y-3">
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
