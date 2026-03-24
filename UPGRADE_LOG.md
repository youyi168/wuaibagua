# 升级日志

## v1.1.1 更新日志

### 2026-03-24 重构

#### 平台策略调整
- **专注 Android 平台** - 不再开发测试 Windows 版本
- **删除 Windows 相关代码** - 简化代码库

#### 删除的文件
- `build-windows.bat` - Windows 打包脚本
- `一键打包-Windows.bat` - Windows 打包脚本
- `wuaibagua.spec` - PyInstaller 配置
- `我爱八卦测试.spec` - PyInstaller 配置
- `wuaibagua_kivy.py` - 旧版本入口文件
- `WINDOWS 打包指南.md` - Windows 文档
- `SUGGESTIONS_COMPLETE.md` - 过时文档
- `PROJECT_CHECK_REPORT.md` - 过时文档
- `RELEASE_GUIDE.md` - 过时文档
- `GitHub Actions 自动打包指南.md` - 过时文档

#### 清理的代码
- `main.py` - 删除 PyInstaller 相关代码（frozen/_MEIPASS）
- `main.py` - 删除 Windows 字体路径
- `config.py` - 删除 Windows 路径处理
- `README.md` - 重写，只保留 Android 说明

---

## v1.1.0 → v1.2.0 开发日志

### 2026-03-24 重构记录

#### 背景
- 基于 v1.1.0 稳定版本重新开始开发
- 之前 dev 分支的代码存在多个问题导致构建失败
- 决定基于稳定版本重新开始

#### 已知问题记录

##### 1. copy.py 命名冲突
- **问题**: `copy.py` 与 Python 标准库的 `copy` 模块同名
- **错误**: `NameError: name 'Button' is not defined`
- **原因**: Kivy 导入 `copy` 模块时导入了项目的 `copy.py`
- **解决方案**: 
  - 重命名 `copy.py` → `long_press_button.py`
  - 或在 `buildozer.spec` 中排除该文件

##### 2. OPPO PKR110 Vulkan 兼容性问题
- **问题**: OPPO PKR110 设备的 Adreno Vulkan 驱动 0800.60 有 bug
- **错误**: `FORTIFY: pthread_mutex_lock called on a destroyed mutex`
- **崩溃线程**: `hwuiTask0` (Android HWUI 渲染线程)
- **原因**: Vulkan 驱动在销毁互斥锁后被 HWUI 访问
- **解决方案**:
  - 短期：在其他品牌设备上测试（小米、华为、三星等）
  - 中期：等待 Kivy/SDL2 官方修复
  - 长期：考虑使用其他跨平台框架

#### 尝试过的解决方案

##### ✅ 已解决
1. ✅ 重命名 `copy.py` → `long_press_button.py`
2. ✅ 在 `buildozer.spec` 中添加 `source.exclude_patterns`

##### ❌ 无效方案
1. ❌ 应用层设置 `KIVY_GL_BACKEND=gles2`
2. ❌ 应用层设置 `SDL_RENDER_DRIVER=opengles2`
3. ❌ 指定 Kivy 2.1.0 版本
4. ❌ 修改 buildozer.spec 中的 requirements

#### 构建配置

##### buildozer.spec 修改
```ini
[app]
requirements = python3,kivy==2.1.0,pyjnius
source.exclude_patterns = copy.py,long_press_button.py
```

##### GitHub Actions 修改
```yaml
- name: Install Buildozer and dependencies
  run: |
    pip3 install Cython==0.29.36
    pip3 install --no-cache-dir buildozer==1.5.0
    pip3 install Kivy==2.1.0
```

#### 待开发功能

##### v1.2.0 计划
- [ ] 长按复制功能
- [ ] 复制按钮组件
- [ ] 分享功能优化

##### v1.3.0 计划
- [ ] 待规划

---

## 版本历史

### v1.1.0 (2026-03-22) - 稳定版本
- 历史记录功能
- 配置类重构
- 数据缓存

### v1.0.0 (2026-03-18) - 初始版本
- 电脑起卦
- 手动起卦
- 基础卦象显示
