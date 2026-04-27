#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  git add .
  git commit -m "Update site: $(date '+%Y-%m-%d %H:%M:%S')"
  git push
  echo "Deployed to GitHub Pages."
  echo "Site: https://kkjudoon.github.io/lolita-research/"
else
  echo "No changes to deploy."
fi
