<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import StoryCard from '@/components/ui/StoryCard.vue'
  import EmptyState from '@/components/ui/EmptyState.vue'

  const digestStore = useDigestStore()
  const stories = computed(() => digestStore.filteredTop5)
</script>

<template>
  <div data-testid="section-top5">
    <!-- Section description -->
    <p class="text-sm text-[var(--color-text-muted)] mb-4">
      Curated selection of the most significant AI/ML developments, combining breakthrough research
      and high-impact announcements.
    </p>

    <div
      v-if="stories.length > 0"
      class="space-y-3"
    >
      <StoryCard
        v-for="(story, index) in stories"
        :key="story.story_id"
        :story="story"
        :rank="index + 1"
        :show-entities="true"
        :show-summary="true"
        accent-class="accent-top5"
      />
    </div>

    <EmptyState
      v-else
      title="No top stories today"
      description="Check back tomorrow!"
    />
  </div>
</template>
