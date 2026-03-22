#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 金钱卦算卦软件
主程序入口

版本：v1.6.0
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# 导入主应用
from src.wuaibagua_kivy import WuaibaguaApp

if __name__ == '__main__':
    WuaibaguaApp().run()
