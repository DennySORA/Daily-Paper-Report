<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import { SECTION_CONFIGS } from '@/types/digest'
  import SectionHeader from '@/components/ui/SectionHeader.vue'
  import StoryCard from '@/components/ui/StoryCard.vue'
  import EmptyState from '@/components/ui/EmptyState.vue'

  const digestStore = useDigestStore()
  const stories = computed(() => digestStore.top5)
  const config = SECTION_CONFIGS.top5
</script>

<template>
  <section class="mb-10" data-testid="section-top5">
    <SectionHeader :config="config" />

    <div v-if="stories.length > 0" class="space-y-3">
      <StoryCard
        v-for="(story, index) in stories"
        :key="story.story_id"
        :story="story"
        :rank="index + 1"
        :show-entities="true"
        accent-class="accent-top5"
      />
    </div>

    <EmptyState v-else title="No top stories today" description="Check back tomorrow!" />
  </section>
</template>
