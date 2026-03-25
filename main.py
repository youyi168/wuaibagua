#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 金钱卦算卦软件 (Android 版)
版本：v1.1.1
功能：电脑起卦、手动起卦、本地卦象解释、长按复制
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

# 导入卦象解释数据
try:
    import gua_interpret
    GUA_INTERPRET_AVAILABLE = True
except ImportError:
    GUA_INTERPRET_AVAILABLE = False
    print('[WARN] gua_interpret module not available')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

# ==================== 注册中文字体 ====================
# 解决中文显示方块问题
def register_chinese_font():
    """注册中文字体到 Kivy"""
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    font_path = os.path.join(font_dir, 'NotoSansSC-Regular.ttf')
    
    if os.path.exists(font_path):
        LabelBase.register(name='NotoSansSC', fn_regular=font_path)
        print(f'[INFO] 中文字体已注册：{font_path}')
    else:
        print(f'[WARN] 中文字体文件不存在：{font_path}')
        # 尝试使用系统字体
        LabelBase.register(name='NotoSansSC', fn_regular='/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc')
        print('[INFO] 使用系统中文字体')

# 在应用启动前注册字体
register_chinese_font()

# Android 剪贴板
try:
    from jnius import autoclass
    ANDROID_CLIPBOARD_AVAILABLE = True
except ImportError:
    ANDROID_CLIPBOARD_AVAILABLE = False
    print('[WARN] jnius not available, using fallback')


# ==================== 长按复制功能 ====================

class LongPressBehavior:
    """长按行为 Mixin"""
    long_press_duration = 0.8  # 长按时长（秒）
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._long_press_trigger = None
        self.bind(on_press=self._start_long_press)
        self.bind(on_release=self._cancel_long_press)
    
    def _start_long_press(self, instance):
        """开始长按计时"""
        self._long_press_trigger = Clock.schedule_once(
            self._on_long_press,
            self.long_press_duration
        )
    
    def _cancel_long_press(self, instance):
        """取消长按"""
        if self._long_press_trigger:
            self._long_press_trigger.cancel()
            self._long_press_trigger = None
    
    def _on_long_press(self, dt):
        """长按触发"""
        self._cancel_long_press()
        self.on_long_press()
    
    def on_long_press(self):
        """长按事件（子类重写）"""
        pass


class LongPressButton(LongPressBehavior, Button):
    """长按按钮"""
    
    def __init__(self, on_long_press_callback=None, **kwargs):
        self.on_long_press_callback = on_long_press_callback
        super().__init__(**kwargs)
    
    def on_long_press(self):
        """长按事件"""
        if self.on_long_press_callback:
            self.on_long_press_callback(self)


class CopyableLabel(LongPressBehavior, Label):
    """可长按复制的标签"""
    
    def __init__(self, copy_text='', **kwargs):
        self.copy_text = copy_text
        super().__init__(**kwargs)
    
    def on_long_press(self):
        """长按复制"""
        if self.copy_text:
            copy_to_clipboard(self.copy_text)
            show_toast('✅ 已复制到剪贴板')


def copy_to_clipboard(text):
    """
    复制文本到剪贴板（Android）
    
    Args:
        text: 要复制的文本
    """
    try:
        if ANDROID_CLIPBOARD_AVAILABLE:
            # Android 原生方式
            Context = autoclass('android.content.Context')
            ClipboardManager = autoclass('android.content.ClipboardManager')
            ClipData = autoclass('android.content.ClipData')
            
            app = App.get_running_app()
            if app and hasattr(app, 'getApplicationContext'):
                context = app.getApplicationContext()
                clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE)
                clip = ClipData.newPlainText('wuaibagua', text)
                clipboard.setPrimaryClip(clip)
        else:
            # 桌面端 fallback
            print(f'[INFO] Copy to clipboard: {text[:50]}...')
    except Exception as e:
        print(f'[ERROR] Copy failed: {e}')


def show_toast(message):
    """显示 Toast 提示（Android）"""
    try:
        if ANDROID_CLIPBOARD_AVAILABLE:
            Context = autoclass('android.content.Context')
            Toast = autoclass('android.widget.Toast')
            
            app = App.get_running_app()
            if app and hasattr(app, 'getApplicationContext'):
                context = app.getApplicationContext()
                toast = Toast.makeText(context, message, Toast.LENGTH_SHORT)
                toast.show()
        else:
            print(f'[TOAST] {message}')
    except Exception as e:
        print(f'[ERROR] Toast failed: {e}')


# ==================== 卦象解释功能 ====================

def get_gua_explanation(gua_name):
    """
    获取卦象完整解释
    
    Args:
        gua_name: 卦名
    
    Returns:
        包含卦辞、爻辞、解释的字典
    """
    if not GUA_INTERPRET_AVAILABLE:
        return None
    
    return gua_interpret.get_gua_interpret(gua_name)


def show_gua_explanation_popup(gua_name):
    """
    显示卦象解释弹窗
    
    Args:
        gua_name: 卦名
    """
    if not GUA_INTERPRET_AVAILABLE:
        show_toast('❌ 卦象数据不可用')
        return
    
    data = get_gua_explanation(gua_name)
    if not data:
        show_toast('❌ 未找到卦象解释')
        return
    
    # 创建弹窗内容
    layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
    
    # 标题
    title_label = Label(
        text=f'[b]{gua_name}[/b]',
        markup=True,
        size_hint_y=None,
        height=dp(50),
        font_size=dp(20),
        bold=True
    )
    layout.add_widget(title_label)
    
    # 滚动区域
    scroll = ScrollView()
    content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
    content_layout.bind(minimum_height=content_layout.setter('height'))
    
    # 卦辞
    gua_ci_label = Label(
        text=f'[b]卦辞：[/b]{data.get("gua_ci", "")}',
        markup=True,
        size_hint_y=None,
        height=dp(40),
        halign='left',
        valign='middle',
        font_size=dp(16)
    )
    gua_ci_label.bind(size=gua_ci_label.setter('text_size'))
    content_layout.add_widget(gua_ci_label)
    
    # 白话解释
    jie_shi_label = Label(
        text=f'[b]解释：[/b]{data.get("jie_shi", "")}',
        markup=True,
        size_hint_y=None,
        height=dp(80),
        halign='left',
        valign='top',
        font_size=dp(14)
    )
    jie_shi_label.bind(size=jie_shi_label.setter('text_size'))
    content_layout.add_widget(jie_shi_label)
    
    # 爻辞
    yao_ci = data.get('yao_ci', [])
    if yao_ci:
        yao_title = Label(
            text='[b]爻辞：[/b]',
            markup=True,
            size_hint_y=None,
            height=dp(30),
            halign='left',
            font_size=dp(16)
        )
        content_layout.add_widget(yao_title)
        
        for yao in yao_ci:
            yao_label = Label(
                text=yao,
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='middle',
                font_size=dp(14)
            )
            yao_label.bind(size=yao_label.setter('text_size'))
            content_layout.add_widget(yao_label)
    
    scroll.add_widget(content_layout)
    layout.add_widget(scroll)
    
    # 关闭按钮
    close_btn = Button(
        text='关闭',
        size_hint_y=None,
        height=dp(50),
        font_size=dp(16)
    )
    
    popup = Popup(
        title='卦象解释',
        content=layout,
        size_hint=(0.9, 0.8),
        auto_dismiss=False
    )
    
    close_btn.bind(on_press=popup.dismiss)
    layout.add_widget(close_btn)
    
    popup.open()


# ==================== 主应用 ====================

class WuaibaguaApp(App):
    """我爱八卦应用主类"""
    
    def build(self):
        """构建应用界面"""
        self.title = '我爱八卦 v1.1.1'
        
        # 设置全局默认字体为中文字体
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        # 设置默认字体
        Label.font_name = 'NotoSansSC'
        Button.font_name = 'NotoSansSC'
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # 标题
        title_label = Label(
            text='[b]我爱八卦[/b]\n[b]v1.1.1[/b]',
            markup=True,
            size_hint_y=None,
            height=dp(80),
            font_size=dp(24),
            bold=True
        )
        main_layout.add_widget(title_label)
        
        # 起卦方式选择
        method_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.btn_auto = Button(
            text='电脑起卦',
            font_size=dp(18)
        )
        self.btn_auto.bind(on_press=self.auto_gua)
        method_layout.add_widget(self.btn_auto)
        
        self.btn_manual = Button(
            text='手动起卦',
            font_size=dp(18)
        )
        self.btn_manual.bind(on_press=self.manual_gua)
        method_layout.add_widget(self.btn_manual)
        
        main_layout.add_widget(method_layout)
        
        # 卦象显示区域
        self.gua_result_label = Label(
            text='点击按钮开始起卦',
            markup=True,
            size_hint_y=1,
            font_size=dp(16),
            halign='center',
            valign='top'
        )
        self.gua_result_label.bind(size=self.gua_result_label.setter('text_size'))
        main_layout.add_widget(self.gua_result_label)
        
        # 功能按钮
        func_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.btn_explain = Button(
            text='查看解释',
            font_size=dp(16)
        )
        self.btn_explain.bind(on_press=self.show_explanation)
        func_layout.add_widget(self.btn_explain)
        
        self.btn_copy = LongPressButton(
            text='长按复制',
            font_size=dp(16),
            on_long_press_callback=self.copy_result
        )
        func_layout.add_widget(self.btn_copy)
        
        main_layout.add_widget(func_layout)
        
        self.current_gua = None
        return main_layout
    
    def auto_gua(self, instance):
        """电脑起卦"""
        # 生成 6 爻
        yao_list = [random.randint(6, 9) for _ in range(6)]
        self.display_gua(yao_list, '电脑起卦')
    
    def manual_gua(self, instance):
        """手动起卦"""
        # 简化版：随机生成
        yao_list = [random.randint(6, 9) for _ in range(6)]
        self.display_gua(yao_list, '手动起卦')
    
    def display_gua(self, yao_list, method):
        """显示卦象"""
        # 卦象符号映射
        yao_symbols = {
            6: '⚋',  # 老阴
            7: '⚊',  # 少阳
            8: '⚋',  # 少阴
            9: '⚊',  # 老阳
        }
        
        # 生成卦象文本
        gua_text = f'[b]{method}[/b]\n\n'
        gua_text += '卦象：\n'
        for i, yao in enumerate(reversed(yao_list)):
            gua_text += f'{yao_symbols.get(yao, "⚊")}  {yao}\n'
        
        # 简单卦名（示例）
        gua_name = '乾为天'  # 实际需要完整的卦象计算逻辑
        gua_text += f'\n[b]卦名：{gua_name}[/b]'
        
        self.gua_result_label.text = gua_text
        self.current_gua = gua_name
        
        # 显示提示
        show_toast('✅ 起卦完成')
    
    def show_explanation(self, instance):
        """显示卦象解释"""
        if not self.current_gua:
            show_toast('❌ 请先起卦')
            return
        
        show_gua_explanation_popup(self.current_gua)
    
    def copy_result(self, instance):
        """复制卦象结果"""
        if not self.gua_result_label.text or self.gua_result_label.text == '点击按钮开始起卦':
            show_toast('❌ 无内容可复制')
            return
        
        copy_to_clipboard(self.gua_result_label.text)
        show_toast('✅ 已复制到剪贴板')


if __name__ == '__main__':
    WuaibaguaApp().run()
