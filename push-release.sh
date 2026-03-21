#!/bin/bash
# 推送到 GitHub 脚本（安全版）
# 从 ~/.openclaw/secrets/ 加载环境变量

set -e

echo "🔐 从安全位置加载环境变量..."

# 从安全位置加载环境变量
if [ -f ~/.openclaw/secrets/github.env ]; then
    set -a  # 自动导出所有变量
    source ~/.openclaw/secrets/github.env
    set +a
    echo "✅ 已加载环境变量（从 ~/.openclaw/secrets/）"
else
    echo "❌ 错误：~/.openclaw/secrets/github.env 不存在"
    exit 1
fi

# 检查必要变量
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 错误：GITHUB_TOKEN 未设置"
    exit 1
fi

# 配置 Git 网络优化
echo "🔧 配置 Git 网络优化..."
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 1000
git config --global http.lowSpeedTime 300

# 测试网络连接
echo "🌐 测试 GitHub 连接..."
if ping -c 1 github.com > /dev/null 2>&1; then
    echo "✅ GitHub 网络连通"
else
    echo "❌ GitHub 网络不通"
    exit 1
fi

# 推送（带重试）
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo ""
    echo "🚀 推送尝试 $RETRY_COUNT/$MAX_RETRIES..."
    
    if git push https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@${GITHUB_REPO_URL} main --tags; then
        echo ""
        echo "✅ 推送成功！"
        echo ""
        echo "📦 GitHub Actions 将自动编译:"
        echo "   - Android APK (20-30 分钟)"
        echo "   - Windows EXE (10-15 分钟)"
        echo ""
        echo "📍 查看进度:"
        echo "   https://github.com/youyi168/wuaibagua/actions"
        echo ""
        echo "📥 发布页面:"
        echo "   https://github.com/youyi168/wuaibagua/releases"
        exit 0
    else
        echo "⚠️ 推送失败"
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "⏳ 30 秒后重试..."
            sleep 30
        fi
    fi
done

echo ""
echo "❌ 推送失败，已达到最大重试次数"
echo ""
echo "💡 建议:"
echo "   1. 检查网络连接"
echo "   2. 检查 Token 是否有效"
echo "   3. 使用 SSH 方式推送：git push origin main --tags"
exit 1
