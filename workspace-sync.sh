#!/bin/bash
# 自动同步 Hermes 工作区到 GitHub（PC B 用）
set -e

WS_DIR="/mnt/c/AI/hermes"

cd "$WS_DIR"

git pull --rebase origin main 2>/dev/null || true

if git status --porcelain | grep -v '__pycache__' | grep -q .; then
    git add -A
    git reset -- morning-brief/__pycache__/ 2>/dev/null || true
    git commit -m "🔄 自动同步 workspace $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true
    git push origin main
    echo "✅ 工作区同步完成：$(date)"
else
    echo "⏭️ 工作区无变化，跳过 $(date)"
fi
