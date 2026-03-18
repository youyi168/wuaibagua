# -*- mode: python ; coding: utf-8 -*-
"""
吾爱八卦 - PyInstaller 打包配置文件
用于生成 Windows 可执行文件
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 项目名称
name = '吾爱八卦'

# 主程序文件
main_script = 'main.py'

# 收集所有数据文件
datas = []

# 添加 data 目录（64 卦数据）
if os.path.exists('data'):
    datas.append(('data', 'data'))
    print(f"[INFO] 添加 data 目录，包含 {len(os.listdir('data'))} 个文件")

# 添加 fonts 目录（中文字体）
if os.path.exists('fonts'):
    datas.append(('fonts', 'fonts'))
    print(f"[INFO] 添加 fonts 目录，包含 {len(os.listdir('fonts'))} 个文件")

# 收集 Kivy 模块
hiddenimports = []
hiddenimports.extend(collect_submodules('kivy'))
hiddenimports.extend(collect_submodules('kivy.uix'))
hiddenimports.extend(collect_submodules('kivy.core'))
hiddenimports.extend(collect_submodules('kivy.graphics'))

# Kivy 需要的额外模块
hiddenimports.extend([
    'kivy.modules',
    'kivy.factory_registers',
    'kivy.text.sdl2',
    'kivy.image',
    'kivy.video',
    'kivy.audio',
    'kivy.core.text',
    'kivy.core.image',
    'kivy.core.window',
    'kivy.core.clipboard',
    'kivy.core.spelling',
    'kivy.core.camera',
    'kivy.core.audio',
    'kivy.core.video',
    'kivy.core.text.text_sdl2',
    'kivy.core.image.img_sdl2',
    'kivy.core.window.window_sdl2',
    'PIL',
    'pkg_resources.py2_warn',
])

# 收集 Kivy 数据文件
datas.extend(collect_data_files('kivy'))

# PyInstaller 配置
a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.testing',
        'tkinter',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
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
    icon=None,  # 可以添加图标：icon='icon.ico'
)
