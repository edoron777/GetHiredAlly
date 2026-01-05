# Component Registry - Single Source of Truth

**Document Type:** Master Index  
**Purpose:** Central catalog of ALL reusable functions and components  
**Version:** 2.0  
**Last Updated:** January 05, 2026

---

## PURPOSE

This is the **Single Source of Truth** for all reusable code in GetHiredAlly.

### Who Uses This

| Audience | Use Case |
|----------|----------|
| **Claude** | Look up existing functions before creating new ones |
| **Replit Agent** | Understand available components |
| **Developers** | Find import paths and usage |
| **Code** | Discover available functions programmatically |

### Rules

1. **Every function/component MUST be registered here**
2. **Check here BEFORE creating new functionality**
3. **Update when adding/modifying/deprecating components**
4. **Link to detailed docs, don't duplicate content**

---

## QUICK LOOKUP TABLE

| Name | Type | Category | Status | Location |
|------|------|----------|--------|----------|
| detect_cv_blocks | Function | CV Detection | ✅ | `backend/common/detection/` |
| detect_cv_issues | Function | CV Detection | ✅ | `backend/common/detection/` |
| CVBlockStructure | Data Class | CV Detection | ✅ | `backend/common/detection/` |
| CVIssueReport | Data Class | CV Detection | ✅ | `backend/common/detection/` |
| calculate_cv_score | Function | Scoring | ✅ | `backend/common/scoring/` |
| calculate_after_fix_score | Function | Scoring | ✅ | `backend/common/scoring/` |
| ActionBar | Component | UI | ✅ | `client/src/components/common/ActionBar/` |
| ActionBarButton | Component | UI | ✅ | `client/src/components/common/ActionBar/` |
| GHAScanner | Component | UI | ✅ | `client/src/components/common/GHAScanner/` |
| GHATooltip | Component | UI | ✅ | `client/src/components/common/Tooltip/` |
| DocStyler | Component | UI | ✅ | `client/src/components/common/DocStyler/` |
| TextMarker | Function | UI Utility | ✅ | `client/src/components/common/TextMarker/` |
| TipBox | Component | UI | ✅ | `client/src/components/common/TipBox/` |
| UserSessionKeep | Component | Session | ✅ | `client/src/components/common/UserSessionKeep/` |
| useServiceSession | Hook | Session | ✅ | `client/src/components/common/UserSessionKeep/` |
| ScoreDashboard | Component | CV Optimizer | ✅ | `client/src/components/cv-optimizer/` |
| ScoreComparison | Component | CV Optimizer | ✅ | `client/src/components/cv-optimizer/` |
| copyToClipboard | Function | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| sendEmail | Function | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| shareToWhatsApp | Function | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| stripMarkdown | Function | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |
| formatContent | Function | Utility | ✅ | `client/src/components/common/ActionBar/utils/` |

**TOTAL: 21 components/functions**

---

## STATUS LEGEND

| Status | Icon | Meaning |
|--------|------|---------|
| Complete | ✅ | Fully implemented and tested |
| In Progress | 🚧 | Currently being developed |
| Placeholder | ⏳ | Interface exists, functionality pending |
| Deprecated | ❌ | Should not be used |

---

## CATEGORY: CV DETECTION

### detect_cv_blocks

| Field | Value |
|-------|-------|
| **Type** | Backend Function |
| **Purpose** | Parse CV text into structured blocks with line numbers |
| **Location** | `backend/common/detection/block_detector.py` |
| **Import** | `from backend.common.detection import detect_cv_blocks` |
| **Input** | `cv_text: str` |
| **Output** | `CVBlockStructure` |
| **Status** | ✅ Complete |
| **Used By** | detect_cv_issues, CV Optimizer |
| **Docs** | `CV_Blocks_Structure_Function.md` |
| **Added** | January 05, 2026 |

---

### detect_cv_issues

| Field | Value |
|-------|-------|
| **Type** | Backend Function |
| **Purpose** | Detect all CV issues and return structured report with score |
| **Location** | `backend/common/detection/master_detector.py` |
| **Import** | `from backend.common.detection import detect_cv_issues` |
| **Input** | `cv_text: str`, `job_description?: str`, `cv_block_structure?: CVBlockStructure` |
| **Output** | `CVIssueReport` |
| **Status** | ✅ Complete |
| **Used By** | CV Optimizer, cv_optimizer.py |
| **Docs** | `CV_Issue_Detection_Function_Description.md` |
| **Added** | January 05, 2026 |

---

### CVBlockStructure

| Field | Value |
|-------|-------|
| **Type** | Data Class |
| **Purpose** | Represents parsed CV structure (blocks, jobs, bullets) |
| **Location** | `backend/common/detection/block_detector.py` |
| **Import** | `from backend.common.detection import CVBlockStructure` |
| **Status** | ✅ Complete |
| **Used By** | detect_cv_blocks, detect_cv_issues |
| **Docs** | `CV_Blocks_Structure_Function.md` |
| **Added** | January 05, 2026 |

---

### CVIssueReport

| Field | Value |
|-------|-------|
| **Type** | Data Class |
| **Purpose** | Represents complete issue detection report with score |
| **Location** | `backend/common/detection/master_detector.py` |
| **Import** | `from backend.common.detection import CVIssueReport` |
| **Status** | ✅ Complete |
| **Used By** | detect_cv_issues, CV Optimizer |
| **Docs** | `CV_Issue_Detection_Function_Description.md` |
| **Added** | January 05, 2026 |

---

## CATEGORY: SCORING

### calculate_cv_score

| Field | Value |
|-------|-------|
| **Type** | Backend Function |
| **Purpose** | Calculate deterministic CV score from extracted data |
| **Location** | `backend/common/scoring/calculator.py` |
| **Import** | `from backend.common.scoring import calculate_cv_score` |
| **Input** | `data: dict` (extracted CV fields) |
| **Output** | `dict` with `total_score`, `breakdown`, `grade`, `message` |
| **Status** | ✅ Complete |
| **Used By** | CV Optimizer API |
| **Added** | December 30, 2025 |

---

### calculate_after_fix_score

| Field | Value |
|-------|-------|
| **Type** | Backend Function |
| **Purpose** | Project score improvement after fixes |
| **Location** | `backend/common/scoring/after_fix.py` |
| **Import** | `from backend.common.scoring import calculate_after_fix_score` |
| **Input** | `before_score: int`, `issues: list`, `breakdown: dict` |
| **Output** | `dict` with `before_score`, `after_score`, `improvement` |
| **Status** | ✅ Complete |
| **Used By** | CV Optimizer API (/fixed endpoint) |
| **Added** | December 30, 2025 |

---

## CATEGORY: SESSION MANAGEMENT

### UserSessionKeep

| Field | Value |
|-------|-------|
| **Type** | React Component |
| **Purpose** | Banner UI showing user has work in progress, with Continue/Start New options |
| **Location** | `client/src/components/common/UserSessionKeep/UserSessionKeep.tsx` |
| **Import** | `import { UserSessionKeep } from '@/components/common/UserSessionKeep'` |
| **Props** | `serviceName: string`, `onStartNew?: function` |
| **Status** | ✅ Complete |
| **Used By** | CV Optimizer, X-Ray Analyzer, Predict Questions |
| **Docs** | `UserSessionKeep/README.md` |
| **Added** | January 05, 2026 |

---

### useServiceSession

| Field | Value |
|-------|-------|
| **Type** | React Hook |
| **Purpose** | Fetches and manages session state via backend API |
| **Location** | `client/src/components/common/UserSessionKeep/useServiceSession.ts` |
| **Import** | `import { useServiceSession } from '@/components/common/UserSessionKeep'` |
| **Input** | `serviceName: string` |
| **Output** | `{ session, loading, error, archiveSession }` |
| **Status** | ✅ Complete |
| **Used By** | UserSessionKeep component |
| **Docs** | `UserSessionKeep/README.md` |
| **Added** | January 05, 2026 |

---

## CATEGORY: UI COMPONENTS

### ActionBar

| Field | Value |
|-------|-------|
| **Type** | React Component |
| **Purpose** | Reusable toolbar for share/export actions (Copy, Email, WhatsApp, PDF, Word, MD) |
| **Location** | `client/src/components/common/ActionBar/ActionBar.jsx` |
| **Import** | `import { ActionBar } from '@/components/common/ActionBar'` |
| **Props** | `content`, `fileName`, `emailSubject`, `hiddenButtons`, `disabledButtons` |
| **Status** | ✅ Complete (PDF/Word ⏳ Placeholder) |
| **Used By** | CV Optimizer Report Page |
| **Docs** | `ActionBar_Knowledge_Document.md` |
| **Added** | December 30, 2025 |

---

### GHAScanner

| Field | Value |
|-------|-------|
| **Type** | React Component |
| **Purpose** | Visual progress indicator with animated graphics during processing |
| **Location** | `client/src/components/common/GHAScanner/GHAScanner.tsx` |
| **Import** | `import { GHAScanner } from '@/components/common/GHAScanner'` |
| **Props** | `isScanning`, `progress`, `style`, `statusMessages`, `onComplete` |
| **Status** | ✅ Complete |
| **Used By** | CV Scanning Page |
| **Docs** | `GHAScanner_Knowledge_Document.md` |
| **Added** | December 30, 2025 |

---

### GHATooltip

| Field | Value |
|-------|-------|
| **Type** | React Component |
| **Purpose** | Reusable tooltip with consistent styling, icons, and learn more links |
| **Location** | `client/src/components/common/Tooltip/GHATooltip.tsx` |
| **Import** | `import { GHATooltip } from '@/components/common/Tooltip'` |
| **Props** | `text`, `title?`, `variant?`, `side?`, `icon?`, `learnMoreUrl?` |
| **Status** | ✅ Complete |
| **Used By** | All services |
| **Docs** | `GHATooltip_Knowledge_Document.md` |
| **Added** | December 30, 2025 |

---

### DocStyler

| Field | Value |
|-------|-------|
| **Type** | React Component |
| **Purpose** | Consistent document styling for reports and analysis outputs |
| **Location** | `client/src/components/common/DocStyler/` |
| **Import** | `import { DocStyler } from '@/components/common/DocStyler'` |
| **Status** | ✅ Complete |
| **Docs** | `DocStyler_Knowledge_Document.md` |
| **Added** | December 30, 2025 |

---

### TextMarker

| Field | Value |
|-------|-------|
| **Type** | UI Utility Function |
| **Purpose** | Highlight/mark text within documents for issue identification |
| **Location** | `client/src/components/common/TextMarker/` |
| **Import** | `import { TextMarker } from '@/components/common/TextMarker'` |
| **Status** | ✅ Complete |
| **Docs** | `TextMarker_Function_Documentation.md` |
| **Added** | January 05, 2026 |

---

### TipBox

| Field | Value |
|-------|-------|
| **Type** | React Component |
| **Purpose** | Contextual tip/hint boxes for user guidance |
| **Location** | `client/src/components/common/TipBox/` |
| **Import** | `import { TipBox } from '@/components/common/TipBox'` |
| **Status** | ✅ Complete |
| **Docs** | `TipBox_Function_Documentation.md` |
| **Added** | January 05, 2026 |

---

### ScoreDashboard

| Field | Value |
|-------|-------|
| **Type** | React Component |
| **Purpose** | Display CV score breakdown with progress bars |
| **Location** | `client/src/components/cv-optimizer/ScoreDashboard.jsx` |
| **Import** | `import ScoreDashboard from './ScoreDashboard'` |
| **Props** | `breakdown`, `totalScore`, `grade`, `message` |
| **Status** | ✅ Complete |
| **Used By** | CV Optimizer Report Page |
| **Added** | December 30, 2025 |

---

### ScoreComparison

| Field | Value |
|-------|-------|
| **Type** | React Component |
| **Purpose** | Display before/after score comparison after optimization |
| **Location** | `client/src/components/cv-optimizer/ScoreComparison.jsx` |
| **Import** | `import ScoreComparison from './ScoreComparison'` |
| **Props** | `beforeScore`, `afterScore`, `improvement`, `categoryImprovements` |
| **Status** | ✅ Complete |
| **Used By** | CV Optimizer Fixed Page |
| **Added** | December 30, 2025 |

---

## CATEGORY: UTILITIES

### copyToClipboard

| Field | Value |
|-------|-------|
| **Type** | Utility Function |
| **Purpose** | Copy text to clipboard with fallback for older browsers |
| **Location** | `client/src/components/common/ActionBar/utils/clipboard.js` |
| **Import** | `import { copyToClipboard } from '@/components/common/ActionBar/utils'` |
| **Input** | `text: string` |
| **Output** | `Promise<boolean>` |
| **Status** | ✅ Complete |
| **Used By** | ActionBar |
| **Added** | December 30, 2025 |

---

### sendEmail

| Field | Value |
|-------|-------|
| **Type** | Utility Function |
| **Purpose** | Open email client with pre-filled content |
| **Location** | `client/src/components/common/ActionBar/utils/email.js` |
| **Import** | `import { sendEmail } from '@/components/common/ActionBar/utils'` |
| **Input** | `{ subject, body, to }` |
| **Output** | `void` |
| **Status** | ✅ Complete |
| **Used By** | ActionBar |
| **Added** | December 30, 2025 |

---

### shareToWhatsApp

| Field | Value |
|-------|-------|
| **Type** | Utility Function |
| **Purpose** | Share content via WhatsApp (opens in new tab) |
| **Location** | `client/src/components/common/ActionBar/utils/whatsapp.js` |
| **Import** | `import { shareToWhatsApp } from '@/components/common/ActionBar/utils'` |
| **Input** | `text: string` (max 4096 chars) |
| **Output** | `void` |
| **Status** | ✅ Complete |
| **Used By** | ActionBar |
| **Added** | December 30, 2025 |

---

### stripMarkdown

| Field | Value |
|-------|-------|
| **Type** | Utility Function |
| **Purpose** | Remove markdown formatting from text |
| **Location** | `client/src/components/common/ActionBar/utils/formatters.js` |
| **Import** | `import { stripMarkdown } from '@/components/common/ActionBar/utils'` |
| **Input** | `content: string` |
| **Output** | `string` (plain text) |
| **Status** | ✅ Complete |
| **Used By** | ActionBar |
| **Added** | December 30, 2025 |

---

### formatContent

| Field | Value |
|-------|-------|
| **Type** | Utility Function |
| **Purpose** | Format content for specific output type (plain/html/markdown) |
| **Location** | `client/src/components/common/ActionBar/utils/formatters.js` |
| **Import** | `import { formatContent } from '@/components/common/ActionBar/utils'` |
| **Input** | `content: string`, `format: 'plain' | 'html' | 'markdown'` |
| **Output** | `string` |
| **Status** | ✅ Complete |
| **Used By** | ActionBar |
| **Added** | December 30, 2025 |

---

## HOW TO REGISTER NEW COMPONENTS

### Step 1: Add to Quick Lookup Table

Add a row with: Name, Type, Category, Status, Location

### Step 2: Add Detailed Entry

Copy this template:
```markdown
### [Component Name]

| Field | Value |
|-------|-------|
| **Type** | [Function/Component/Hook/Data Class] |
| **Purpose** | [One-line description] |
| **Location** | [File path] |
| **Import** | [Import statement] |
| **Input** | [Parameters] |
| **Output** | [Return type] |
| **Status** | [✅/🚧/⏳/❌] |
| **Used By** | [Services using this] |
| **Docs** | [Link to detailed documentation] |
| **Added** | [Date] |
```

### Step 3: Create Knowledge Document (if complex)

For complex components, create `[ComponentName]_Knowledge_Document.md`

---

## RELATED DOCUMENTATION

| Document | Purpose |
|----------|---------|
| `*_Knowledge_Document.md` | Detailed component specifications |
| `*_Function_Documentation.md` | Function specifications |
| `ServiceDocumentationStandard.md` | Documentation format guidelines |
| `ReplitFunctionCreationGuidelines.md` | How to create new functions |

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 30, 2025 | Initial creation with 11 components |
| 2.0 | Jan 05, 2026 | Major update: Added CV Detection functions, Session Management, restructured as Single Source of Truth |

---

**TOTAL COMPONENTS:** 21  
**Last Updated:** January 05, 2026

---

**END OF COMPONENT REGISTRY v2.0**
