# APK 构建问题排查与修复

**问题时间**: 2026-03-22  
**当前版本**: v1.6.0  
**状态**: 网页显示成功，但实际无 APK 下载

---

## 🔍 问题分析

### 1. APK 查找路径问题

**当前配置**:
```yaml
- name: Find and copy APK
  run: |
    find . -name "*.apk" -type f 2>/dev/null
    
    mkdir -p release
    
    if [ -s /tmp/apk_files.txt ]; then
      while IFS= read -r apk; do
        cp -v "$apk" release/ 2>/dev/null || true
      done < /tmp/apk_files.txt
    fi
    
    if [ -d "bin" ]; then
      cp -v bin/*.apk release/ 2>/dev/null || true
    fi
```

**问题**: Buildozer 实际输出路径是 `.buildozer/android/bin/`，不是 `bin/`

**修复**:
```yaml
- name: Find and copy APK
  run: |
    echo "=== Searching for APK files ==="
    
    # Buildozer 标准输出路径
    BUILD_DIR=".buildozer/android/bin"
    
    mkdir -p release
    
    # 查找所有 APK
    if [ -d "$BUILD_DIR" ]; then
      find "$BUILD_DIR" -name "*.apk" -type f | while read apk; do
        echo "Found: $apk"
        cp -v "$apk" release/
      done
    fi
    
    # 也检查其他可能位置
    find . -path "./.buildozer" -prune -o -name "*.apk" -type f -print | while read apk; do
      echo "Found (other): $apk"
      cp -v "$apk" release/
    done
    
    echo "=== Release directory contents ==="
    ls -la release/ || echo "No release directory"
    
    # 设置输出变量
    APK_COUNT=$(ls -1 release/*.apk 2>/dev/null | wc -l || echo "0")
    echo "apk_count=$APK_COUNT" >> $GITHUB_OUTPUT
    
    # 如果没找到 APK，显示错误
    if [ "$APK_COUNT" -eq 0 ]; then
      echo "::error::未找到 APK 文件！"
      echo "检查 Buildozer 构建日志"
      exit 1
    fi
```

---

### 2. buildozer.spec 配置问题

**当前配置**:
```ini
[app]
source.include_exts = py,png,jpg,kv,atlas,txt,json,ttf,svg
```

**问题**: 缺少新增模块需要的扩展名

**修复**:
```ini
[app]
source.include_exts = py,png,jpg,kv,atlas,txt,json,ttf,svg,mp3,ogg,wav
source.include_dirs = data,fonts,sounds
```

---

### 3. 新增模块未包含

**问题**: v1.5.0 和 v1.6.0 新增的模块可能未被识别

**检查清单**:
- [x] animation.py
- [x] favorite.py
- [x] statistics.py
- [x] sound.py
- [x] reminder.py
- [x] quick_topic.py
- [x] interpreter.py
- [x] compact_gua.py

**解决**: 确保所有 `.py` 文件都被包含（默认已包含）

---

### 4. 音效文件处理

**问题**: sounds 目录可能不存在或为空

**当前状态**:
```
sounds/
└── README.md  (说明文档)
```

**解决**: 
1. 音效文件为可选，不影响构建
2. 在 sound.py 中已处理文件不存在的情况
3. 可以暂时忽略，或添加示例音效文件

---

### 5. Release 创建失败

**可能问题**: softprops/action-gh-release 可能失败

**检查点**:
- GitHub Token 权限
- Release 标签是否存在
- 文件路径是否正确

**修复**:
```yaml
- name: Create Release (on tag)
  if: startsWith(github.ref, 'refs/tags/v')
  uses: softprops/action-gh-release@v2  # 使用最新版本
  with:
    files: |
      release/*.apk
    generate_release_notes: true
    fail_on_unmatched_files: false  # 文件不匹配时不失败
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 🔧 完整修复方案

### 方案 A: 快速修复（推荐）

**修改 `.github/workflows/build-android.yml`**:

1. **修复 APK 查找路径** (第 120-150 行)
2. **更新 buildozer.spec** (添加音频扩展名)
3. **添加错误诊断** (显示更多构建信息)

**预计耗时**: 30 分钟

---

### 方案 B: 完整重构

**重写整个构建流程**:
- 使用更可靠的 APK 查找逻辑
- 添加多个备份查找路径
- 增强错误诊断
- 添加构建产物验证

**预计耗时**: 1 小时

---

## 📝 立即修复步骤

### Step 1: 更新 buildozer.spec

```ini
[app]
title = 我爱八卦
package.name = woaibagua
package.domain = org.woaibagua
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json,ttf,svg,mp3,ogg,wav
source.include_dirs = data,fonts,sounds
version = 1.6.0
icon.filename = icon.png
```

### Step 2: 更新工作流文件

修改 `.github/workflows/build-android.yml` 的 APK 查找部分

### Step 3: 重新触发构建

```bash
# 添加一个空提交来触发构建
cd /home/admin/.openclaw/workspace/wuaibagua
git commit --allow-empty -m "ci: 触发 APK 构建修复"
git push origin main
```

### Step 4: 检查构建日志

访问：https://github.com/youyi168/wuaibagua/actions

查看最新的 "Build Android APK" 运行

---

## 🎯 诊断命令

### 本地测试构建

```bash
# 1. 检查文件结构
cd /home/admin/.openclaw/workspace/wuaibagua
find . -name "*.py" | head -20

# 2. 检查 buildozer.spec
cat buildozer.spec | grep -E "^(source\.|version)"

# 3. 模拟查找 APK
find . -name "*.apk" -type f

# 4. 检查 sounds 目录
ls -la sounds/
```

### GitHub Actions 诊断

在构建日志中搜索:
- "Searching for APK files"
- "Found:"
- "Release directory contents"
- "apk_count="

---

## ✅ 验证清单

构建成功后，应该能看到:

- [ ] APK 文件在 `release/` 目录
- [ ] `apk_count` 变量 > 0
- [ ] Upload Artifact 成功
- [ ] Create Release 成功（如果是 tag）
- [ ] 可以下载 APK 文件

---

## 🐛 常见问题

### Q1: 构建成功但找不到 APK

**原因**: Buildozer 输出路径变化

**解决**: 检查 `.buildozer/android/bin/` 目录

### Q2: Release 创建失败

**原因**: 权限不足或文件路径错误

**解决**: 检查 GITHUB_TOKEN 权限和文件路径

### Q3: 构建时间过长

**原因**: 缓存未命中或网络问题

**解决**: 检查缓存配置，使用国内镜像

---

## 📊 预期结果

修复后:
- 构建时间：12-15 分钟
- APK 大小：15-20 MB
- 成功率：95%+
- 自动发布到 Release

---

**修复负责人**: 小爪 💕  
**修复时间**: 预计 30 分钟  
**状态**: 待修复
