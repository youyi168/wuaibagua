#!/bin/bash
# 吾爱八卦 - APK 开发环境安装脚本
# 适用于 Ubuntu 22.04 / Debian 11+

set -e

echo "=========================================="
echo "  吾爱八卦 - APK 开发环境安装"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查是否以 root 运行
if [ "$EUID" -eq 0 ]; then
    error "请不要以 root 用户运行此脚本"
    exit 1
fi

# 1. 更新系统包
info "更新系统包..."
sudo apt-get update

# 2. 安装系统依赖
info "安装系统依赖..."
sudo apt-get install -y \
    git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev liblzma-dev \
    python3-pip python3-venv python3-dev \
    libffi-dev libssl-dev \
    automake cmake \
    wget curl

# 3. 配置 Java 环境
info "配置 Java 环境..."
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 写入 ~/.bashrc
if ! grep -q "JAVA_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# Java for Android Development
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
EOF
    info "Java 环境变量已添加到 ~/.bashrc"
fi

# 4. 安装/升级 Buildozer 和依赖
info "安装 Buildozer 和依赖..."
pip3 install --user --upgrade pip setuptools wheel
pip3 install --user buildozer cython virtualenv packaging

# 5. 安装国内镜像配置
info "配置 Python 镜像源（阿里云）..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
trusted-host = mirrors.aliyun.com
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# 6. 配置 Android SDK 镜像（使用清华镜像）
info "配置 Android SDK 镜像..."
export ANDROID_HOME=$HOME/.android/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

if ! grep -q "ANDROID_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# Android SDK
export ANDROID_HOME=$HOME/.android/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
EOF
    info "Android SDK 环境变量已添加到 ~/.bashrc"
fi

# 7. 验证安装
info "验证安装..."
echo ""
echo "=== Python ==="
python3 --version
pip3 --version

echo ""
echo "=== Java ==="
java -version 2>&1 | head -3

echo ""
echo "=== Buildozer ==="
which buildozer
buildozer --version

echo ""
echo "=== Cython ==="
cython --version | head -1

# 8. 创建项目虚拟环境（可选）
info "创建项目虚拟环境..."
cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    info "虚拟环境已创建：venv/"
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install --upgrade pip
pip install kivy buildozer cython

echo ""
echo "=========================================="
info "安装完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 重新加载环境变量：source ~/.bashrc"
echo "2. 进入项目目录：cd $(dirname "$0")"
echo "3. 激活虚拟环境：source venv/bin/activate"
echo "4. 首次编译：buildozer android debug"
echo ""
echo "注意："
echo "- 首次编译需要下载 Android SDK/NDK（约 2-3GB）"
echo "- 编译时间约 30-40 分钟"
echo "- 确保有足够的磁盘空间（建议 10GB+）"
echo ""
