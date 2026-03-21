#!/bin/bash
# 原生 Android 开发环境安装脚本
# 适用于 Ubuntu 22.04 / Debian 11+

set -e

echo "=========================================="
echo "  原生 Android 开发环境安装"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查磁盘空间
AVAILABLE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -lt 30 ]; then
    error "磁盘空间不足！需要至少 30GB，当前可用：${AVAILABLE_SPACE}GB"
    exit 1
fi
info "磁盘空间检查通过：${AVAILABLE_SPACE}GB 可用"

# 1. 更新系统
info "更新系统包..."
sudo apt-get update

# 2. 安装基础依赖
info "安装系统依赖..."
sudo apt-get install -y \
    openjdk-17-jdk \
    wget curl unzip \
    git gitk git-gui \
    lib32z1 lib32ncurses6 lib32stdc++6 \
    libbz2-dev liblz4-dev libzstd-dev \
    qemu-kvm virt-manager libvirt-daemon-system \
    bridge-utils net-tools

# 3. 配置 Java 环境
info "配置 Java 环境..."
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 设置默认 Java
sudo update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java 2>/dev/null || true
sudo update-alternatives --set javac /usr/lib/jvm/java-17-openjdk-amd64/bin/javac 2>/dev/null || true

if ! grep -q "JAVA_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# Android Native Development
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
EOF
    info "Java 环境变量已添加到 ~/.bashrc"
fi

# 4. 安装 Android Studio
info "下载 Android Studio..."
ANDROID_STUDIO_URL="https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.2.1.12/android-studio-2024.2.1.12-linux.tar.gz"
ANDROID_STUDIO_ZIP="/tmp/android-studio.tar.gz"

# 使用镜像源
MIRROR_URL="https://mirrors.cloud.tencent.com/android-studio/ide-zips/2024.2.1.12/android-studio-2024.2.1.12-linux.tar.gz"

if ! wget -O "$ANDROID_STUDIO_ZIP" "$MIRROR_URL" 2>/dev/null; then
    warn "腾讯镜像下载失败，尝试官方源..."
    wget -O "$ANDROID_STUDIO_ZIP" "$ANDROID_STUDIO_URL"
fi

info "解压 Android Studio..."
sudo rm -rf /opt/android-studio
sudo tar -xzf "$ANDROID_STUDIO_ZIP" -C /opt/
sudo rm "$ANDROID_STUDIO_ZIP"

# 创建启动脚本
sudo cat > /usr/local/bin/android-studio << 'EOF'
#!/bin/bash
/opt/android-studio/bin/studio.sh "$@"
EOF
sudo chmod +x /usr/local/bin/android-studio

info "Android Studio 已安装到 /opt/android-studio"

# 5. 安装 Android SDK Command Line Tools
info "安装 Android SDK Command Line Tools..."
mkdir -p ~/Android/Sdk/cmdline-tools
SDK_CMDLINE_URL="https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
SDK_ZIP="/tmp/cmdline-tools.zip"

if ! wget -O "$SDK_ZIP" "$SDK_CMDLINE_URL" 2>/dev/null; then
    warn "下载失败，稍后可以通过 Android Studio 安装 SDK"
else
    unzip -q "$SDK_ZIP" -d /tmp/
    mv /tmp/cmdline-tools ~/Android/Sdk/cmdline-tools/latest
    rm "$SDK_ZIP"
fi

# 6. 配置 SDK 环境变量
info "配置环境变量..."
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/build-tools/34.0.0

if ! grep -q "ANDROID_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# Android SDK
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/build-tools/34.0.0
EOF
    info "Android SDK 环境变量已添加到 ~/.bashrc"
fi

# 7. 安装 Gradle
info "安装 Gradle..."
GRADLE_VERSION="8.5"
GRADLE_URL="https://mirrors.cloud.tencent.com/gradle/gradle-${GRADLE_VERSION}-bin.zip"
GRADLE_ZIP="/tmp/gradle-${GRADLE_VERSION}.zip"

if wget -O "$GRADLE_ZIP" "$GRADLE_URL" 2>/dev/null; then
    sudo unzip -q "$GRADLE_ZIP" -d /opt/
    sudo ln -sf "/opt/gradle-${GRADLE_VERSION}/bin/gradle" /usr/local/bin/gradle
    rm "$GRADLE_ZIP"
    
    if ! grep -q "gradle" ~/.bashrc; then
        cat >> ~/.bashrc << 'EOF'

# Gradle
export PATH=/opt/gradle-8.5/bin:$PATH
EOF
    fi
    info "Gradle ${GRADLE_VERSION} 已安装"
else
    warn "Gradle 下载失败，将使用项目自带的 Gradle Wrapper"
fi

# 8. 配置 KVM 虚拟化（加速模拟器）
info "配置 KVM 虚拟化..."
if [ -e /dev/kvm ]; then
    info "KVM 已启用"
else
    warn "KVM 不可用，Android 模拟器可能较慢"
fi

# 9. 接受 SDK 许可证
if [ -d ~/Android/Sdk/cmdline-tools/latest ]; then
    info "接受 Android SDK 许可证..."
    yes | sdkmanager --licenses 2>/dev/null || true
fi

# 10. 验证安装
info "验证安装..."
echo ""
echo "=== Java ==="
java -version 2>&1 | head -3

echo ""
echo "=== Android Studio ==="
ls -la /opt/android-studio/bin/studio.sh && echo "已安装" || echo "未找到"

echo ""
echo "=== Gradle ==="
gradle --version 2>/dev/null | head -2 || echo "未安装（将使用 Gradle Wrapper）"

echo ""
echo "=== SDK 目录 ==="
ls -la ~/Android/Sdk 2>/dev/null || echo "将通过 Android Studio 下载"

# 11. 创建桌面快捷方式
info "创建桌面快捷方式..."
cat > /tmp/android-studio.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Android Studio
Exec=/opt/android-studio/bin/studio.sh %F
Icon=/opt/android-studio/bin/studio.png
Categories=Development;IDE;
Terminal=false
StartupNotify=true
StartupWMClass=jetbrains-studio
MimeType=application/x-extension-iml;
EOF

sudo mv /tmp/android-studio.desktop /usr/share/applications/android-studio.desktop
sudo desktop-file-install /usr/share/applications/android-studio.desktop

info "桌面快捷方式已创建"

echo ""
echo "=========================================="
info "安装完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 重新加载环境变量：source ~/.bashrc"
echo "2. 启动 Android Studio: android-studio"
echo "3. 首次启动会下载 SDK 组件（约 2-3GB）"
echo "4. 配置 SDK 路径：~/Android/Sdk"
echo ""
echo "推荐安装的 SDK 组件："
echo "- Android SDK Platform 34 (Android 14)"
echo "- Android SDK Build-Tools 34.0.0"
echo "- Android Emulator"
echo "- Android SDK Platform-Tools"
echo ""
echo "创建第一个项目："
echo "1. 启动 Android Studio"
echo "2. New Project → Empty Activity"
echo "3. Language: Kotlin 或 Java"
echo "4. Minimum SDK: API 21 (Android 5.0)"
echo ""
