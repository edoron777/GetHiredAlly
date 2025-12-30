#!/bin/bash

# ===========================================
# Git Backup Script for GetHiredAlly
# Usage: Just type "backupgit" in terminal
# ===========================================

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "🚀 Starting Git Backup..."
echo ""

# Step 1: Ensure .gitignore has the right exclusions
GITIGNORE_ENTRIES=(
    "Temp/*"
    "attached_assets/Pasted--Replit-Prompt-Google-Social-Login-Task-Implement-Googl_1766925450134.txt"
    "*.pyc"
    "__pycache__/"
    ".env"
)

for entry in "${GITIGNORE_ENTRIES[@]}"; do
    if ! grep -qxF "$entry" .gitignore 2>/dev/null; then
        echo "$entry" >> .gitignore
        echo -e "${YELLOW}➕ Added to .gitignore: $entry${NC}"
    fi
done
echo -e "${GREEN}✓ .gitignore verified${NC}"

# Step 2: Stage all changes
git add -A
echo -e "${GREEN}✓ Changes staged${NC}"

# Step 3: Check if there are changes to commit
if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠ No changes to commit${NC}"
    exit 0
fi

# Step 4: Create commit with timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
COMMIT_MSG="Backup $TIMESTAMP"

git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✓ Committed: $COMMIT_MSG${NC}"

# Step 5: Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
if git push origin main; then
    echo ""
    echo -e "${GREEN}✅ Backup completed successfully!${NC}"
    echo -e "${GREEN}   Time: $TIMESTAMP${NC}"
else
    echo ""
    echo -e "${RED}❌ Push failed! Check your connection or credentials.${NC}"
    exit 1
fi

echo ""
