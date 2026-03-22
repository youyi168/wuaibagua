#!/bin/bash
# 触发构建脚本

echo "🚀 触发 GitHub Actions 构建..."
echo ""

# 检查 Git 状态
echo "📋 检查 Git 状态..."
git status --short

echo ""
echo "📝 创建触发提交的空更改..."

# 添加一个空提交来触发构建
git commit --allow-empty -m "ci: 触发构建测试（强制清缓存）"

echo ""
echo "📤 推送到 GitHub..."
git push origin main

echo ""
echo "✅ 推送完成！"
echo ""
echo "📍 查看构建进度:"
echo "   https://github.com/youyi168/wuaibagua/actions"
echo ""
echo "⏱️ 预计耗时：12-15 分钟"
echo ""
