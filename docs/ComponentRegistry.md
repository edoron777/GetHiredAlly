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
| GHAScanner | UI Component | ✅ | `client/src/components/common/GHAScanner/` |
| scannerSounds | Utility | ✅ | `client/src/components/common/GHAScanner/` |
| ScoreDashboard | UI Component | ✅ | `client/src/components/cv-optimizer/` |
| ScoreComparison | UI Component | ✅ | `client/src/components/cv-optimizer/` |
| copyToClipboard | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| sendEmail | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| shareToWhatsApp | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| stripMarkdown | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| formatContent | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| calculate_cv_score | Backend | ✅ | `backend/common/scoring/` |
| calculate_after_fix_score | Backend | ✅ | `backend/common/scoring/` |
| DocStyler | Utility | ✅ | `client/src/components/common/DocStyler/` |
| generatePDF | Utility | ✅ | `client/src/components/common/DocStyler/generators/` |
| generateWord | Utility | ✅ | `client/src/components/common/DocStyler/generators/` |
| generateMD | Utility | ✅ | `client/src/components/common/DocStyler/generators/` |
| GHATooltip | UI Component | ✅ | `client/src/components/common/Tooltip/` |
| TOOLTIP_TEXTS | Utility | ✅ | `client/src/components/common/Tooltip/` |
| TOOLTIP_STYLES | Utility | ✅ | `client/src/components/common/Tooltip/` |

---

## CATEGORY: UI COMPONENTS

### ActionBar

| Field | Value |
|-------|-------|
| **Name** | ActionBar |
| **Purpose** | Reusable toolbar for share/export actions |
| **Category** | UI Component |
| **Location** | `client/src/components/common/ActionBar/` |
| **Import** | `import { ActionBar } from '@/components/common/ActionBar'` |
| **Status** | ✅ Complete |
| **Used By** | CV Optimizer, X-Ray Analyzer, Interview Questions |
| **Added** | December 30, 2025 |

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `content` | string | Text/markdown content to act on |
| `fileName` | string | Default filename for downloads |
| `emailSubject` | string | Email subject line |
| `contentType` | string | Service identifier (for DocStyler) |
| `contentMetadata` | object | Additional metadata (score, grade) |
| `hiddenButtons` | array | Buttons to hide |
| `disabledButtons` | array | Buttons to disable |

**Buttons:**

| Button | Function | Calls |
|--------|----------|-------|
| Copy | Copy to clipboard | Internal clipboard.js |
| Email | Open email client | Internal email.js |
| WhatsApp | Share via WhatsApp | Internal whatsapp.js |
| PDF | Download styled PDF | **DocStyler.pdf()** |
| WORD | Download styled DOCX | **DocStyler.word()** |
| MD | Download Markdown | **DocStyler.md()** |

**Example:**
```jsx
<ActionBar
  content={reportContent}
  fileName="CV_Analysis_Report"
  emailSubject="My CV Analysis - GetHiredAlly"
  contentType="cv-optimizer"
  contentMetadata={{ score: 72, grade: 'Good' }}
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

### GHAScanner

| Field | Value |
|-------|-------|
| **Name** | GHAScanner |
| **Purpose** | Visual progress indicator with animated grid (Defrag-style) |
| **Category** | UI Component |
| **Location** | `client/src/components/common/GHAScanner/` |
| **Import** | `import { GHAScanner } from '@/components/common/GHAScanner'` |
| **Status** | ✅ Complete |
| **Used By** | CVScanningPage, future services |
| **Added** | December 30, 2025 |

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `isScanning` | boolean | Yes | Controls animation state |
| `progress` | number | Yes | Progress 0-100 |
| `statusMessages` | string[] | No | Rotating status texts |
| `showProgress` | boolean | No | Show progress bar |
| `showLegend` | boolean | No | Show color legend |
| `onComplete` | function | No | Callback at 100% |

**Features:**
- Windows 95 Defrag-style grid animation
- Color-coded blocks (OK, Minor, Medium, Critical)
- Rotating status messages
- Progress bar
- Pleasant sound effects (Web Audio API)

**Related Files:**
- `scannerStyles.ts` - Style constants and colors
- `scannerSounds.ts` - Web Audio API sound effects

**Sound Effects:**

| Sound | Trigger | Character |
|-------|---------|-----------|
| Start | Scan begins | Ascending chime |
| Complete | Scan finishes | 3-note success chord |
| Error | Problem | Gentle descending tone |

**Example:**
```tsx
import { GHAScanner, STATUS_MESSAGES } from '@/components/common/GHAScanner';

<GHAScanner
  isScanning={true}
  progress={45}
  statusMessages={STATUS_MESSAGES.cvOptimizer}
  onComplete={() => navigate('/results')}
/>
```

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

### GHATooltip

| Field | Value |
|-------|-------|
| **Name** | GHATooltip |
| **Purpose** | Reusable tooltip with consistent styling for contextual help |
| **Category** | UI Component |
| **Location** | `client/src/components/common/Tooltip/` |
| **Import** | `import { GHATooltip } from '@/components/common/Tooltip'` |
| **Status** | ✅ Complete |
| **Used By** | ActionBar, All Service Pages |
| **Added** | December 30, 2025 |

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `children` | ReactNode | Yes | Trigger element |
| `text` | string | Yes | Tooltip description |
| `title` | string | No | Optional bold title |
| `variant` | 'default' \| 'warning' \| 'info' | No | Color variant |
| `side` | 'top' \| 'bottom' \| 'left' \| 'right' | No | Position |
| `icon` | 'info' \| 'warning' \| 'tip' | No | Optional icon |
| `learnMoreUrl` | string | No | Optional help link |

**Related Files:**
- `tooltipTexts.ts` - Central text storage for all tooltips
- `tooltipStyles.ts` - Style constants and variants

**Example:**
```tsx
import { GHATooltip, TOOLTIP_TEXTS } from '@/components/common/Tooltip';

// Basic usage
<GHATooltip text="Copy to clipboard">
  <Button>Copy</Button>
</GHATooltip>

// Using central texts
<GHATooltip {...TOOLTIP_TEXTS.actionBar.pdf}>
  <Button>PDF</Button>
</GHATooltip>
```

---

## CATEGORY: DOCUMENT GENERATION

### DocStyler

| Field | Value |
|-------|-------|
| **Name** | DocStyler |
| **Purpose** | Centralized document formatting for PDF, Word, Markdown exports |
| **Category** | Utility |
| **Location** | `client/src/components/common/DocStyler/` |
| **Import** | `import { DocStyler } from '@/components/common/DocStyler'` |
| **Status** | ✅ Complete |
| **Used By** | ActionBar |
| **Added** | December 30, 2025 |

**Main Methods:**

| Method | Description |
|--------|-------------|
| `DocStyler.generate({ content, format, options })` | Generate document in specified format |
| `DocStyler.pdf(content, options)` | Generate PDF |
| `DocStyler.word(content, options)` | Generate Word document |
| `DocStyler.md(content, options)` | Generate Markdown |

**Options Object:**

| Option | Type | Description |
|--------|------|-------------|
| `title` | string | Document title |
| `service` | string | Service name (cv-optimizer, xray-analyzer, etc.) |
| `fileName` | string | Download filename |
| `metadata` | object | Additional data (score, grade, etc.) |

**Related Files:**
- `generators/generatePDF.js` - PDF generation with pdf-lib
- `generators/generateWord.js` - Word generation with docx
- `generators/generateMD.js` - Markdown with header/footer
- `styles/documentStyles.js` - Brand colors, fonts, company info

**Document Styling Includes:**
- Professional header with title, service name, date
- Footer with page numbers (Page X of Y)
- Footer links: GetHiredAlly App | GetHiredAlly Blog
- Brand color: #1E5A85
- Markdown to styled text conversion

**Example:**
```javascript
import { DocStyler } from '@/components/common/DocStyler';

await DocStyler.pdf(content, {
  title: 'CV Analysis Report',
  service: 'cv-optimizer',
  fileName: 'CV_Report',
  metadata: { score: 72, grade: 'Good' }
});
```

---

### generatePDF

| Field | Value |
|-------|-------|
| **Purpose** | Generate styled PDF document using pdf-lib |
| **Location** | `client/src/components/common/DocStyler/generators/generatePDF.js` |
| **Import** | `import { generatePDF } from '@/components/common/DocStyler'` |
| **Parameters** | `content` (string), `options` (object) |
| **Status** | ✅ Complete |

---

### generateWord

| Field | Value |
|-------|-------|
| **Purpose** | Generate styled Word document using docx library |
| **Location** | `client/src/components/common/DocStyler/generators/generateWord.js` |
| **Import** | `import { generateWord } from '@/components/common/DocStyler'` |
| **Parameters** | `content` (string), `options` (object) |
| **Status** | ✅ Complete |

---

### generateMD

| Field | Value |
|-------|-------|
| **Purpose** | Generate styled Markdown document with header/footer |
| **Location** | `client/src/components/common/DocStyler/generators/generateMD.js` |
| **Import** | `import { generateMD, downloadMD } from '@/components/common/DocStyler'` |
| **Parameters** | `content` (string), `options` (object) |
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

## COMPONENT RELATIONSHIPS

This section documents how components work together.

### ActionBar → DocStyler (Document Export)

**Flow:**
1. User clicks PDF/WORD/MD button
2. ActionBar captures: content, fileName, contentType, metadata
3. ActionBar calls DocStyler.pdf() or .word() or .md()
4. DocStyler applies: header, footer, styling, branding
5. User downloads styled document

**How to Connect:**
1. ActionBar passes contentType and contentMetadata props
2. DocStyler uses these to generate appropriate header
3. Document includes service name, date, score (if applicable)

```
ActionBar.handlePDF() → DocStyler.pdf(content, options) → Downloads styled PDF
ActionBar.handleWord() → DocStyler.word(content, options) → Downloads styled DOCX
ActionBar.handleMD() → DocStyler.md(content, options) → Downloads Markdown
```

### ActionBar → GHATooltip (Button Explanations)

**Flow:**
1. ActionBarButton wrapped in GHATooltip
2. User hovers over button
3. GHATooltip shows: title, description, icon
4. User understands button purpose

**How to Connect:**
1. Import GHATooltip and TOOLTIP_TEXTS
2. Wrap ActionBarButton with GHATooltip
3. Use TOOLTIP_TEXTS.actionBar.[buttonName] for content

```tsx
import { GHATooltip, TOOLTIP_TEXTS } from '@/components/common/Tooltip';

<GHATooltip {...TOOLTIP_TEXTS.actionBar.pdf}>
  <ActionBarButton label="PDF" onClick={handlePDF} />
</GHATooltip>
```

### TOOLTIP_TEXTS Central Storage

All tooltip content organized by service:
- `TOOLTIP_TEXTS.actionBar` - ActionBar button tooltips
- `TOOLTIP_TEXTS.cvOptimizer` - CV Optimizer tooltips
- `TOOLTIP_TEXTS.xrayAnalyzer` - X-Ray Analyzer tooltips
- `TOOLTIP_TEXTS.interviewQuestions` - Interview Questions tooltips
- `TOOLTIP_TEXTS.general` - Shared tooltips (delete, save, etc.)

### Full Integration Example

```tsx
import { ActionBar } from '@/components/common/ActionBar';
import { DocStyler } from '@/components/common/DocStyler';
import { GHATooltip, TOOLTIP_TEXTS } from '@/components/common/Tooltip';

<ActionBar
  content={analysisResult.report}
  fileName="CV_Analysis_Report"
  emailSubject="My CV Analysis"
  contentType="cv-optimizer"
  contentMetadata={{
    score: analysisResult.score,
    grade: analysisResult.grade,
  }}
/>
```

---

**TOTAL COMPONENTS:** 20  
**Last Updated:** December 30, 2025
