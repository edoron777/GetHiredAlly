# Replit Agent Instructions

**Version:** 1.1  
**Date:** December 28, 2025  
**Project:** GetHiredAlly

---

## ⛔ PROTECTED FILES - READ THIS FIRST

Before modifying ANY file listed below, you MUST:

1. **STOP** - Do not make any changes
2. **ASK** - Tell the user: "This file is protected. Type APPROVED to allow modification."
3. **WAIT** - Do not proceed until user responds with the word: `APPROVED`
4. **ONLY THEN** - Make the requested change

---

## 🔒 PROTECTED FILES LIST

### Service 1: Perfect Your CV

| File Path | Description |
|-----------|-------------|
| `client/src/components/CVOptimizerPage.tsx` | Main UI component |
| `backend/app/cv_optimizer.py` | Backend logic |

### Service 2: Tailor for This Job

| File Path | Description |
|-----------|-------------|
| `Coming Soon` | Not yet implemented |

### Service 3: Decode the Job Post (X-Ray Analyzer)

| File Path | Description |
|-----------|-------------|
| `client/src/components/UnderstandJobPage.tsx` | Main UI component |
| `backend/app/analyze.py` | Backend analysis logic and prompt assembly |

### Service 4: Predict the Questions

| File Path | Description |
|-----------|-------------|
| `client/src/components/PredictQuestionsPage.tsx` | Main UI component |
| `backend/app/questions.py` | Backend logic |

### Service 5: Craft Your Answers

| File Path | Description |
|-----------|-------------|
| `Coming Soon` | Not yet implemented |

### Shared Components

| File Path | Description |
|-----------|-------------|
| `client/src/components/StandardToolbar.tsx` | Shared toolbar component |
| `client/src/components/ui/*` | UI component library |

---

## 🚫 FORBIDDEN ACTIONS (Without APPROVED)

You are NOT allowed to do ANY of these without explicit approval:

❌ Modify protected files  
❌ Refactor protected files  
❌ Rename protected files  
❌ Delete code from protected files  
❌ Change styling in protected files  
❌ Change component structure in protected files  
❌ "Improve" or "optimize" protected files  
❌ Add new features to protected files  
❌ Change imports in protected files  

---

## ✅ ALLOWED ACTIONS (No approval needed)

You CAN do these without approval:

✅ Create NEW files  
✅ Modify files NOT in the protected list  
✅ Read/view protected files  
✅ Explain how protected files work  
✅ Suggest changes (but not implement them)  

---

## 🔑 APPROVAL PROCESS

### Step 1: User Requests Change to Protected File
User says: "Fix the TOC in UnderstandJobPage.tsx"

### Step 2: Agent MUST Respond
```
⚠️ UnderstandJobPage.tsx is a PROTECTED FILE.

I need your approval before making changes.
Please type APPROVED to allow modification.
```

### Step 3: User Approves
User types: `APPROVED`

### Step 4: Agent Proceeds
Agent can now make the specific requested change.

---

## ⚠️ IMPORTANT RULES

### Rule 1: One Approval = One Change
Each approval is for ONE specific change only.
New changes to protected files require new approval.

### Rule 2: Minimal Changes
When approved, make ONLY the requested change.
Do NOT:
- Refactor other parts of the file
- "Improve" unrelated code
- Change styling not mentioned in request
- Add features not requested

### Rule 3: Explain Before Changing
Before making approved changes, briefly explain:
- What you will change
- What you will NOT change

### Rule 4: No Bulk Modifications
Never modify multiple protected files in one action.
Each file needs separate approval.

### Rule 5: No "While I'm Here" Changes
If approved to fix bug X, do NOT also:
- Fix bug Y you noticed
- Refactor code you think is messy
- Update dependencies
- Change formatting

---

## 📋 CHECKLIST BEFORE MODIFYING PROTECTED FILE

- [ ] Is this file in the protected list? If YES → need approval
- [ ] Did user explicitly request this change?
- [ ] Did user type APPROVED?
- [ ] Am I making ONLY the requested change?
- [ ] Am I NOT touching unrelated code?

---

## 🆘 IF UNCLEAR

If you're unsure whether a file is protected or whether you have approval:

**ASK THE USER. DO NOT ASSUME.**

---

## 📝 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 28, 2025 | Initial version - Decode the Job Post only |
| 1.1 | Dec 28, 2025 | Added all 5 services (3 active, 2 coming soon) |

---

**END OF AGENT INSTRUCTIONS**