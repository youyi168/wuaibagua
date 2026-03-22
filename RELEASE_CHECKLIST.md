# 版本发布检查清单

**目的**: 确保每次版本更新时，所有相关配置都同步更新，避免构建失败

**最后更新**: 2026-03-22 (v1.6.0)

---

## 📋 发布前检查清单

### 1. 版本号更新 ✅

**必须更新的文件**:

| 文件 | 位置 | 更新内容 | 检查人 |
|------|------|---------|--------|
| buildozer.spec | 根目录 | `version = X.Y.Z` | 开发者 |
| wuaibagua_kivy.py | 根目录 | `Config.VERSION = 'X.Y.Z'` | 开发者 |
| README.md | 根目录 | 标题和更新日志 | 开发者 |
| CHANGELOG.md | 根目录 | 新增版本记录 | 开发者 |

**检查命令**:
```bash
# 检查版本号是否一致
grep -r "version.*1\." buildozer.spec wuaibagua_kivy.py README.md
```

---

### 2. 新增模块检查 ✅

**检查是否有新增的 `.py` 文件**:

```bash
# 列出所有 Python 文件
find . -name "*.py" -type f | sort

# 检查是否都在版本控制中
git status
```

**新增模块清单** (v1.6.0):
- [x] animation.py (v1.5.0)
- [x] favorite.py (v1.5.0)
- [x] statistics.py (v1.5.0)
- [x] sound.py (v1.6.0)
- [x] reminder.py (v1.6.0)
- [x] quick_topic.py (v1.4.0)
- [x] interpreter.py (v1.4.0)
- [x] compact_gua.py (v1.2.5)
- [x] user.py (v1.3.2)
- [x] copy.py (v1.3.1)
- [x] history_screen.py (v1.3.0)

---

### 3. 资源文件检查 ✅

**检查新增的资源文件**:

| 类型 | 目录 | 扩展名 | buildozer.spec 配置 |
|------|------|--------|-------------------|
| 数据文件 | data/ | .txt | source.include_dirs = data |
| 字体文件 | fonts/ | .ttf | source.include_dirs = fonts |
| 音效文件 | sounds/ | .mp3,.ogg,.wav | source.include_exts = ...,mp3,ogg,wav |
| 图片文件 | 根目录/ | .png,.jpg | source.include_exts = ...,png,jpg |

**当前配置** (v1.6.0):
```ini
source.include_exts = py,png,jpg,kv,atlas,txt,json,ttf,svg,mp3,ogg,wav
source.include_dirs = data,fonts,sounds
```

**检查命令**:
```bash
# 检查资源目录
ls -la data/ fonts/ sounds/

# 检查新增文件
git status --porcelain | grep -E "\.(png|jpg|ttf|mp3|wav|ogg)$"
```

---

### 4. GitHub Actions 工作流检查 ✅

**检查文件**:
- `.github/workflows/build-android.yml`
- `.github/workflows/build-windows-exe.yml`

**检查项**:
- [ ] 工作流配置是否为最新
- [ ] APK 查找路径是否正确
- [ ] 上传配置是否正确
- [ ] Release 配置是否正确

**最新版本**: v1.6.0 (2026-03-22 重构)

**关键配置**:
```yaml
# APK 查找路径
BUILD_DIR=".buildozer/android/bin"
RELEASE_DIR="release"

# 查找逻辑:
1. Buildozer 标准输出目录
2. bin 目录（兼容）
3. 全局查找（排除 .buildozer）
```

---

### 5. 依赖检查 ✅

**检查文件**:
- `requirements-win.txt` (Windows)
- `buildozer.spec` (Android)

**检查命令**:
```bash
# 检查 Windows 依赖
cat requirements-win.txt

# 检查 Android 依赖
cat buildozer.spec | grep -E "^requirements"
```

**当前依赖** (v1.6.0):
```txt
# Windows
kivy==2.3.0
pyinstaller==6.5.0

# Android
python3,kivy
```

---

### 6. Git 标签检查 ✅

**创建标签**:
```bash
# 创建版本标签
git tag -a vX.Y.Z -m "vX.Y.Z - 版本名称"

# 推送标签
git push origin main --tags
```

**标签命名规范**:
- 格式：`v主版本。次版本.修订号`
- 示例：`v1.6.0`
- 说明：`v1.6.0 - 完美版`

---

### 7. 文档更新检查 ✅

**必须更新的文档**:

| 文档 | 更新内容 | 优先级 |
|------|---------|--------|
| README.md | 版本号、更新日志、功能说明 | P0 |
| CHANGELOG.md | 新增版本记录 | P0 |
| APK_BUILD_FIX.md | 构建配置说明 | P1 |
| RELEASE_CHECKLIST.md | 本检查清单 | P1 |

---

### 8. 构建测试 ✅

**本地测试** (可选):
```bash
# Windows EXE
pyinstaller wuaibagua.spec

# Android APK (需要 Linux)
buildozer android debug
```

**GitHub Actions 测试**:
1. 推送代码到 GitHub
2. 访问 https://github.com/youyi168/wuaibagua/actions
3. 查看构建状态
4. 下载 APK 测试

---

## 🚀 发布流程

### Step 1: 准备发布
```bash
# 1. 更新版本号
# 2. 更新文档
# 3. 提交更改
git add -A
git commit -m "release: v1.6.0 - 完美版"
```

### Step 2: 创建标签
```bash
# 创建版本标签
git tag -a v1.6.0 -m "v1.6.0 - 完美版"

# 推送代码和标签
git push origin main --tags
```

### Step 3: 监控构建
```
1. 访问 https://github.com/youyi168/wuaibagua/actions
2. 查看 "Build Android APK" 和 "Build Windows EXE"
3. 等待构建完成（绿色 ✓）
4. 检查 APK 是否生成
```

### Step 4: 验证发布
```
1. 访问 https://github.com/youyi168/wuaibagua/releases
2. 检查 v1.6.0 是否创建
3. 检查 APK 文件是否上传
4. 下载测试
```

### Step 5: 通知用户
```
1. 更新 README 下载链接
2. 发布更新公告
3. 回复用户反馈
```

---

## ⚠️ 常见问题

### Q1: 构建成功但找不到 APK

**原因**: APK 查找路径不对

**解决**: 
1. 检查 `.buildozer/android/bin/` 目录
2. 查看构建日志中的 "Searching for APK files"
3. 确认 `build-android.yml` 配置正确

### Q2: 版本号不一致

**原因**: 忘记更新某个文件

**解决**:
```bash
# 检查所有文件中的版本号
grep -r "1\.6\.0" . --include="*.spec" --include="*.py" --include="*.md"
```

### Q3: 新增模块未打包

**原因**: 未添加到版本控制或配置

**解决**:
```bash
# 检查文件是否在 Git 中
git ls-files | grep "\.py$"

# 检查 buildozer.spec 配置
cat buildozer.spec | grep "source\."
```

### Q4: Release 未自动创建

**原因**: tag 推送失败或工作流配置问题

**解决**:
1. 检查 tag 是否存在：`git tag -l`
2. 检查 tag 是否推送：`git push origin --tags`
3. 检查 GitHub Actions 日志

---

## 📊 版本历史

| 版本 | 日期 | 构建状态 | 备注 |
|------|------|---------|------|
| v1.6.0 | 2026-03-22 | ✅ 已重构 | 完美版 |
| v1.5.0 | 2026-03-22 | ✅ | 视觉增强版 |
| v1.4.0 | 2026-03-22 | ✅ | 解读增强版 |
| v1.3.2 | 2026-03-22 | ✅ | 个性化运势版 |
| v1.3.1 | 2026-03-22 | ✅ | 体验优化版 |
| v1.3.0 | 2026-03-22 | ✅ | 历史记录版 |

---

## 🎯 负责人

- **开发者**: 更新代码和版本号
- **测试者**: 验证构建和下载
- **发布人**: 创建 Release 和通知

---

## 📝 更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-03-22 | v1.6.0 | 初始版本，完整重构构建流程 | 小爪 |

---

**重要提醒**: 
- ⚠️ 每次版本更新**必须**更新此检查清单
- ⚠️ 每次新增模块**必须**检查 buildozer.spec 配置
- ⚠️ 每次构建失败**必须**查看日志并修复

---

**维护人**: 小爪 💕  
**最后更新**: 2026-03-22  
**下次检查**: 下次版本发布时
