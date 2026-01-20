<script setup lang="ts">
  import { onMounted } from 'vue'
  import { useDigestStore } from '@/stores/digest'
  import TheHeader from '@/components/layout/TheHeader.vue'
  import TheFooter from '@/components/layout/TheFooter.vue'

  const digestStore = useDigestStore()

  onMounted(async () => {
    await digestStore.fetchDigest()
  })
</script>

<template>
  <div class="min-h-screen flex flex-col bg-[var(--color-surface-primary)]">
    <TheHeader />
    <main class="flex-1">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        <RouterView />
      </div>
    </main>
    <TheFooter />
  </div>
</template>
