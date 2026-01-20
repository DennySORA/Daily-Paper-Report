<script setup lang="ts">
  import { computed } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import { SECTION_CONFIGS } from '@/types/digest'
  import SectionHeader from '@/components/ui/SectionHeader.vue'
  import StoryCard from '@/components/ui/StoryCard.vue'
  import EmptyState from '@/components/ui/EmptyState.vue'

  const digestStore = useDigestStore()
  const stories = computed(() => digestStore.papers)
  const config = SECTION_CONFIGS.papers
</script>

<template>
  <section class="mb-10" data-testid="section-papers">
    <SectionHeader :config="config" />

    <div v-if="stories.length > 0" class="space-y-3">
      <StoryCard
        v-for="story in stories"
        :key="story.story_id"
        :story="story"
        :show-arxiv="true"
        accent-class="accent-papers"
      />
    </div>

    <EmptyState v-else title="No new papers today" description="Check back tomorrow!" />
  </section>
</template>
