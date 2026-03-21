# GitHub Actions 自动打包指南

## 📦 自动打包配置

项目已配置 3 个自动打包工作流：

| 工作流 | 平台 | 输出 | 触发条件 |
|--------|------|------|----------|
| `build-android.yml` | Android | APK | 推送到 main |
| `build-windows-exe.yml` | Windows | EXE | 推送 + 手动触发 |
| `build-windows-exe.yml` | Windows | EXE + Release | 创建标签时 |

---

## 🚀 Windows EXE 自动打包

### 触发方式

**1. 推送代码自动打包**
```bash
git push origin main
```

**2. 手动触发**
1. 进入 https://github.com/youyi168/wuaibagua/actions
2. 选择 "Build Windows EXE" 工作流
3. 点击 "Run workflow"
4. 选择分支（默认 main）
5. 点击 "Run workflow" 按钮

**3. 创建发布版本（自动生成 Release）**
```bash
# 创建带标签的提交
git tag v2.4.0
git push origin v2.4.0
```

### 打包过程

工作流会执行以下步骤：

1. ✅ 检出代码
2. ✅ 设置 Python 3.10
3. ✅ 安装 Kivy 和依赖
4. ✅ 安装 PyInstaller
5. ✅ 验证项目结构
6. ✅ 打包为 EXE
7. ✅ 上传为 Artifact

### 获取打包结果

**方式 1：下载 Artifact（推荐）**

1. 打开工作流运行页面
2. 找到成功的运行（绿色勾）
3. 滚动到页面底部
4. 点击 "wuaibagua-windows-exe" 下载 EXE 文件
5. 文件有效期：30 天

**方式 2：从 Release 下载（标签触发）**

1. 进入 https://github.com/youyi168/wuaibagua/releases
2. 找到对应版本
3. 下载 `吾爱八卦.exe`

---

## 📱 Android APK 自动打包

### 触发方式

**推送代码自动打包**
```bash
git push origin main
```

### 获取打包结果

1. 打开 https://github.com/youyi168/wuaibagua/actions
2. 选择 "Build Android APK" 工作流
3. 找到最近的运行
4. 下载 "wuaibagua-apk" artifact

---

## ⚙️ 自定义配置

### 修改打包选项

编辑对应的工作流文件：

**Windows EXE:** `.github/workflows/build-windows-exe.yml`
**Android APK:** `.github/workflows/build-android.yml`

### 常见修改

#### 1. 添加程序图标（Windows）

```yaml
- name: Build EXE
  run: |
    pyinstaller `
      --icon=icon.ico `  # 添加这行
      ...
```

需要先上传 `icon.ico` 到项目根目录。

#### 2. 更改 Python 版本

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # 改为 3.11
```

#### 3. 延长超时时间

```yaml
jobs:
  build-windows:
    runs-on: windows-latest
    timeout-minutes: 30  # 默认 15 分钟，可调整
```

#### 4. 添加更多隐藏导入

```yaml
- name: Build EXE
  run: |
    pyinstaller `
      --hidden-import=your_module `
      ...
```

---

## 📊 工作流状态徽章

添加到 README.md：

```markdown
### 构建状态

[![Build Windows EXE](https://github.com/youyi168/wuaibagua/actions/workflows/build-windows-exe.yml/badge.svg)](https://github.com/youyi168/wuaibagua/actions/workflows/build-windows-exe.yml)
[![Build Android APK](https://github.com/youyi168/wuaibagua/actions/workflows/build-android.yml/badge.svg)](https://github.com/youyi168/wuaibagua/actions/workflows/build-android.yml)
```

显示效果：

[![Build Windows EXE](https://github.com/youyi168/wuaibagua/actions/workflows/build-windows-exe.yml/badge.svg)](https://github.com/youyi168/wuaibagua/actions/workflows/build-windows-exe.yml)
[![Build Android APK](https://github.com/youyi168/wuaibagua/actions/workflows/build-android.yml/badge.svg)](https://github.com/youyi168/wuaibagua/actions/workflows/build-android.yml)

---

## 🔧 故障排除

### 问题 1：打包失败

**查看日志：**
1. 打开工作流运行页面
2. 点击失败的步骤
3. 查看错误信息

**常见错误：**
- 缺少依赖 → 检查 `pip install` 步骤
- 文件路径错误 → 检查 `--add-data` 参数
- 内存不足 → 增加 `timeout-minutes`

### 问题 2：Artifact 找不到

**可能原因：**
- 打包失败
- 文件路径不正确
- 超过 30 天有效期

**解决：**
- 重新运行工作流
- 检查 `upload-artifact` 的 `path` 参数

### 问题 3：打包时间过长

**优化方法：**
1. 缓存 pip 依赖：
```yaml
- name: Cache pip
  uses: actions/cache@v4
  with:
    path: ~\AppData\Local\pip\Cache
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

2. 减少隐藏导入
3. 禁用 UPX 压缩（如果不需要）

---

## 💡 最佳实践

### 1. 使用标签发布版本

```bash
# 更新版本号
# 提交代码
git commit -am "release: v2.4.0"

# 创建标签
git tag v2.4.0

# 推送标签（触发 Release）
git push origin v2.4.0
```

### 2. 定期清理旧 Artifact

GitHub 会自动清理 90 天前的日志，但 Artifact 需要手动清理：

1. 进入仓库 Settings
2. 选择 Actions
3. 设置 "Artifact & Log Retention"

### 3. 使用矩阵构建（多版本）

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11']
    
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
```

---

## 📈 使用统计

查看工作流使用情况：

1. 进入仓库 → Actions
2. 点击工作流名称
3. 查看运行历史

---

## 🔗 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [PyInstaller 文档](https://pyinstaller.org/en/stable/)
- [Buildozer 文档](https://buildozer.readthedocs.io/)
- [actions/upload-artifact](https://github.com/actions/upload-artifact)

---

## 📝 注意事项

1. **免费额度**：GitHub Actions 每月有 2000 分钟免费额度
2. **文件大小**：单个 Artifact 最大 512 MB
3. **存储限制**：仓库总存储限制 10 GB
4. **并发限制**：免费账户最多 1 个并发任务

---

**最后更新**: 2026-03-18
**版本**: v2.4.0
