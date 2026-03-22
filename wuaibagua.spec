# -*- mode: python ; coding: utf-8 -*-
"""
我爱八卦 - PyInstaller 打包配置文件
用于生成 Windows 可执行文件
注意：此文件在 CI/CD 环境中使用，避免 Kivy 初始化 OpenGL
"""

import os
import sys

# 在导入 PyInstaller 之前设置环境变量
os.environ['PYINSTALLER_ANALYZE'] = '1'
os.environ['CI'] = 'true'
os.environ['KIVY_NO_ARGS'] = '1'

from PyInstaller.utils.hooks import collect_data_files

# 项目名称
name = '我爱八卦'

# 版本号
version = '1.6.0'

# 主程序文件（使用新的入口）
main_script = 'main.py'

# 收集数据文件（不触发 Kivy 导入）
datas = []

# 添加 data 目录（64 卦数据）
if os.path.exists('data'):
    datas.append(('data', 'data'))

# 添加 fonts 目录（中文字体）
if os.path.exists('fonts'):
    datas.append(('fonts', 'fonts'))

# 收集 Kivy 数据文件
try:
    datas.extend(collect_data_files('kivy'))
except Exception as e:
    print(f"[WARN] Could not collect kivy data files: {e}")

# 预定义的隐藏导入（使用 collect_all 收集所有本地模块）
hiddenimports = [
    'kivy',
    'kivy.app',
    'kivy.uix',
    'kivy.uix.boxlayout',
    'kivy.uix.gridlayout',
    'kivy.uix.scrollview',
    'kivy.uix.button',
    'kivy.uix.label',
    'kivy.uix.spinner',
    'kivy.uix.popup',
    'kivy.uix.togglebutton',
    'kivy.core',
    'kivy.core.window',
    'kivy.core.text',
    'kivy.core.image',
    'kivy.core.gl',
    'kivy.graphics',
    'kivy.graphics.instructions',
    'kivy.graphics.vertex_instructions',
    'kivy.graphics.tesselator',
    'kivy.lang',
    'kivy.factory',
    'kivy.factory_registers',
    'kivy.properties',
    'kivy.config',
    'kivy.resources',
    'kivy.metrics',
    'kivy.atlas',
    'kivy.cache',
    'kivy.clock',
    'kivy.event',
    'kivy.logger',
    'kivy.base',
    'kivy.weakmethod',
    'kivy.compat',
    'kivy.vector',
    'kivy.animation',
    'kivy.texture',
    'kivy.image',
    'kivy.text',
    'kivy.text.sdl2',
    'kivy.core.window.window_sdl2',
    'kivy.core.text.text_sdl2',
    'kivy.core.image.img_sdl2',
    'kivy.core.audio.audio_sdl2',
    'PIL',
    'PIL.Image',
    'pkg_resources',
]

# 使用 PyInstaller hooks 收集所有本地模块
from PyInstaller.utils.hooks import collect_submodules

# 收集所有本地模块
local_modules = [
    'config',
    'logger',
    'cache',
    'copy',
    'user',
    'interpreter',
    'theme',
    'share',
    'sound',
    'favorite',
    'history',
    'quick_topic',
    'animation',
    'compact_gua',
    'statistics',
    'history_screen',
]

# 添加到 hiddenimports
for module in local_modules:
    try:
        hiddenimports.extend(collect_submodules(module))
    except Exception as e:
        print(f"[WARN] Could not collect {module}: {e}")
        # 如果 collect_submodules 失败，直接添加模块名
        hiddenimports.append(module)

# PyInstaller 配置
a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['build_hook.py'],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.testing',
        'tkinter',
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    module_collection_mode={
        'kivy': 'py',  # 收集为 py 文件，避免触发初始化
    },
)

# 创建 PYZ 归档
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建 EXE 文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = 无控制台窗口（GUI 模式）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
