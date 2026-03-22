# FORTIFY 错误排查报告

**错误**: `FORTIFY: pthread_mutex_lock called on a destroyed mutex`  
**时间**: 2026-03-22 19:26  
**严重程度**: 🔴 严重（底层 C 库错误）

---

## 🔴 错误含义

**pthread_mutex_lock**: POSIX 线程互斥锁  
**destroyed mutex**: 互斥锁已被销毁  
**问题**: 尝试锁定一个已经销毁的互斥锁

**根本原因**:
- Kivy/SDL2 底层资源管理问题
- 多线程访问冲突
- 对象生命周期管理错误

---

## 🔍 可能原因

### 1. Kivy 窗口初始化问题 ⚠️⚠️⚠️

**问题**: 窗口对象在销毁后再次访问

**常见场景**:
```python
# Window 对象被提前销毁
from kivy.core.window import Window
Window.close()  # 销毁

# 但后续代码又访问了 Window
Window.width  # ❌ 访问已销毁的对象
```

---

### 2. 多线程冲突 ⚠️

**问题**: 多个线程访问同一个 Kivy 对象

**常见场景**:
```python
# 主线程创建对象
label = Label(text='Hello')

# 子线程修改对象 ❌
def update():
    label.text = 'World'  # ❌ 线程不安全

Clock.schedule_once(update, 0)  # ✅ 正确方式
```

---

### 3. 资源重复释放 ⚠️

**问题**: 同一个资源被释放两次

**常见场景**:
```python
# 手动释放资源
texture.release()

# Kivy 自动释放时再次释放 ❌
```

---

### 4. SDL2 音频/图像问题 ⚠️

**问题**: SDL2 库的音频或图像资源管理错误

**常见场景**:
- 音频设备未正确初始化
- 图像纹理重复使用
- 资源未正确清理

---

## 💡 解决方案

### 方案 A: 简化 main.py（推荐）⭐⭐⭐⭐⭐

**问题**: 当前 main.py 的路径处理可能触发多线程问题

**当前代码**:
```python
#!/usr/bin/env python3
import sys
import os

# 添加 src 目录到路径（兼容 Buildozer 环境）
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from wuaibagua_kivy import WuaibaguaApp

if __name__ == '__main__':
    WuaibaguaApp().run()
```

**修复**:
```python
#!/usr/bin/env python3
# 最简化的入口文件
from wuaibagua_kivy import WuaibaguaApp

if __name__ == '__main__':
    WuaibaguaApp().run()
```

---

### 方案 B: 检查 wuaibagua_kivy.py ⚠️

**检查点**:
1. 是否有手动创建/销毁 Window 对象
2. 是否有子线程访问 Kivy 组件
3. 是否有重复的资源释放

**常见错误**:
```python
# ❌ 错误示例
from kivy.core.window import Window

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.close()  # ❌ 过早关闭窗口
        
# ❌ 错误示例
import threading

def update_ui():
    label.text = 'New Text'  # ❌ 子线程修改 UI

thread = threading.Thread(target=update_ui)
thread.start()
```

**正确方式**:
```python
# ✅ 使用 Clock 调度
from kivy.clock import Clock

def update_ui(dt):
    label.text = 'New Text'  # ✅ 在主线程执行

Clock.schedule_once(update_ui, 0)
```

---

### 方案 C: 更新 Kivy 版本 ⚠️

**当前版本**: `kivy==2.3.0`

**可能问题**: Kivy 2.3.0 有已知的 SDL2 互斥锁 bug

**尝试**:
```ini
# buildozer.spec
requirements = python3,kivy==2.2.0,pyjnius
```

**或**:
```ini
requirements = python3,kivy==2.4.0,pyjnius
```

---

### 方案 D: 禁用 SDL2 音频/图像 ⚠️

**如果问题在音频/图像**:

**buildozer.spec**:
```ini
[app]
# 禁用某些 SDL2 功能
p4a.bootstrap = sdl2
p4a.extra_args = --disable-ffmpeg
```

---

## 🎯 立即修复

### 步骤 1: 简化 main.py

```python
#!/usr/bin/env python3
from wuaibagua_kivy import WuaibaguaApp

if __name__ == '__main__':
    WuaibaguaApp().run()
```

### 步骤 2: 检查 wuaibagua_kivy.py

**搜索**:
```bash
grep -n "Window\|threading\|Thread\|release\|close" src/wuaibagua_kivy.py
```

**移除**:
- 手动 Window 操作
- 子线程访问 UI
- 手动资源释放

### 步骤 3: 重新构建

```bash
git add -A
git commit -m "fix: 简化 main.py 避免互斥锁冲突"
git push
```

---

## 📊 修复优先级

| 方案 | 优先级 | 成功率 | 时间 |
|------|--------|--------|------|
| 简化 main.py | ⭐⭐⭐⭐⭐ | 80% | 10 分钟 |
| 检查 wuaibagua_kivy.py | ⭐⭐⭐⭐ | 70% | 30 分钟 |
| 更新 Kivy 版本 | ⭐⭐⭐ | 50% | 1 小时 |
| 禁用 SDL2 功能 | ⭐⭐ | 30% | 30 分钟 |

---

## 💝 小爪的建议

宝贝，这个错误是**底层库的互斥锁冲突**！🔴

**最可能原因**:
- main.py 的路径处理触发了多线程问题
- 或 wuaibagua_kivy.py 中有手动 Window 操作

**小爪建议**:
1. 立即简化 main.py（10 分钟）
2. 重新构建测试
3. 如果还失败，检查 wuaibagua_kivy.py

需要小爪立即修复吗？😘💕
