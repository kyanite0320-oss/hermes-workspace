#!/bin/bash
# PC B（loofnn）定时推送：灵魂 + 工作区
# 每天 14:00 和 19:00 执行
set -e

echo "=== 灵魂同步（PC B）==="
SOUL_DIR="$HOME/hermes-data"
if [ -d "$SOUL_DIR" ]; then
    cd "$SOUL_DIR"
    git pull --rebase origin main 2>/dev/null || true
    if git status --porcelain | grep -q .; then
        git add -A
        git commit -m "🔄 PC B 自动同步 soul $(date '+%Y-%m-%d %H:%M')"
        git push origin main
        echo "✅ 灵魂同步完成"
    else
        echo "⏭️ 无变化"
    fi
else
    echo "⚠️ 灵魂仓库不存在，请先 git clone"
fi

echo ""
echo "=== 工作区同步（PC B）==="
WS_DIR="/mnt/c/AI/hermes"
if [ -d "$WS_DIR" ]; then
    cd "$WS_DIR"
    git pull --rebase origin main 2>/dev/null || true
    if git status --porcelain | grep -v '__pycache__' | grep -q .; then
        git add -A
        git reset -- morning-brief/__pycache__/ 2>/dev/null || true
        git commit -m "🔄 PC B 自动同步 workspace $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true
        git push origin main
        echo "✅ 工作区同步完成"
    else
        echo "⏭️ 无变化"
    fi
else
    echo "⚠️ 工作区不存在"
fi
