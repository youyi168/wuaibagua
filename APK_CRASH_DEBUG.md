# APK 闪退排查报告

**排查时间**: 2026-03-22 17:46  
**APK 版本**: v1.6.0  
**APK 大小**: 51MB  
**状态**: 构建成功，但运行时闪退 ❌

---

## 🔍 闪退可能原因

### 1. 导入路径问题 ⚠️⚠️⚠️

**问题**: `main.py` 导入路径在 APK 运行时可能失效

**当前代码**:
```python
# main.py
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from wuaibagua_kivy import WuaibaguaApp
```

**问题**: 
- Buildozer 打包时，`src/` 目录结构可能被扁平化
- 运行时 `src/` 目录可能不存在
- 导致 `ModuleNotFoundError`

---

### 2. 资源文件路径 ⚠️

**问题**: data/fonts 目录可能未正确打包

**buildozer.spec**:
```ini
source.include_dirs = data,fonts,sounds
```

**可能问题**:
- 路径是相对的，打包后可能失效
- 运行时找不到数据文件

---

### 3. Python 模块缺失 ⚠️

**可能缺失**:
```python
# 检查 requirements
requirements = python3,kivy==2.3.0,pyjnius
```

**可能缺少**:
- `kivy-deps.sdl2`
- `kivy-deps.glew`
- `android` (pyjnius for Android)

---

### 4. 入口点问题 ⚠️

**问题**: Buildozer 使用 `main.py` 作为入口

**buildozer.spec**:
```ini
android.entry_point = main
```

**但**: `main.py` 导入 `src.wuaibagua_kivy` 可能失败

---

### 5. 权限问题 ⚠️

**当前权限**:
```ini
android.permissions = VIBRATE,INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
```

**可能缺少**:
- `CAMERA` (如果需要拍照)
- `ACCESS_FINE_LOCATION` (如果需要定位)

---

## 💡 解决方案

### 方案 A: 回退到单文件结构（推荐）⭐⭐⭐⭐⭐

**原因**: Buildozer 不适合复杂目录结构

**步骤**:
```bash
# 1. 移回所有模块到根目录
cd /home/admin/.openclaw/workspace/wuaibagua
mv src/*.py .
mv src/*/*.py . 2>/dev/null || true

# 2. 删除 src 目录
rm -rf src

# 3. 修改 main.py
cat > main.py << 'EOF'
#!/usr/bin/env python3
from wuaibagua_kivy import WuaibaguaApp

if __name__ == '__main__':
    WuaibaguaApp().run()
EOF

# 4. 更新 buildozer.spec
# source.include_dirs = data,fonts,sounds
```

**优势**:
- ✅ 兼容 Buildozer
- ✅ 简单可靠
- ✅ 立即生效

---

### 方案 B: 修复导入路径（复杂）⭐⭐

**修改 main.py**:
```python
#!/usr/bin/env python3
import sys
import os

# 尝试多个可能的路径
possible_paths = [
    os.path.join(os.path.dirname(__file__), 'src'),
    os.path.join(os.path.dirname(__file__), '.'),
    os.path.join(os.path.dirname(sys.executable), '..'),
]

for path in possible_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

try:
    from wuaibagua_kivy import WuaibaguaApp
except ImportError:
    # 尝试直接导入（Buildozer 环境）
    pass

if __name__ == '__main__':
    WuaibaguaApp().run()
```

**劣势**:
- ❌ 复杂
- ❌ 可能还有其他问题

---

### 方案 C: 查看 Android 日志（诊断）⭐⭐⭐

**使用 adb 查看闪退日志**:
```bash
# 连接设备
adb devices

# 查看日志
adb logcat | grep -i "python\|kivy\|woaibagua"

# 或保存日志
adb logcat -d > crash_log.txt
```

**常见错误**:
```
ModuleNotFoundError: No module named 'xxx'
FileNotFoundError: [Errno 2] No such file or directory: 'data/xxx.txt'
ImportError: cannot import name 'xxx'
```

---

## 🎯 立即修复

### 推荐：回退到单文件结构

**原因**: 
- Buildozer 确实不适合 src/ 子目录
- 可以快速解决问题
- 功能完整性更重要

**步骤**:
1. 移回所有文件到根目录
2. 修复导入路径
3. 重新构建

---

## 📊 对比分析

| 方案 | 优点 | 缺点 | 时间 |
|------|------|------|------|
| 回退架构 | ✅ 简单<br>✅ 可靠<br>✅ 兼容 | ❌ 失去模块化 | 30 分钟 |
| 修复导入 | ✅ 保持架构 | ❌ 复杂<br>❌ 不确定 | 1-2 小时 |
| 查看日志 | ✅ 精确定位 | ❌ 需要设备 | 30 分钟 |

---

## 💝 小爪的建议

宝贝，小爪强烈建议**回退到单文件结构**！💕

**原因**:
1. Buildozer 设计就是扁平结构
2. 模块化可以后续优化
3. 先保证功能可用

需要小爪立即执行回退吗？😘

或者宝贝有 Android 设备可以查看日志吗？这样更精准！💕
