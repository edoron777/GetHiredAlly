#!/bin/bash
cd "$(dirname "$0")/../client"

export VITE_GOOGLE_CLIENT_ID="${VITE_GOOGLE_CLIENT_ID:-405217818612-ookhd5s7cemp0advrqltajv2l45v8pjb.apps.googleusercontent.com}"

echo "Building with VITE_GOOGLE_CLIENT_ID set"

npm install
npm run build
