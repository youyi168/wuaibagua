#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 金钱卦算卦软件
主程序入口

版本：v1.6.0
"""

import sys
import os

# 添加 src 目录到路径（兼容 Buildozer 环境）
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 导入主应用
from wuaibagua_kivy import WuaibaguaApp

if __name__ == '__main__':
    WuaibaguaApp().run()
