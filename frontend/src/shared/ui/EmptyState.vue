<script setup lang="ts">
interface Props {
  title: string
  description?: string
  icon?: string
}

withDefaults(defineProps<Props>(), {
  description: undefined,
  icon: '📭',
})
</script>

<template>
  <div class="empty-state">
    <div class="empty-state-icon">
      {{ icon }}
    </div>
    <h3 class="empty-state-title">
      {{ title }}
    </h3>
    <p
      v-if="description"
      class="empty-state-desc"
    >
      {{ description }}
    </p>
    <slot />
  </div>
</template>
