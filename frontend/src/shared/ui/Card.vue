<script setup lang="ts">
interface Props {
  featured?: boolean
  accent?: 'highlight' | 'papers' | 'models' | 'sources' | 'radar'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  featured: false,
  accent: undefined,
  padding: 'md',
})

const paddingClasses: Record<string, string> = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-5',
}
</script>

<template>
  <div
    class="card"
    :class="[
      props.featured && 'card-featured',
      props.accent && `card-accent card-accent-${props.accent}`,
      paddingClasses[props.padding],
    ]"
  >
    <slot />
  </div>
</template>
