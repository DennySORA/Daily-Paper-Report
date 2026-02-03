<script setup lang="ts">
interface Props {
  variant?:
    | 'default'
    | 'muted'
    | 'highlight'
    | 'papers'
    | 'models'
    | 'sources'
    | 'radar'
    | 'top-pick'
    | 'source-arxiv'
    | 'source-hf'
    | 'source-blog'
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
})

const variantClasses: Record<string, string> = {
  default: 'badge-muted',
  muted: 'badge-muted',
  highlight: 'badge-highlight',
  papers: 'badge-papers',
  models: 'badge-models',
  sources: 'badge-sources',
  radar: 'badge-radar',
  'top-pick': 'badge-top-pick',
  'source-arxiv': 'badge-source-arxiv',
  'source-hf': 'badge-source-hf',
  'source-blog': 'badge-source-blog',
}

const sizeClasses: Record<string, string> = {
  sm: 'text-[0.625rem] py-0.5 px-2',
  md: '',
}
</script>

<template>
  <span
    class="badge"
    :class="[variantClasses[props.variant], sizeClasses[props.size]]"
  >
    <slot />
  </span>
</template>
