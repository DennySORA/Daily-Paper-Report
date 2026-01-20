import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EmptyState from '../ui/EmptyState.vue'

describe('EmptyState', () => {
  it('renders with required title prop', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'No content available' },
    })

    expect(wrapper.text()).toContain('No content available')
  })

  it('renders the inbox icon', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Test title' },
    })

    // Check that an SVG icon is rendered
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('renders description when provided', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Test title', description: 'This is a description' },
    })

    expect(wrapper.text()).toContain('This is a description')
  })

  it('does not render description element when not provided', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Test title' },
    })

    // Check that only one paragraph exists (the title)
    const paragraphs = wrapper.findAll('p')
    expect(paragraphs.length).toBe(1)
  })

  it('has correct test id', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Test title' },
    })

    expect(wrapper.find('[data-testid="empty-state"]').exists()).toBe(true)
  })

  it('applies correct styling classes', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Test title' },
    })

    const container = wrapper.find('[data-testid="empty-state"]')
    expect(container.classes()).toContain('animate-fade-in-scale')
  })
})
