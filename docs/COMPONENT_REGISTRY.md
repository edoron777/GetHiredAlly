# Component Registry

This document catalogs all reusable components in the GetHiredAlly application.

---

## TextMarker

| Field | Value |
|-------|-------|
| **Name** | TextMarker |
| **Location** | `client/src/components/common/TextMarker/` |
| **Purpose** | Mark/highlight text with customizable colors, styles, icons |
| **Files** | types.ts, MarkerService.ts, MarkerStyles.css, TextMarker.tsx, index.ts |
| **Import** | `import { TextMarker, CV_OPTIMIZER_COLORS } from '@/components/common/TextMarker'` |
| **Parameters** | content (string), markers (MarkerItem[]), config (MarkerConfig) |
| **Styles** | 'underline' or 'rectangle' |
| **Predefined Colors** | CV_OPTIMIZER_COLORS, NOTION_COLORS |
| **Date Added** | January 1, 2026 |

### Usage Example:
```typescript
<TextMarker
  content={text}
  markers={[{ id: '1', matchText: 'word', tag: 'critical' }]}
  config={{
    style: 'underline',
    tagColors: { critical: { color: '#e03e3e' } },
    icon: { icon: 'i', position: 'after' },
    onClick: (id) => handleClick(id)
  }}
/>
```

---

## StandardToolbar

| Field | Value |
|-------|-------|
| **Name** | StandardToolbar |
| **Location** | `client/src/components/common/StandardToolbar.tsx` |
| **Purpose** | Expand/Collapse + Email/WhatsApp sharing + PDF/Word/MD export |
| **Import** | `import { StandardToolbar } from '@/components/common'` |
| **Used By** | CV Optimizer, X-Ray, Interview Questions |

---

## VideoModal

| Field | Value |
|-------|-------|
| **Name** | VideoModal |
| **Location** | `client/src/components/common/VideoModal.tsx` |
| **Purpose** | YouTube video player with 16:9 aspect ratio, expand/minimize |
| **Import** | `import { VideoModal } from '@/components/common'` |
| **Used By** | Dashboard ServiceCards |

---

## ServiceCard

| Field | Value |
|-------|-------|
| **Name** | ServiceCard |
| **Location** | `client/src/components/common/ServiceCard.tsx` |
| **Purpose** | Service cards with icon+title, description, Coming Soon support |
| **Import** | `import { ServiceCard } from '@/components/common'` |
| **Used By** | Dashboard HomeSection |

---

## SectionSeparator

| Field | Value |
|-------|-------|
| **Name** | SectionSeparator |
| **Location** | `client/src/components/common/SectionSeparator.tsx` |
| **Purpose** | Navy gradient horizontal separator line |
| **Import** | `import { SectionSeparator } from '@/components/common'` |
| **Used By** | Dashboard between sections |

---

## GoogleSignInButton

| Field | Value |
|-------|-------|
| **Name** | GoogleSignInButton |
| **Location** | `client/src/components/common/GoogleSignInButton.tsx` |
| **Purpose** | Google OAuth sign-in with loading state and error handling |
| **Import** | `import { GoogleSignInButton } from '@/components/common'` |
| **Used By** | LoginPage, RegisterPage |

---

## OrDivider

| Field | Value |
|-------|-------|
| **Name** | OrDivider |
| **Location** | `client/src/components/common/OrDivider.tsx` |
| **Purpose** | "or" text divider between auth methods |
| **Import** | `import { OrDivider } from '@/components/common'` |
| **Used By** | LoginPage, RegisterPage |

---

## UserSessionKeep

| Field | Value |
|-------|-------|
| **Name** | UserSessionKeep |
| **Location** | `client/src/components/common/UserSessionKeep/` |
| **Purpose** | "Continue work" banner with session resume/archive |
| **Import** | `import { UserSessionKeep } from '@/components/common'` |
| **Used By** | CV Optimizer, X-Ray, Smart Questions |

---

## TipBox

| Field | Value |
|-------|-------|
| **Name** | TipBox |
| **Location** | `client/src/components/common/TipBox/` |
| **Purpose** | Flexible modal popup with dynamic sections and buttons |
| **Files** | types.ts, TipBoxSection.tsx, TipBox.tsx, TipBoxStyles.css, index.ts |
| **Import** | `import { TipBox, TIPBOX_COLORS } from '@/components/common'` |
| **Parameters** | isOpen, onClose, title, severity, sections[], buttons[] |
| **Section Types** | text, category, example-wrong, example-correct, input, instructions, custom |
| **Severities** | critical, important, consider, polish, info |
| **Date Added** | January 1, 2026 |

### Usage Example:
```typescript
<TipBox
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Missing Quantification"
  severity="critical"
  sections={[
    { type: 'category', label: 'CATEGORY', content: 'Content Quality' },
    { type: 'text', label: 'WHY THIS MATTERS', content: 'Numbers make achievements concrete.' },
    { type: 'example-wrong', label: 'CURRENT', content: 'Helped with projects' },
    { type: 'example-correct', label: 'SUGGESTED', content: 'Led 5 projects saving $2M' },
    { type: 'input', label: 'YOUR VERSION', placeholder: 'Type your improved version...' }
  ]}
  buttons={[
    { id: 'apply', label: 'Apply to CV', variant: 'primary', onClick: handleApply },
    { id: 'close', label: 'Close', variant: 'secondary', onClick: handleClose }
  ]}
/>
```

---

## GHAScanner

| Field | Value |
|-------|-------|
| **Name** | GHAScanner |
| **Location** | `client/src/components/common/GHAScanner.tsx` |
| **Purpose** | GitHub Actions-style scanning animation |
| **Import** | `import { GHAScanner } from '@/components/common'` |
| **Used By** | CV Optimizer scanning page |
