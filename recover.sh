#!/bin/bash
case "$1" in
    "list") git log --oneline -${2:-10} ;;
    "file") git checkout ${3:-HEAD~1} -- $2 ;;
    "undo") git checkout -- . ;;
    "rollback") git checkout $2 -- . ;;
    *) echo "Commands: list, file <path>, undo, rollback <id>" ;;
esac
