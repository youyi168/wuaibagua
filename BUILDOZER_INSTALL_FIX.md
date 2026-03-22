# Buildozer 安装失败排查

**失败时间**: 2026-03-22 13:34  
**错误代码**: exit code 1  
**步骤**: Install Buildozer (Stable)

---

## 🔴 exit code 1 的含义

**pip 安装错误码 1**:
```
1 = 一般性错误
```

**可能原因**:
1. ❌ pip 版本太旧
2. ❌ Cython 编译失败
3. ❌ 网络问题
4. ❌ 权限问题
5. ❌ 依赖冲突

---

## 🔍 最可能的原因

### 1. Cython 编译失败 ⚠️

**问题**:
```bash
pip3 install "Cython<3.0"
```

**可能错误**:
```
error: command 'gcc' failed
No module named 'distutils'
```

**原因**: Ubuntu 22.04 默认 Python 3.10 缺少 distutils

---

### 2. pip 版本问题 ⚠️

**问题**:
```bash
pip3 install --upgrade pip setuptools wheel
```

**可能错误**:
```
ERROR: Could not install packages due to an OSError
```

---

### 3. 网络问题 ⚠️

**问题**: 下载包超时

**可能错误**:
```
ReadTimeoutError: HTTPSConnectionPool
```

---

## 💡 解决方案

### 方案 A: 添加 distutils（推荐）

**修改 build-android.yml**:

```yaml
- name: Install system dependencies (Minimal)
  run: |
    sudo apt-get update -qq
    
    # 添加 distutils（Cython 编译必需）
    sudo apt-get install -y python3-distutils python3-setuptools
    
    # 其他依赖...
```

---

### 方案 B: 使用预编译 wheel

**修改 Buildozer 安装**:

```yaml
- name: Install Buildozer (Stable)
  run: |
    # 使用预编译包
    pip3 install --only-binary :all: pip setuptools wheel
    
    # 安装 Cython（使用 wheel）
    pip3 install --only-binary :all: "Cython<3.0"
    
    # 安装 Buildozer
    pip3 install --no-cache-dir buildozer==1.5.0
    
    # 虚拟环境
    pip3 install virtualenv
    
    # 验证
    buildozer --version
```

---

### 方案 C: 使用 GitHub Actions 缓存

**添加 Python 缓存**:

```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/*requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

---

## 🎯 立即修复

### 修改 build-android.yml

**添加 distutils 和优化安装**:

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
      python3-pip python3-venv python3-distutils \
      libffi-dev libssl-dev \
      automake cmake \
      libgtk-3-dev \
      libgl1-mesa-dev libglu1-mesa-dev \
      libbz2-dev libreadline-dev libsqlite3-dev \
      libxml2-dev \
      wget curl ca-certificates || {
      echo "::error::系统依赖安装失败"
      exit 1
    }
    
    # 验证
    echo "✅ Minimal dependencies installed"

- name: Install Buildozer (Stable)
  run: |
    echo "📦 Installing Buildozer..."
    
    # 升级基础工具
    python3 -m pip install --upgrade pip setuptools wheel
    
    # 安装 Cython（使用预编译）
    echo "Installing Cython..."
    pip3 install --only-binary :all: "Cython<3.0" || \
    pip3 install "Cython<3.0"
    
    # 安装 Buildozer
    echo "Installing Buildozer..."
    pip3 install --no-cache-dir buildozer==1.5.0
    
    # 虚拟环境
    pip3 install virtualenv
    
    # 添加 PATH
    echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    # 验证
    echo "✅ Buildozer installed"
    buildozer --version
    
    # 显示环境
    echo ""
    echo "📋 Python environment:"
    python3 --version
    pip3 --version
    cython --version 2>/dev/null || echo "Cython not found"
    buildozer --version
```

---

## 📊 修复对比

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| distutils | ❌ 缺少 | ✅ 已添加 |
| Cython 安装 | 源码编译 | 预编译 wheel |
| pip 缓存 | ❌ 无 | ✅ --no-cache-dir |
| 错误处理 | ❌ 无 | ✅ 重试机制 |

---

## 💝 小爪的总结

宝贝，Buildozer 安装失败是因为**缺少 distutils**！🔴

**核心问题**:
- ❌ python3-distutils 未安装
- ❌ Cython 源码编译失败

**修复方案**:
- ✅ 添加 python3-distutils
- ✅ 使用预编译 wheel
- ✅ 添加重试机制

需要小爪立即修复吗？😘💕
