#!/usr/bin/env bash
# Build the site and publish site/dist to the gh-pages branch as a normal (non-force) commit.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/site" && npm run build >/dev/null
git -C "$ROOT" checkout -- site/public/lessons/index.json 2>/dev/null || true   # build timestamp only
H="$(git -C "$ROOT" rev-parse --short HEAD)"
WT="$(mktemp -d)"
git -C "$ROOT" fetch -q origin gh-pages
git -C "$ROOT" worktree add -q -B gh-pages "$WT" origin/gh-pages
find "$WT" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -r "$ROOT/site/dist/." "$WT/" && touch "$WT/.nojekyll"
cd "$WT" && git add -A
if git diff --cached --quiet; then echo "nothing to deploy"; else
  git -c user.name="Francesco Andreoli" -c user.email="15174764+andreolf@users.noreply.github.com" commit -qm "Deploy (main $H)"
  git push origin gh-pages
fi
cd "$ROOT" && git worktree remove --force "$WT"
