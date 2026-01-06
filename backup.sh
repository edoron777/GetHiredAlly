#!/bin/bash
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
if [ -z "$1" ]; then
    MSG="Backup: ${TIMESTAMP}"
else
    MSG="$1 [${TIMESTAMP}]"
fi
echo -e "${YELLOW}Creating backup...${NC}"
git add -A
git commit -m "$MSG"
git push origin main
echo -e "${GREEN}✅ Backup complete!${NC}"
git log --oneline -3
