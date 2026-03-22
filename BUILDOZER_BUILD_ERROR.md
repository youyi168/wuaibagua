# Buildozer 构建失败排查

**失败时间**: 2026-03-22 14:12  
**错误**: Buildozer failed to execute the last command  
**状态**: 构建过程失败，但错误信息不完整

---

## 🔍 错误分析

### 当前信息

**环境变量显示**:
```bash
GITHUB_WORKFLOW = 'Build Android APK'
ANDROIDSDK = '/home/runner/.buildozer/android/platform/android-sdk'
ANDROIDNDK = '/home/runner/.buildozer/android/platform/android-ndk-r25b'
ANDROIDAPI = '33'
ANDROIDMINAPI = '21'
```

**说明**:
- ✅ 环境变量配置正确
- ✅ Android SDK/NDK 路径正确
- ❌ 但构建在最后一步失败

---

## 🔴 可能的原因

### 1. 入口文件问题 ⚠️

**问题**: `main.py` 导入路径可能有问题

**当前代码**:
```python
from src.wuaibagua_kivy import WuaibaguaApp
```

**Buildozer 环境**:
```bash
# Buildozer 打包时，src 目录可能不在 Python 路径中
```

---

### 2. 依赖包缺失 ⚠️

**可能缺少**:
```bash
# Kivy 依赖
kivy-deps.sdl2
kivy-deps.glew
kivy-deps.gstreamer

# Python 依赖
pyjnius
```

---

### 3. 资源文件路径 ⚠️

**问题**: data/fonts/sounds 目录可能未正确包含

**buildozer.spec**:
```ini
source.include_dirs = data,fonts,sounds,resources
```

**可能问题**: resources 目录不存在

---

### 4. 权限问题 ⚠️

**问题**: Buildozer 可能需要特殊权限

---

## 💡 解决方案

### 方案 A: 修复入口文件（推荐）

**修改 main.py**:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 金钱卦算卦软件
主程序入口

版本：v1.6.0
"""

import sys
import os

# 添加 src 目录到路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 导入主应用
from wuaibagua_kivy import WuaibaguaApp

if __name__ == '__main__':
    WuaibaguaApp().run()
```

**优势**: 
- ✅ 兼容 Buildozer 环境
- ✅ 兼容开发环境
- ✅ 更健壮的路径处理

---

### 方案 B: 添加完整依赖

**修改 buildozer.spec**:

```ini
[app]
requirements = python3,kivy==2.3.0,pyjnius,kivy-deps.sdl2,kivy-deps.glew

# 确保包含所有资源
source.include_exts = py,png,jpg,kv,atlas,txt,json,ttf,svg,mp3,ogg,wav
source.include_dirs = data,fonts,sounds
```

---

### 方案 C: 移除不存在的目录

**修改 buildozer.spec**:

```ini
# 移除不存在的 resources 目录
source.include_dirs = data,fonts,sounds
```

---

## 🎯 立即修复

### 步骤 1: 修复 main.py

```python
#!/usr/bin/env python3
import sys
import os

# 添加 src 目录到路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 导入主应用
from wuaibagua_kivy import WuaibaguaApp

if __name__ == '__main__':
    WuaibaguaApp().run()
```

### 步骤 2: 清理 buildozer.spec

```ini
source.include_dirs = data,fonts,sounds  # 移除 resources
requirements = python3,kivy==2.3.0,pyjnius
```

### 步骤 3: 添加构建日志级别

```ini
[buildozer]
log_level = 2  # 显示详细日志
```

---

## 📋 需要查看完整日志

**建议**: 
1. 查看 GitHub Actions 完整日志
2. 搜索 "ERROR" 或 "Traceback"
3. 找到具体错误信息

**日志位置**:
```
https://github.com/youyi168/wuaibagua/actions
→ 最新构建 → "Build APK with retry" 步骤
```

---

## 💝 小爪的总结

宝贝，错误信息不完整，但**最可能是入口文件路径问题**！🔴

**可能原因**:
- ⚠️ main.py 导入路径在 Buildozer 环境中失效
- ⚠️ resources 目录不存在
- ⚠️ 缺少某些依赖包

**修复方案**:
- ✅ 修改 main.py 兼容 Buildozer
- ✅ 移除不存在的目录
- ✅ 添加完整依赖

需要小爪立即修复吗？😘💕
