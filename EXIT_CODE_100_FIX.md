# 系统依赖安装失败排查

**失败时间**: 2026-03-22 13:29  
**错误代码**: exit code 100  
**步骤**: Install system dependencies (Complete)

---

## 🔴 exit code 100 的含义

**apt-get/dpkg 错误码 100**:
```
100 = 依赖关系问题或包冲突
```

**可能原因**:
1. ❌ 包名错误或不存在的包
2. ❌ 依赖冲突
3. ❌ 磁盘空间不足
4. ❌ 软件源问题

---

## 🔍 最可能的原因

### 1. 包名错误 ⚠️

**检查问题包**:
```bash
# 可能不存在的包
libxmlsec1-dev  # 这个包名可能不对
gstreamer1.0-plugins-base  # 可能需要 -gstreamer 前缀
```

**正确的包名**:
```bash
libxmlsec1-dev → libxmlsec1-dev (正确)
gstreamer1.0-plugins-base → gstreamer1.0-plugins-base (正确)
gstreamer1.0-plugins-good → gstreamer1.0-plugins-good (正确)
```

---

### 2. 包冲突 ⚠️

**Ubuntu 22.04 特有**:
```bash
# libgl1-mesa-dev 可能与其他包冲突
# gstreamer 可能有版本冲突
```

---

### 3. 软件源问题 ⚠️

**可能原因**:
```bash
# 某些包不在 main 仓库
# 需要启用 universe/multiverse 仓库
```

---

## 💡 解决方案

### 方案 A: 精简依赖（推荐）

**只安装 Buildozer 必需的依赖**:

```yaml
- name: Install system dependencies (Minimal)
  run: |
    echo "📦 Installing minimal system dependencies..."
    
    sudo apt-get update -qq
    
    # Buildozer 核心依赖
    sudo apt-get install -y --no-install-recommends \
      git zip unzip \
      autoconf libtool pkg-config \
      zlib1g-dev libncurses5-dev libncursesw5-dev liblzma-dev \
      python3-pip python3-venv \
      libffi-dev libssl-dev \
      automake cmake \
      libgtk-3-dev \
      libgl1-mesa-dev libglu1-mesa-dev \
      libbz2-dev libreadline-dev libsqlite3-dev \
      libxml2-dev \
      wget curl ca-certificates
    
    echo "✅ Minimal dependencies installed"
```

**移除的包**:
```bash
# 移除可能冲突的包
- libxmlsec1-dev       # 可能不存在
- gstreamer1.0-dev     # 可选，非必需
- gstreamer1.0-plugins-base  # 可选
- gstreamer1.0-plugins-good  # 可选
- xz-utils             # 已包含在 liblzma-dev
- tk-dev               # 非必需
```

---

### 方案 B: 分步安装

**分批安装依赖，定位问题包**:

```yaml
- name: Install system dependencies (Step 1)
  run: |
    sudo apt-get update -qq
    sudo apt-get install -y --no-install-recommends \
      git zip unzip \
      autoconf libtool pkg-config \
      zlib1g-dev libncurses5-dev libncursesw5-dev liblzma-dev \
      python3-pip python3-venv \
      libffi-dev libssl-dev \
      automake cmake
    
- name: Install system dependencies (Step 2)
  run: |
    sudo apt-get install -y --no-install-recommends \
      libgtk-3-dev \
      libgl1-mesa-dev libglu1-mesa-dev \
      libbz2-dev libreadline-dev libsqlite3-dev \
      libxml2-dev \
      wget curl ca-certificates
    
- name: Install system dependencies (Step 3 - Optional)
  run: |
    # 可选依赖，失败不影响构建
    sudo apt-get install -y --no-install-recommends \
      libgstreamer1.0-dev \
      gstreamer1.0-plugins-base \
      gstreamer1.0-plugins-good || echo "⚠️ GStreamer installation failed, skipping..."
```

---

### 方案 C: 启用所有仓库

**确保所有仓库都启用**:

```yaml
- name: Enable all Ubuntu repositories
  run: |
    sudo add-apt-repository main
    sudo add-apt-repository universe
    sudo add-apt-repository multiverse
    sudo add-apt-repository restricted
    sudo apt-get update -qq
```

---

## 🎯 立即修复

### 修改 build-android.yml

**使用精简依赖方案**:

```yaml
- name: Install system dependencies (Minimal)
  run: |
    echo "📦 Installing minimal system dependencies..."
    
    sudo apt-get update -qq
    
    # 核心依赖（Buildozer 必需）
    sudo apt-get install -y --no-install-recommends \
      git zip unzip \
      autoconf libtool pkg-config \
      zlib1g-dev libncurses5-dev libncursesw5-dev liblzma-dev \
      python3-pip python3-venv \
      libffi-dev libssl-dev \
      automake cmake \
      libgtk-3-dev \
      libgl1-mesa-dev libglu1-mesa-dev \
      libbz2-dev libreadline-dev libsqlite3-dev \
      libxml2-dev \
      wget curl ca-certificates
    
    # 验证安装
    echo ""
    echo "📋 Verifying:"
    echo "  git: $(git --version)"
    echo "  cmake: $(cmake --version | head -1)"
    echo "  python3: $(python3 --version)"
    
    echo "✅ Minimal dependencies installed"
```

---

## 📊 依赖分类

### 必需依赖（必须安装）

```bash
# 版本控制
git

# 压缩工具
zip unzip

# 构建工具
autoconf libtool pkg-config automake cmake

# Python
python3-pip python3-venv

# 开发库
zlib1g-dev libncurses5-dev libncursesw5-dev liblzma-dev
libffi-dev libssl-dev
libbz2-dev libreadline-dev libsqlite3-dev
libxml2-dev

# GUI
libgtk-3-dev
libgl1-mesa-dev libglu1-mesa-dev

# 网络
wget curl ca-certificates
```

### 可选依赖（非必需）

```bash
# 多媒体（GStreamer）
libgstreamer1.0-dev
gstreamer1.0-plugins-base
gstreamer1.0-plugins-good

# XML 安全
libxmlsec1-dev

# Tk
tk-dev
```

---

## 💝 小爪的总结

宝贝，exit code 100 是**依赖关系问题**！🔴

**最可能原因**:
- ❌ libxmlsec1-dev 包名问题
- ❌ gstreamer 包冲突
- ❌ 某些包不在 main 仓库

**修复方案**:
- ✅ 移除非必需依赖
- ✅ 精简到最小必需集合
- ✅ 分步安装定位问题

需要小爪立即修复吗？😘💕
