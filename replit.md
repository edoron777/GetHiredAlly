# GetHiredAlly - Interview Preparation Application

## Overview
GetHiredAlly is an interview preparation application designed to empower job seekers. It offers advanced job description analysis ("X-Ray"), personalized interview question preparation, and AI-powered answer crafting. The application aims to provide a comprehensive toolkit for users to confidently approach their job interviews, increasing their chances of success.

## User Preferences
I prefer iterative development, with a focus on delivering small, functional increments. Please provide detailed explanations for any complex architectural decisions or significant code changes. I like clean, readable code with a strong emphasis on maintainability. When suggesting changes, please offer multiple options with their respective pros and cons. I want to be asked before any major changes are made to the core logic or database schema.

---

## PERMANENT DEVELOPMENT RULES

These rules must be followed in ALL development work. They ensure code consistency, maintainability, and prevent duplicate code.

---

### 1. FOLDER STRUCTURE

```
client/src/
│
├── components/
│   │
│   ├── common/                    # REUSABLE (All services use these)
│   │   ├── StandardToolbar.tsx    # Export toolbar (PDF, Word, Email, etc.)
│   │   ├── VideoModal.tsx         # Video lightbox modal
│   │   ├── ServiceCard.tsx        # Home page service cards
│   │   ├── SectionSeparator.tsx   # Visual separator line
│   │   ├── GoogleSignInButton.tsx # Google OAuth sign-in button
│   │   ├── OrDivider.tsx          # "or" divider between auth options
│   │   ├── UserSessionKeep/       # Session resume banner component
│   │   │   ├── UserSessionKeep.tsx
│   │   │   ├── useServiceSession.ts
│   │   │   ├── sessionTypes.ts
│   │   │   └── index.ts
│   │   ├── DocumentEditor/        # Document display with formatting
│   │   │   ├── DocumentEditor.tsx
│   │   │   ├── DocumentEditorStyles.css
│   │   │   ├── types.ts
│   │   │   ├── index.ts
│   │   │   ├── renderers/
│   │   │   │   ├── TextRenderer.tsx
│   │   │   │   ├── MarkdownRenderer.tsx
│   │   │   │   └── WordRenderer.tsx
│   │   │   └── utils/
│   │   │       └── formatDetector.ts
│   │   └── index.ts               # Exports all common components
│   │
│   ├── cv-optimizer/              # CV Optimizer specific
│   │   ├── CategoryFilterPanel.tsx
│   │   ├── StrengthsSection.tsx
│   │   ├── EffortGroupView.tsx
│   │   ├── WorkTypeGroupView.tsx
│   │   └── index.ts
│   │
│   ├── home/                      # Home page specific
│   │   ├── HomeSection.tsx
│   │   └── index.ts
│   │
│   └── ui/                        # shadcn/ui components
│
├── config/                        # Configuration files
│   ├── homePageServices.ts        # Home page card content
│   ├── cvCategories.ts            # CV analysis categories
│   └── workTypeCategories.ts      # Work type definitions
│
├── lib/                           # Core utilities
│   ├── auth.ts                    # Authentication
│   └── utils.ts                   # General utilities
│
└── utils/                         # Helper functions
    └── strengthsDetector.ts       # CV strengths detection
```

---

### 2. REUSABLE COMPONENTS RULES

#### Rule 2.1: Single Source of Truth
**NEVER duplicate component code.** If a component is used in 2+ places, it belongs in `components/common/`.

#### Rule 2.2: StandardToolbar
**ALWAYS** use `StandardToolbar` from `components/common/` when a page needs:
- Expand/Collapse all functionality
- Email sharing
- WhatsApp sharing
- PDF/Word/Markdown export

```tsx
// CORRECT
import { StandardToolbar } from '../components/common';

// WRONG - Never create new toolbar code
<div className="toolbar">...</div>
```

#### Rule 2.3: VideoModal
**ALWAYS** use `VideoModal` from `components/common/` for tutorial videos.

#### Rule 2.4: ServiceCard
**ALWAYS** use `ServiceCard` from `components/common/` for home page service cards.

#### Rule 2.5: How to Import Common Components
```tsx
// CORRECT - Import from index
import { StandardToolbar, VideoModal, ServiceCard } from '../components/common';

// WRONG - Don't import from individual files
import StandardToolbar from '../components/common/StandardToolbar';
```

---

### 3. AVAILABLE REUSABLE COMPONENTS

| Component | Purpose | Used By |
|-----------|---------|---------|
| StandardToolbar | Expand/Collapse + Email/WhatsApp sharing + PDF/Word/MD export | CV Optimizer, X-Ray, Interview Questions |
| VideoModal | YouTube video player with 16:9 aspect ratio, expand/minimize | Dashboard ServiceCards |
| ServiceCard | Service cards with icon+title, description, Coming Soon support | Dashboard HomeSection |
| SectionSeparator | Navy gradient horizontal separator line | Dashboard between sections |
| GoogleSignInButton | Google OAuth sign-in with loading state and error handling | LoginPage, RegisterPage |
| OrDivider | "or" text divider between auth methods | LoginPage, RegisterPage |
| UserSessionKeep | "Continue work" banner with session resume/archive | CV Optimizer, X-Ray, Smart Questions |
| DocumentEditor | Display documents with formatting (MD, Word, PDF, Text) + TextMarker | CV Optimizer |

---

### 4. COMPONENT CREATION RULES

#### Rule 4.1: One Component = One File
Each component should be in its own file. Max 150 lines per component.

#### Rule 4.2: One Responsibility
Each file should do ONE thing. If a component does multiple things, split it.

#### Rule 4.3: Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `StandardToolbar.tsx`, `IssueCard.tsx` |
| Services | camelCase | `exportService.ts`, `emailService.ts` |
| Config | camelCase | `cvCategories.ts`, `homePageServices.ts` |
| Utils | camelCase | `formatters.ts`, `validators.ts` |
| Hooks | camelCase with "use" | `useAuth.ts`, `useLocalStorage.ts` |
| Folders | kebab-case | `cv-optimizer/`, `xray-analyzer/` |

#### Rule 4.4: Where to Put New Components
| If component is... | Put it in... |
|--------------------|--------------|
| Used by multiple services | `components/common/` |
| Used only by CV Optimizer | `components/cv-optimizer/` |
| Used only by X-Ray Analyzer | `components/xray-analyzer/` |
| Used only by Interview Questions | `components/interview-questions/` |
| A full page | Root of `components/` |

---

### 5. DESIGN SYSTEM

#### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Navy Blue | `#1E3A5F` | Primary, headers, toolbar |
| Warm Beige | `#FAF9F7` | Page backgrounds |
| White | `#FFFFFF` | Cards, content areas |
| Blue | `#2563EB` | Buttons, links |
| Gray 50 | `#F9FAFB` | Disabled states |
| Gray 200 | `#E5E7EB` | Borders |
| Gray 500 | `#6B7280` | Secondary text |
| Gray 900 | `#111827` | Primary text |

#### Typography
| Element | Size | Weight |
|---------|------|--------|
| Page Title | 32px | Bold |
| Section Title | 24px | Bold |
| Card Title | 20px | Bold |
| Body Text | 16px | Regular |
| Small Text | 14px | Regular |
| Button Text | 16px | Medium |

#### Spacing
| Size | Value | Usage |
|------|-------|-------|
| xs | 4px | Tight spacing |
| sm | 8px | Small gaps |
| md | 16px | Default gaps |
| lg | 24px | Card padding |
| xl | 32px | Section padding |
| 2xl | 48px | Large separations |

---

### 6. STANDARD TOOLBAR SPECIFICATION

The StandardToolbar is a navy blue bar with white text/icons.

**Layout:**
```
┌────────────────────────────────────────────────────────────────────────────┐
│ [+] [−]  │  [         SPACE         ]  │  Email  WhatsApp  │  PDF  WORD  MD │
└────────────────────────────────────────────────────────────────────────────┘
```

**Styling:**
- Background: Navy Blue (#1E3A5F)
- Text: White
- Height: One line only
- Separators: White with 30% opacity (`│`)

---

### 7. DOCUMENT EXPORT STANDARDS

All exported documents (PDF, Word, MD) must include:

| Position | Content |
|----------|---------|
| Left | Page X of Y |
| Center | Service name (e.g., "CV Optimizer Report") |
| Right | https://gethiredally.com |

---

### 8. CODE QUALITY RULES

- **No Console Logs in Production** - Remove all `console.log` statements before committing
- **Error Handling** - Always handle errors gracefully with user-friendly messages
- **Loading States** - Always show loading indicators during async operations
- **TypeScript** - Use TypeScript interfaces for all props and data structures

---

### 9. BEFORE CREATING ANY COMPONENT

**ALWAYS check first:**
1. Does it already exist in `components/common/`?
2. Can an existing component be extended?
3. Will this be used in multiple places? → Put in `common/`

**If unsure, ASK before creating new components.**

---

### 10. THE 5 GOLDEN RULES

1. **Check `common/` first** - Before creating any component
2. **Never duplicate** - If it exists, import it
3. **One file, one job** - Keep components focused
4. **Use StandardToolbar** - For all export/share functionality
5. **Follow naming conventions** - PascalCase for components, camelCase for others

---

## System Architecture

The application features a modern web architecture with a React 19 frontend utilizing Vite, Tailwind CSS, and shadcn/ui for a consistent and responsive user experience. The backend is built with FastAPI (Python), providing robust API endpoints and serving the static frontend assets in production. Supabase, a PostgreSQL-based platform, handles data persistence, authentication, and real-time capabilities.

**UI/UX Design:**
- **Color Scheme:** Warm beige (#FAF9F7) background, navy blue (#1E3A5F) primary accents, and dark gray (#333333) text for high readability.
- **Component Library:** Leverages shadcn/ui for consistent, accessible, and themeable UI components.
- **Workflow:** Emphasizes a coaching-style language, especially in AI interactions, focusing on "Focus Areas" instead of "weaknesses" to foster a positive user experience.

**Technical Implementations:**
- **Authentication:** User registration and login utilize bcrypt for password hashing and Supabase for session management. Email verification is implemented via the Resend API. Google OAuth Sign-In is supported via @react-oauth/google library, allowing one-click registration/login with automatic account linking.
- **AI Integration:** A unified AI service routes requests to Claude or Gemini models via LiteLLM, allowing users to select their preferred provider. All AI interactions are logged for usage tracking, cost analysis, and auditing.
- **Interview Questions:** A comprehensive database of 54 static interview questions categorized into Universal, Behavioral, Situational, Self-Assessment, and Cultural Fit, each with detailed preparation guidance. Dynamic, AI-generated questions are personalized based on user input.
- **CV Optimization:** An AI-powered CV optimizer scans resumes (PDF, DOCX, TXT), identifies issues, suggests improvements, and can even generate a fixed version with side-by-side comparison. CV content is encrypted at rest using Fernet.

**Feature Specifications:**
- **Job Description X-Ray:** Analyzes job descriptions using AI to extract key requirements and suggest relevant interview preparation.
- **Interview Question Predictor:** Provides access to static questions with varying levels of detail (questions only, with tips, full prep) and generates smart, personalized questions.
- **CV Optimizer:** Scans CVs, identifies strengths and areas for improvement, and offers AI-generated fixes.
- **User Tiers:** Differentiated access and usage limits based on user profiles (Standard, Special, VIP) for various services.

**System Design Choices:**
- **Security:** Implements security headers, rate limiting on sensitive endpoints, audit logging for security events, input validation with Pydantic, and secure password handling.
- **Scalability:** Utilizes Supabase for a managed and scalable database solution, and FastAPI for an asynchronous and high-performance backend.
- **Environment Variables:** Critical configurations are managed via environment variables for secure deployment.

## External Dependencies
- **Supabase:** Database (PostgreSQL), Authentication, Storage.
- **Vite:** Frontend build tool.
- **Tailwind CSS:** Utility-first CSS framework.
- **React Router:** Frontend routing.
- **Resend API:** Email sending for verification.
- **Claude AI (Anthropic):** Job description analysis.
- **Gemini AI (Google):** Personalized interview question generation, CV analysis.
- **LiteLLM:** Unified interface for various LLM providers, including cost tracking.
