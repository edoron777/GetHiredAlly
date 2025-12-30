# ComponentRegistry

**Document Type:** Registry / Index  
**Purpose:** Catalog of all reusable functions and components  
**Version:** 1.0  
**Date:** December 30, 2025

---

## PURPOSE

This document serves as a **central registry** for all reusable code in GetHiredAlly.

**IMPORTANT FOR REPLIT AI AGENT:**
Before creating any new component or utility function, CHECK THIS FILE FIRST
to see if it already exists.

---

## STATUS LEGEND

| Status | Meaning |
|--------|---------|
| ✅ Complete | Fully implemented and tested |
| ⏳ Placeholder | Interface exists, functionality pending |
| 🚧 In Progress | Currently being developed |
| ❌ Deprecated | Should not be used |

---

## QUICK LOOKUP TABLE

| Name | Category | Status | Location |
|------|----------|--------|----------|
| ActionBar | UI Component | ✅ | `client/src/components/common/ActionBar/` |
| ActionBarButton | UI Component | ✅ | `client/src/components/common/ActionBar/` |
| ScoreDashboard | UI Component | ✅ | `client/src/components/cv-optimizer/` |
| ScoreComparison | UI Component | ✅ | `client/src/components/cv-optimizer/` |
| copyToClipboard | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| sendEmail | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| shareToWhatsApp | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| stripMarkdown | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| formatContent | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| calculate_cv_score | Backend | ✅ | `backend/common/scoring/` |
| calculate_after_fix_score | Backend | ✅ | `backend/common/scoring/` |

---

## CATEGORY: UI COMPONENTS

### ActionBar

| Field | Value |
|-------|-------|
| **Purpose** | Reusable toolbar for share/export actions |
| **Location** | `client/src/components/common/ActionBar/` |
| **Import** | `import { ActionBar } from '@/components/common/ActionBar'` |
| **Status** | ✅ Complete (Copy, Email, WhatsApp, MD) / ⏳ (PDF, WORD) |

**Props:** `content`, `fileName`, `emailSubject`, `hiddenButtons`, `disabledButtons`

**Example:**
```jsx
<ActionBar
  content={reportContent}
  fileName="CV_Analysis_Report"
  emailSubject="My CV Analysis - GetHiredAlly"
  disabledButtons={['pdf', 'word']}
/>
```

---

### ActionBarButton

| Field | Value |
|-------|-------|
| **Purpose** | Individual button with tooltip for ActionBar |
| **Location** | `client/src/components/common/ActionBar/ActionBarButton.jsx` |
| **Import** | `import { ActionBarButton } from '@/components/common/ActionBar'` |
| **Status** | ✅ Complete |

**Props:** `label`, `icon`, `tooltip`, `color`, `hoverBg`, `onClick`, `disabled`, `successLabel`

---

### ScoreDashboard

| Field | Value |
|-------|-------|
| **Purpose** | Display CV score breakdown with progress bars |
| **Location** | `client/src/components/cv-optimizer/ScoreDashboard.jsx` |
| **Import** | `import ScoreDashboard from './ScoreDashboard'` |
| **Status** | ✅ Complete |

**Props:** `breakdown`, `totalScore`, `grade`, `message`

---

### ScoreComparison

| Field | Value |
|-------|-------|
| **Purpose** | Display before/after score comparison |
| **Location** | `client/src/components/cv-optimizer/ScoreComparison.jsx` |
| **Import** | `import ScoreComparison from './ScoreComparison'` |
| **Status** | ✅ Complete |

**Props:** `beforeScore`, `afterScore`, `improvement`, `categoryImprovements`

---

## CATEGORY: UTILITIES

### copyToClipboard

| Field | Value |
|-------|-------|
| **Purpose** | Copy text to clipboard with fallback |
| **Location** | `client/src/components/common/ActionBar/utils/clipboard.js` |
| **Import** | `import { copyToClipboard } from '@/components/common/ActionBar/utils'` |
| **Parameters** | `text` (string) |
| **Returns** | `Promise<boolean>` |
| **Status** | ✅ Complete |

---

### sendEmail

| Field | Value |
|-------|-------|
| **Purpose** | Open email client with pre-filled content |
| **Location** | `client/src/components/common/ActionBar/utils/email.js` |
| **Import** | `import { sendEmail } from '@/components/common/ActionBar/utils'` |
| **Parameters** | `{ subject, body, to }` |
| **Returns** | `void` |
| **Status** | ✅ Complete |

---

### shareToWhatsApp

| Field | Value |
|-------|-------|
| **Purpose** | Share content via WhatsApp |
| **Location** | `client/src/components/common/ActionBar/utils/whatsapp.js` |
| **Import** | `import { shareToWhatsApp } from '@/components/common/ActionBar/utils'` |
| **Parameters** | `text` (string, max 4096 chars) |
| **Returns** | `void` |
| **Status** | ✅ Complete |

---

### stripMarkdown

| Field | Value |
|-------|-------|
| **Purpose** | Remove markdown formatting from text |
| **Location** | `client/src/components/common/ActionBar/utils/formatters.js` |
| **Import** | `import { stripMarkdown } from '@/components/common/ActionBar/utils'` |
| **Parameters** | `content` (string) |
| **Returns** | `string` (plain text) |
| **Status** | ✅ Complete |

---

### formatContent

| Field | Value |
|-------|-------|
| **Purpose** | Format content for specific output type |
| **Location** | `client/src/components/common/ActionBar/utils/formatters.js` |
| **Import** | `import { formatContent } from '@/components/common/ActionBar/utils'` |
| **Parameters** | `content`, `format` ('plain' / 'html' / 'markdown') |
| **Returns** | `string` |
| **Status** | ✅ Complete |

---

## CATEGORY: BACKEND SCORING

### calculate_cv_score

| Field | Value |
|-------|-------|
| **Purpose** | Calculate deterministic CV score |
| **Location** | `backend/common/scoring/calculator.py` |
| **Import** | `from backend.common.scoring import calculate_cv_score` |
| **Parameters** | `data` (dict) |
| **Returns** | `dict` with `total_score`, `breakdown`, `grade`, `message` |
| **Status** | ✅ Complete |

---

### calculate_after_fix_score

| Field | Value |
|-------|-------|
| **Purpose** | Project score improvement after fixes |
| **Location** | `backend/common/scoring/after_fix.py` |
| **Import** | `from backend.common.scoring import calculate_after_fix_score` |
| **Parameters** | `before_score`, `issues`, `breakdown` |
| **Returns** | `dict` with `before_score`, `after_score`, `improvement` |
| **Status** | ✅ Complete |

---

## HOW TO UPDATE THIS REGISTRY

### Adding New Entry:
1. Choose correct category
2. Add entry with all fields
3. Include example if helpful

### Template for New Entry:
```markdown
### [Name]

| Field | Value |
|-------|-------|
| **Purpose** | [One-line description] |
| **Location** | [File path] |
| **Import** | [Import statement] |
| **Status** | [✅/⏳/🚧/❌] |

**Props/Parameters:** [List]
```

---

**TOTAL COMPONENTS:** 11  
**Last Updated:** December 30, 2025
