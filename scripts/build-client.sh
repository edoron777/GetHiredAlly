#!/bin/bash
set -e

echo "=== Starting client build ==="
echo "Current directory: $(pwd)"
echo "Changing to client directory..."

(
  cd "$(dirname "$0")/../client"
  echo "Now in: $(pwd)"
  echo "Package.json contents:"
  cat package.json | grep -A5 '"scripts"'
  echo ""
  echo "Running npm install..."
  npm install
  echo "Running npm run build..."
  npm run build
)

echo "=== Build complete ==="
