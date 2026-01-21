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
  <div class="min-h-screen flex flex-col bg-[var(--color-surface-base)]">
    <TheHeader />
    <main class="flex-1">
      <div class="container-app py-6 sm:py-8">
        <RouterView />
      </div>
    </main>
    <TheFooter />
  </div>
</template>
