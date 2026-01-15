# DESIGN_GUIDE.md - Sources Status Page

## Feature: add-sources-status-and-degradation-reporting

## Visual Design Direction

This guide documents the design decisions for the Sources Status page, ensuring consistency and maintainability.

## Color Palette

The design uses semantic colors from the base design system CSS variables:

### Status Colors

| Status | Background | Text | Variable |
|--------|------------|------|----------|
| Success (HAS_UPDATE) | `--color-success-bg` (#dcfce7) | `--color-success` (#16a34a) | Green |
| Info (NO_UPDATE, STATUS_ONLY) | `--color-info-bg` (#cffafe) | `--color-info` (#0891b2) | Cyan |
| Error (FETCH_FAILED, PARSE_FAILED) | `--color-error-bg` (#fee2e2) | `--color-error` (#dc2626) | Red |
| Warning (CANNOT_CONFIRM) | `--color-warning-bg` (#fef9c3) | `--color-warning` (#ca8a04) | Amber |

### Dark Mode Support

All colors adapt automatically via CSS media query `prefers-color-scheme: dark`:

| Status | Dark Background | Dark Text |
|--------|-----------------|-----------|
| Success | #14532d | #4ade80 |
| Info | #164e63 | #22d3ee |
| Error | #450a0a | #f87171 |
| Warning | #422006 | #facc15 |

## Typography

### Hierarchy

| Element | Size | Weight | Variable |
|---------|------|--------|----------|
| Page title (h1) | 1.875rem | 600 | -- |
| Section heading (h2) | 1.25rem | 600 | -- |
| Source name | inherit | 600 | `.source-name` |
| Source ID | 0.75rem | 400 | `.source-id`, monospace |
| Status badge | 0.6875rem | 600 | uppercase |
| Summary count | 1.75rem | 700 | `.summary-card__count` |
| Summary label | 0.8125rem | 500 | uppercase |

### Font Families

- **Sans-serif:** System font stack (`--font-sans`)
- **Monospace:** `--font-mono` for source IDs, method tags, item counts

## Spacing Scale

Using CSS custom properties:

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | 0.25rem | Inline padding |
| `--space-2` | 0.5rem | Badge padding |
| `--space-3` | 0.75rem | Grid gaps |
| `--space-4` | 1rem | Card padding |
| `--space-6` | 1.5rem | Section margins |
| `--space-8` | 2rem | Category section margins |

## Component Specifications

### Summary Cards

```css
.summary-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: var(--space-4);
    border-radius: var(--radius-lg);
    border: 1px solid transparent;
    transition: transform 200ms ease, box-shadow 200ms ease;
}

.summary-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}
```

**Grid Layout:**
```css
.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: var(--space-3);
}
```

### Status Badges

```css
.status-badge {
    display: inline-flex;
    align-items: center;
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-sm);
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: transform 150ms ease;
}

.status-badge:hover {
    transform: scale(1.05);
}
```

### Tier Badge

Circular indicator showing source priority tier:

```css
.tier-badge {
    width: 1.5rem;
    height: 1.5rem;
    border-radius: 50%;
    font-size: 0.75rem;
    font-weight: 600;
    background: var(--color-bg-muted);
}

.tier-badge--0 {
    background: var(--color-primary-light);
    color: var(--color-primary);
}
```

### Method Tag

Monospace tag for collection method:

```css
.method-tag {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    padding: var(--space-1) var(--space-2);
    background: var(--color-bg-muted);
    border-radius: var(--radius-sm);
}
```

### Item Counts

```css
.item-count {
    font-family: var(--font-mono);
    font-weight: 500;
}

.item-count--positive { color: var(--color-success); }
.item-count--zero { color: var(--color-text-muted); }
```

## Interactions

### Hover States

| Element | Hover Effect |
|---------|--------------|
| Summary cards | `translateY(-2px)`, shadow |
| Status badges | `scale(1.05)` |
| Table rows | Background color change |
| Navigation links | Border color, background change |

### Transitions

All interactive elements use consistent transition timing:

- **Fast:** 150ms ease (badges, micro-interactions)
- **Base:** 200ms ease (cards, panels)

### Focus States

Accessibility-compliant focus indicators:

```css
a:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
    border-radius: var(--radius-sm);
}
```

## Responsive Design

### Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| > 768px | Full table with all columns |
| <= 768px | Hide Tier, Method, Details columns |

### Mobile Optimizations

```css
@media (max-width: 768px) {
    .summary-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .hide-mobile {
        display: none;
    }
}
```

## Accessibility

### ARIA Labels

- Summary section: `aria-labelledby="summary-heading"`
- Category sections: `aria-labelledby="[category]-heading"`
- Status badges: `role="status"` with `aria-label`
- Empty state: `role="alert"`

### Screen Reader Support

- Summary grid uses `role="list"` and `role="listitem"`
- Proper heading hierarchy (h1 > h2)
- Skip link to main content

## Information Hierarchy

### Visual Priority (Top to Bottom)

1. **Summary cards** - Quick status overview at a glance
2. **Category sections** - Grouped by source type for easy scanning
3. **Source tables** - Detailed per-source information
4. **Details column** - Reason text and remediation hints

### Color Semantics

- **Green:** Positive outcome, updates found
- **Cyan/Blue:** Neutral, no action needed
- **Red:** Error, requires attention
- **Amber/Yellow:** Warning, uncertain state

## Design Rationale

### Why Cards for Summary?

- Provides scannable dashboard-style overview
- Clear visual separation between status types
- Hover effects invite exploration

### Why Category Grouping?

- Reduces cognitive load by chunking related sources
- Allows users to focus on relevant categories
- Count in heading provides quick reference

### Why Monospace for IDs?

- Technical identifiers look better in monospace
- Easier to read and copy
- Distinguishes from human-readable names

---

*Design guide created: 2026-01-15*
