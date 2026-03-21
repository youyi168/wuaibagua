#!/bin/bash
# 原生 Android 开发环境安装脚本（简化版 - 仅 SDK）
# 不安装 Android Studio GUI，仅安装 SDK 和构建工具

set -e

echo "=========================================="
echo "  Android SDK 命令行工具安装"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# 1. 创建 SDK 目录
info "创建 SDK 目录..."
mkdir -p ~/Android/Sdk/cmdline-tools
mkdir -p ~/Android/Sdk/platforms
mkdir -p ~/Android/Sdk/build-tools
mkdir -p ~/Android/Sdk/platform-tools

# 2. 下载 Command Line Tools
info "下载 Android SDK Command Line Tools..."
CMDLINE_VERSION="11076708"
CMDLINE_ZIP="/tmp/cmdline-tools.zip"

wget -q --show-progress -O "$CMDLINE_ZIP" \
    "https://dl.google.com/android/repository/commandlinetools-linux-${CMDLINE_VERSION}_latest.zip"

info "解压 Command Line Tools..."
cd ~/Android/Sdk/cmdline-tools
unzip -q -o "$CMDLINE_ZIP"
mv cmdline-tools latest
rm "$CMDLINE_ZIP"

# 3. 配置环境变量
info "配置环境变量..."
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools

if ! grep -q "ANDROID_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# Android SDK
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/build-tools/34.0.0
EOF
    info "环境变量已添加到 ~/.bashrc"
fi

# 4. 接受许可证
info "接受 Android SDK 许可证..."
yes | sdkmanager --licenses 2>&1 | tail -5

# 5. 安装必要的 SDK 组件
info "安装 Android SDK 组件..."
info "这可能需要 10-20 分钟，取决于网络速度..."

sdkmanager --install \
    "platform-tools" \
    "platforms;android-34" \
    "build-tools;34.0.0" \
    "cmdline-tools;latest" 2>&1 | tail -20

# 6. 安装 Gradle
info "安装 Gradle..."
GRADLE_VERSION="8.5"
GRADLE_ZIP="/tmp/gradle-${GRADLE_VERSION}.zip"

wget -q --show-progress -O "$GRADLE_ZIP" \
    "https://mirrors.cloud.tencent.com/gradle/gradle-${GRADLE_VERSION}-bin.zip"

sudo unzip -q "$GRADLE_ZIP" -d /opt/
sudo ln -sf "/opt/gradle-${GRADLE_VERSION}/bin/gradle" /usr/local/bin/gradle
rm "$GRADLE_ZIP"

if ! grep -q "gradle" ~/.bashrc; then
    cat >> ~/.bashrc << EOF

# Gradle
export PATH=/opt/gradle-${GRADLE_VERSION}/bin:\$PATH
EOF
fi

# 7. 验证安装
info "验证安装..."
source ~/.bashrc

echo ""
echo "=== SDK 版本 ==="
sdkmanager --version

echo ""
echo "=== 已安装的组件 ==="
sdkmanager --list_installed | head -20

echo ""
echo "=== Gradle 版本 ==="
gradle --version | head -5

echo ""
echo "=== ADB 版本 ==="
adb --version | head -1

echo ""
echo "=========================================="
info "安装完成！"
echo "=========================================="
echo ""
echo "环境变量已配置，重新加载：source ~/.bashrc"
echo ""
echo "常用命令："
echo "  sdkmanager --list                    # 列出可用组件"
echo "  sdkmanager --install <package>       # 安装组件"
echo "  adb devices                          # 查看连接的设备"
echo "  gradle --version                     # 查看 Gradle 版本"
echo ""
echo "推荐的 IDE："
echo "  1. Android Studio: https://developer.android.com/studio"
echo "  2. IntelliJ IDEA: https://www.jetbrains.com/idea/"
echo "  3. VS Code + Android 插件"
echo ""
