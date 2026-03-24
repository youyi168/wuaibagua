# v1.1.1 功能说明

## 📋 版本信息

- **版本号**: v1.1.1
- **发布日期**: 2026-03-24
- **平台**: Android
- **构建**: GitHub Actions

---

## ✨ 新增功能

### 1. 本地卦象解释 ⭐⭐⭐⭐⭐

**功能描述**:
- 内置 64 卦完整数据，无需联网
- 每卦包含：卦辞、爻辞、白话解释
- 一键查看卦象详细解释
- 支持卦名搜索

**使用方法**:
1. 起卦后，点击"查看解释"按钮
2. 弹窗显示卦象完整解释
3. 包含卦辞、爻辞、白话解释

**数据来源**:
- 《周易》原文
- 白话解释（ simplified）
- 数据来源：`gua_interpret.py`

**技术实现**:
```python
# 卦象数据文件
gua_interpret.py (856 行)
- GUA_DATA: 64 卦数据字典
- get_gua_interpret(): 获取卦象解释
- search_gua(): 搜索卦象
```

---

### 2. 长按复制功能 ⭐⭐⭐⭐⭐

**功能描述**:
- 长按卦象文本 0.8 秒触发复制
- Android 原生剪贴板支持
- 复制成功显示 Toast 提示
- 桌面端 fallback 支持

**使用方法**:
1. 起卦后，长按"长按复制"按钮 0.8 秒
2. 自动复制卦象文本到剪贴板
3. 显示"✅ 已复制到剪贴板"提示

**技术实现**:
```python
# 长按复制组件
- LongPressBehavior: 长按行为 Mixin
- LongPressButton: 长按按钮
- CopyableLabel: 可长按复制的标签
- copy_to_clipboard(): 剪贴板复制函数
- show_toast(): Toast 提示函数
```

**Android API**:
```python
# 使用 jnius 调用 Android 原生 API
from jnius import autoclass

Context = autoclass('android.content.Context')
ClipboardManager = autoclass('android.content.ClipboardManager')
ClipData = autoclass('android.content.ClipData')
```

---

## 🐛 问题修复

### 1. copy.py 命名冲突
- **问题**: 与 Python 标准库冲突
- **修复**: 重命名为 `long_press_button.py` 并排除

### 2. Windows 代码清理
- **问题**: 代码冗余，维护成本高
- **修复**: 删除所有 Windows 相关代码（3640 行）
- **影响**: 专注 Android 平台，简化代码库

---

## 📦 构建配置

### buildozer.spec
```ini
[app]
version = 1.1.1
requirements = python3,kivy==2.1.0,pyjnius
source.exclude_patterns = copy.py,long_press_button.py
```

### GitHub Actions
```yaml
- name: Install Buildozer and dependencies
  run: |
    pip3 install Cython==0.29.36
    pip3 install --no-cache-dir buildozer==1.5.0
    pip3 install Kivy==2.1.0
```

---

## 📱 使用说明

### 起卦
1. 打开应用
2. 选择"电脑起卦"或"手动起卦"
3. 查看生成的卦象

### 查看解释
1. 起卦后，点击"查看解释"按钮
2. 弹窗显示卦象完整解释
3. 包含卦辞、爻辞、白话解释

### 复制卦象
1. 起卦后，长按"长按复制"按钮 0.8 秒
2. 自动复制卦象文本到剪贴板
3. 显示"✅ 已复制到剪贴板"提示

---

## 🔧 技术栈

- **Kivy 2.1.0** - 跨平台 UI 框架
- **Python 3.11** - 编程语言
- **Buildozer 1.5.0** - Android 打包工具
- **Cython 0.29.36** - Python 扩展
- **pyjnius** - Android JNI 调用

---

## 📝 代码结构

```
wuaibagua/
├── main.py                 # 主程序（386 行）
├── gua_interpret.py        # 卦象数据（856 行）
├── config.py               # 配置管理
├── cache.py                # 数据缓存
├── history.py              # 历史记录
├── buildozer.spec          # Buildozer 配置
└── UPGRADE_LOG.md          # 升级日志
```

---

## 🎯 验收标准

- [x] 构建成功（GitHub Actions）
- [x] 卦象解释正常显示
- [x] 长按复制功能正常
- [x] Toast 提示正常
- [ ] APK 安装测试（待完成）

---

## 📅 更新计划

### v1.1.2 (待定)
- [ ] 优化卦象计算逻辑
- [ ] 添加更多卦象解释内容
- [ ] 改进 UI 样式

### v1.2.0 (计划中)
- [ ] 分享功能（微信/QQ/抖音/小红书）
- [ ] 卦象收藏功能
- [ ] 历史记录优化

---

**创建时间**: 2026-03-24 23:20
**创建人**: 小爪 💕
