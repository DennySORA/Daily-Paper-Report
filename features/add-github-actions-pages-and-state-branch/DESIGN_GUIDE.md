# Design Guide - Research Digest Frontend

This document defines the visual direction and UX patterns for the Research Digest static site.

## Design Philosophy

- **Clarity over decoration**: Information hierarchy is paramount
- **Minimal cognitive load**: Clean, scannable layouts
- **Responsive by default**: Mobile-first approach
- **Accessible first**: WCAG 2.1 Level A compliance

## Color System

### Light Mode
```css
--color-primary: #2563eb       /* Blue - links, CTAs */
--color-primary-hover: #1d4ed8 /* Darker blue on interaction */
--color-primary-light: #dbeafe /* Light blue backgrounds */

--color-bg: #ffffff            /* Main background */
--color-bg-subtle: #f8fafc     /* Cards, elevated surfaces */
--color-bg-muted: #f1f5f9      /* Disabled, inactive */

--color-text: #0f172a          /* Primary text */
--color-text-secondary: #475569 /* Secondary text */
--color-text-muted: #64748b    /* Tertiary, hints */

--color-border: #e2e8f0        /* Default borders */
--color-border-strong: #cbd5e1 /* Emphasized borders */
```

### Dark Mode
Dark mode is automatically applied via `@media (prefers-color-scheme: dark)`:
- Background shifts to slate (#0f172a)
- Text becomes light (#f1f5f9)
- Primary blue becomes lighter for contrast (#60a5fa)

### Semantic Colors
| Purpose | Color | Usage |
|---------|-------|-------|
| Success | `#16a34a` (green) | HAS_UPDATE, SUCCESS |
| Warning | `#ca8a04` (amber) | CANNOT_CONFIRM, RUNNING |
| Error | `#dc2626` (red) | FETCH_FAILED, FAILED |
| Info | `#0891b2` (cyan) | NO_UPDATE |

## Typography

### Font Stack
```css
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
--font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
```

### Scale
| Element | Size | Weight | Use |
|---------|------|--------|-----|
| H1 | 1.875rem | 600 | Page title |
| H2 | 1.25rem | 600 | Section headers |
| H3 | 1.125rem | 600 | Subsection |
| Body | 1rem | 400 | Main content |
| Small | 0.875rem | 400 | Meta, captions |
| Tiny | 0.75rem | 500 | Badges, labels |

### Line Height
- Headings: 1.3
- Body: 1.6

## Spacing

Consistent spacing scale based on 0.25rem (4px) increments:
```css
--space-1: 0.25rem   /* 4px */
--space-2: 0.5rem    /* 8px */
--space-3: 0.75rem   /* 12px */
--space-4: 1rem      /* 16px */
--space-5: 1.25rem   /* 20px */
--space-6: 1.5rem    /* 24px */
--space-8: 2rem      /* 32px */
--space-10: 2.5rem   /* 40px */
--space-12: 3rem     /* 48px */
```

## Layout

### Container
- Max width: 52rem (832px)
- Centered with auto margins
- Padding: 1.5rem (desktop), 1rem (mobile)

### Page Structure
```
[Skip Link]
[Header]
  [H1 Title]
  [Navigation]
[Main Content]
  [Sections with H2]
[Footer]
```

## Components

### Navigation
- Horizontal flex layout with wrap
- Pill-style links with subtle background
- Current page indicated with `aria-current="page"` and highlighted styling
- Hover: darker background, stronger border
- Focus: 2px primary outline

### Story Item
- Title as primary link
- Meta line with date, entities, arXiv ID
- Optional link chips for additional resources
- Border bottom for visual separation

### Status Badges
```html
<span class="status-badge status-success">SUCCESS</span>
<span class="status-badge status-warning">RUNNING</span>
<span class="status-badge status-error">FAILED</span>
```
- Uppercase text
- Rounded corners (0.25rem)
- Semantic background colors

### Tables
- Full width with horizontal scroll container
- Header row with muted background
- Row hover state for scanability
- Cell padding: 0.75rem x 1rem

### Archive Grid
- CSS Grid with auto-fill, minmax(140px, 1fr)
- Card-style date links
- Hover lift effect with shadow

## Accessibility

### Skip Link
```html
<a href="#main-content" class="skip-link">Skip to main content</a>
```
- Hidden by default (top: -40px)
- Visible on focus (top: 0)
- Primary blue background with white text

### Current Page
```html
<a href="index.html" aria-current="page">Latest</a>
```
- Highlighted with primary-light background
- Primary color border and text

### Focus States
All interactive elements have visible focus indicators:
- 2px solid primary color outline
- 2px offset for visibility

### Color Contrast
- All text meets WCAG AA contrast ratio (4.5:1 for normal text)
- Large text and icons meet 3:1 ratio

## Responsive Breakpoints

### Mobile (< 640px)
- Reduced body padding (1rem)
- Smaller headings (H1: 1.5rem, H2: 1.125rem)
- Smaller nav buttons
- Archive grid: minmax(120px, 1fr)
- Tables: full-bleed with negative margins

### Print
- Full width, no max-width
- Navigation and footer hidden
- Story items prevent page break inside

## Animation & Motion

- Transitions: 150ms ease (fast), 200ms ease (base)
- Hover transitions on all interactive elements
- Skip link slide animation on focus
- Archive card subtle lift on hover

## File Organization

```
src/renderer/templates/
├── _macros.html      # Reusable Jinja macros
├── base.html         # Base layout with design system
├── index.html        # Latest digest
├── day.html          # Archive day view
├── archive.html      # Date list
├── sources.html      # Source status
└── status.html       # Run history
```

## Maintenance Notes

1. **CSS Variables**: All colors/spacing use CSS custom properties for easy theming
2. **Macros**: Story rendering is centralized in `_macros.html`
3. **Dark Mode**: Automatic via media query, no JS required
4. **No External Dependencies**: All styles inline in base.html
