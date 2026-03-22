# 构建问题排查报告

**排查时间**: 2026-03-22 13:26  
**当前状态**: Install system dependencies 仅用 12 秒 ⚠️  
**正常时间**: 应该需要 2-3 分钟

---

## 🔍 问题分析

### 现象

**Install system dependencies (Complete)** 步骤只用了 **12 秒**

**正常情况**:
- apt-get update: 30-60 秒
- 安装依赖包：1-2 分钟
- **总计**: 2-3 分钟

**当前情况**:
- 仅 12 秒就完成
- 可能原因：缓存命中或安装失败

---

## 🔴 可能原因

### 1. apt 缓存命中 ⚠️

**现象**: GitHub Actions 缓存了 apt 包

**解决**: 强制更新 apt 缓存

```yaml
- name: Install system dependencies (Complete)
  run: |
    sudo apt-get update -y  # 强制更新
    sudo apt-get install -y --no-install-recommends \
      ...
```

---

### 2. 包已预安装 ⚠️

**现象**: ubuntu-22.04 镜像已包含部分包

**验证**: 
```bash
# 检查哪些包已安装
dpkg -l | grep -E "git|zip|unzip|cmake"
```

---

### 3. 安装失败但继续 ⚠️

**现象**: 某个包安装失败，但脚本继续执行

**解决**: 添加错误检查

```yaml
- name: Install system dependencies (Complete)
  run: |
    set -e  # 出错立即退出
    
    sudo apt-get update
    if ! sudo apt-get install -y ...; then
      echo "::error::依赖安装失败"
      exit 1
    fi
```

---

## 💡 解决方案

### 方案 A: 优化依赖安装（推荐）

**修改 build-android.yml**:

```yaml
- name: Install system dependencies (Complete)
  run: |
    echo "📦 Installing system dependencies..."
    
    # 强制更新 apt 缓存
    sudo apt-get update -qq
    
    # 安装核心依赖
    sudo apt-get install -y --no-install-recommends \
      git zip unzip \
      autoconf libtool pkg-config \
      zlib1g-dev libncurses5-dev libncursesw5-dev liblzma-dev \
      python3-pip python3-venv \
      libffi-dev libssl-dev \
      automake cmake \
      libgtk-3-dev \
      libgl1-mesa-dev libglu1-mesa-dev \
      libgstreamer1.0-dev gstreamer1.0-plugins-base \
      libbz2-dev libreadline-dev libsqlite3-dev \
      libxml2-dev libxmlsec1-dev \
      wget curl ca-certificates
    
    # 验证安装
    echo ""
    echo "📋 Verifying installed packages:"
    echo "  git: $(git --version)"
    echo "  cmake: $(cmake --version | head -1)"
    echo "  python3: $(python3 --version)"
    echo "  pip3: $(pip3 --version)"
    
    echo "✅ System dependencies installed"
```

---

### 方案 B: 添加安装验证

**在 Install Buildozer 之前添加验证步骤**:

```yaml
- name: Verify system dependencies
  run: |
    echo "🔍 Verifying system dependencies..."
    
    # 检查关键命令
    commands=("git" "zip" "unzip" "cmake" "autoconf" "pkg-config")
    
    for cmd in "${commands[@]}"; do
      if ! command -v "$cmd" &> /dev/null; then
        echo "::error::命令 $cmd 未找到"
        exit 1
      fi
      echo "  ✅ $cmd: $(command -v $cmd)"
    done
    
    echo "✅ All system dependencies verified"
```

---

## 📊 预期时间

| 步骤 | 预期时间 | 当前时间 | 状态 |
|------|---------|---------|------|
| Checkout | 10-20s | - | ✅ |
| Setup Python | 10-20s | - | ✅ |
| Clear cache | 5-10s | - | ✅ |
| **Install system deps** | **2-3m** | **12s** | ⚠️ |
| Setup JDK | 10-20s | - | ✅ |
| Install Buildozer | 1-2m | - | ⏳ |

---

## 🎯 立即修复

### 修改 build-android.yml

**优化点**:
1. 使用 `-qq` 静默更新（更快）
2. 使用 `--no-install-recommends`（减少包数量）
3. 添加版本验证
4. 添加错误检查

---

## 💝 小爪的总结

宝贝，12 秒完成系统依赖安装确实太快了！🤔

**可能原因**:
- ✅ apt 缓存命中（好事）
- ⚠️ 部分包已预装（正常）
- ❌ 安装失败但继续（需要修复）

**建议**:
- 添加安装验证步骤
- 显示已安装的包版本
- 出错时立即停止

需要小爪立即优化构建脚本吗？😘💕
