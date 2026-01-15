# Design Guide - Research Digest Static Site

## Overview

This document defines the visual design system for the Research Digest static HTML site. The design follows modern best practices for readability, accessibility, and responsiveness.

## Design Principles

1. **Clarity First**: Content is king. Design serves to present information clearly.
2. **Minimal Distraction**: No unnecessary decoration. Every element has purpose.
3. **Accessibility**: WCAG 2.1 AA compliant color contrast and focus states.
4. **System Adaptive**: Respects user preferences (dark mode, reduced motion).

## Color Palette

### Light Mode

| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `#2563eb` | Links, interactive elements |
| `--color-primary-hover` | `#1d4ed8` | Hover states |
| `--color-primary-light` | `#dbeafe` | Highlight backgrounds |
| `--color-bg` | `#ffffff` | Page background |
| `--color-bg-subtle` | `#f8fafc` | Cards, alternate rows |
| `--color-bg-muted` | `#f1f5f9` | Badges, code blocks |
| `--color-text` | `#0f172a` | Primary text |
| `--color-text-secondary` | `#475569` | Secondary text |
| `--color-text-muted` | `#64748b` | Tertiary text, metadata |
| `--color-border` | `#e2e8f0` | Dividers, borders |

### Dark Mode

| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `#60a5fa` | Links (lighter for dark bg) |
| `--color-bg` | `#0f172a` | Page background |
| `--color-bg-subtle` | `#1e293b` | Cards |
| `--color-text` | `#f1f5f9` | Primary text |
| `--color-border` | `#334155` | Dividers |

### Semantic Colors

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--color-success` | `#16a34a` | `#4ade80` | Success states |
| `--color-warning` | `#ca8a04` | `#facc15` | Warning states |
| `--color-error` | `#dc2626` | `#f87171` | Error states |
| `--color-info` | `#0891b2` | `#22d3ee` | Info states |

## Typography

### Font Stack

```css
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
--font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
```

### Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | 1.875rem (30px) | 600 | 1.3 |
| H2 | 1.25rem (20px) | 600 | 1.3 |
| H3 | 1.125rem (18px) | 600 | 1.3 |
| Body | 1rem (16px) | 400 | 1.6 |
| Small | 0.875rem (14px) | 400 | 1.5 |
| Caption | 0.8125rem (13px) | 400 | 1.5 |

### Text Colors

- **Primary text**: Headings, story titles
- **Secondary text**: Body content, descriptions
- **Muted text**: Metadata, timestamps, footer

## Spacing Scale

Based on 0.25rem (4px) increments:

| Token | Value | Pixels |
|-------|-------|--------|
| `--space-1` | 0.25rem | 4px |
| `--space-2` | 0.5rem | 8px |
| `--space-3` | 0.75rem | 12px |
| `--space-4` | 1rem | 16px |
| `--space-5` | 1.25rem | 20px |
| `--space-6` | 1.5rem | 24px |
| `--space-8` | 2rem | 32px |
| `--space-10` | 2.5rem | 40px |
| `--space-12` | 3rem | 48px |

## Components

### Navigation

- Pill-shaped buttons with subtle background
- Hover: darker background, text color change
- Focus: 2px primary color outline

### Story Cards

- Title: Bold, text color, hover changes to primary
- Metadata: Muted color, smaller size
- Link badges: Uppercase, small, pill-shaped

### Entity Groups

- Container: Subtle background, rounded corners, border
- Header: Bold name with bottom border
- Stories: Standard story list inside

### Status Badges

```html
<span class="status-badge status-success">SUCCESS</span>
<span class="status-badge status-warning">RUNNING</span>
<span class="status-badge status-error">FAILED</span>
```

### Tables

- Container with border and rounded corners
- Header row: Muted background
- Body rows: Hover effect
- Responsive: Horizontal scroll on mobile

### Archive Grid

- CSS Grid: Auto-fill, 140px minimum column width
- Cards: Centered text, subtle background
- Hover: Primary color highlight, slight lift

## Responsive Breakpoints

| Breakpoint | Width | Adjustments |
|------------|-------|-------------|
| Mobile | < 640px | Reduced padding, smaller fonts |
| Tablet | 640px - 1024px | Default layout |
| Desktop | > 1024px | Max-width constraint (52rem) |

### Mobile Adaptations

- Reduced body padding (16px)
- Smaller H1 (1.5rem)
- Navigation pills: smaller padding
- Tables: Full-bleed with horizontal scroll

## Accessibility

### Color Contrast

All text meets WCAG 2.1 AA requirements:
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum

### Focus States

All interactive elements have visible focus indicators:
- 2px solid primary color outline
- 2px offset for clarity

### Motion

Transitions are kept under 200ms. Future: Add `prefers-reduced-motion` media query.

## Print Styles

When printing:
- Navigation and footer are hidden
- Max-width constraint removed
- Story items avoid page breaks

## Implementation

All styles are embedded in `base.html` using CSS custom properties. No external dependencies required.

### Extending the Design

To add new components:

1. Use existing CSS variables for colors/spacing
2. Follow the established naming conventions
3. Include hover/focus states
4. Test in both light and dark mode
5. Verify responsive behavior

### Example: Adding a New Badge Type

```css
.status-pending {
    background-color: var(--color-info-bg);
    color: var(--color-info);
}
```
