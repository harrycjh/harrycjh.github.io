#!/bin/bash

# 狼人杀服务器启动脚本

echo "🎭 狼人杀联机服务器启动器"
echo "============================"

cd "$(dirname "$0")"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装 Node.js"
    exit 1
fi

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 正在安装依赖..."
    npm install ws
fi

# 启动服务器
echo "🚀 启动服务器..."
echo ""

node server.js &

SERVER_PID=$!

echo ""
echo "✅ 服务器已启动！"
echo ""
echo "📱 手机访问方式："
echo ""
echo "   1. 先安装 ngrok (如果没有):"
echo "      brew install ngrok"
echo ""
echo "   2. 另开终端窗口，运行:"
echo "      ngrok http 3000"
echo ""
echo "   3. ngrok 会给你一个公网地址，复制发给朋友"
echo ""
echo "   4. 朋友在手机浏览器打开那个地址就能玩"
echo ""
echo "📋 游戏规则:"
echo "   • 6-12 人游戏"
echo "   • 包含: 狼人、村民、预言家、女巫、守卫、猎人、白痴"
echo "   • 每晚狼人击杀 → 女巫救人/毒人 → 预言家查验 → 守卫守护"
echo "   • 白天投票处决"
echo ""
echo "🛑 按 Ctrl+C 停止服务器"
echo ""

# 等待
wait $SERVER_PID