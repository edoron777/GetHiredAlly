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

## GHAScanner

| Field | Value |
|-------|-------|
| **Name** | GHAScanner |
| **Location** | `client/src/components/common/GHAScanner.tsx` |
| **Purpose** | GitHub Actions-style scanning animation |
| **Import** | `import { GHAScanner } from '@/components/common'` |
| **Used By** | CV Optimizer scanning page |
