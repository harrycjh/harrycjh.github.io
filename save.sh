#!/bin/bash
cd "$(dirname "$0")"
if [ -z "$1" ]; then
    echo "用法: ./save.sh '提交说明'"
    exit 1
fi
git add -A
git commit -m "$1"
echo "✅ 已保存: $1"
