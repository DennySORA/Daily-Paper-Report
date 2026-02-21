<script setup lang="ts">
interface Props {
  variant?: 'text' | 'title' | 'avatar' | 'card'
  width?: string
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'text',
  width: undefined,
  height: undefined,
})

const variantClasses: Record<string, string> = {
  text: 'h-4 rounded',
  title: 'h-6 rounded-md',
  avatar: 'w-10 h-10 rounded-full',
  card: 'h-32 rounded-lg',
}
</script>

<template>
  <div
    class="skeleton"
    :class="variantClasses[props.variant]"
    :style="{
      width: props.width,
      height: props.height,
    }"
  />
</template>
