#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 金钱卦算卦软件 (Android版)
版本：v1.1.1
"""

import os
import sys
import random

# webbrowser 在 Android 上可能不可用，需要安全导入
try:
    import webbrowser
    WEBBROWSER_AVAILABLE = True
except ImportError:
    WEBBROWSER_AVAILABLE = False
    print('[WARN] webbrowser module not available')


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy import Config
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.text import LabelBase
import random

# 注册中文字体 - 解决 Android/Windows 上汉字显示乱码问题
def register_chinese_font():
    """注册支持中文的字体"""
    import os
    import sys
    
    # 获取应用根目录（兼容打包后的环境）
    # Android 环境
app_dir = os.path.dirname(os.path.abspath(__file__))
    
    
