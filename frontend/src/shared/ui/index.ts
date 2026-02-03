/**
 * Shared UI primitives barrel export
 *
 * These are lightweight, reusable UI primitives that leverage
 * the design system classes defined in main.css.
 *
 * Note: For feature-specific components with more complex styling,
 * see @/components/ui which contains richer implementations.
 */
export { default as Badge } from './Badge.vue'
export { default as Card } from './Card.vue'
export { default as Skeleton } from './Skeleton.vue'
export { default as EmptyState } from './EmptyState.vue'

// Re-export icons from components for convenience
export * from '@/components/icons'
