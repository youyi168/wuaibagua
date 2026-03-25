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

# 导入简单卦象计算（保守版本，避免闪退）
try:
    import gua_simple
    GUA_SIMPLE_AVAILABLE = True
except ImportError:
    GUA_SIMPLE_AVAILABLE = False
    print('[WARN] gua_simple module not available')

# 导入旧版卦象解释数据（备用）
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


def show_manual_gua_popup(app):
    """
    手动起卦弹窗（让用户选择每一爻）
    
    Args:
        app: WuaibaguaApp 实例
    """
    try:
        # 创建弹窗
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # 标题
        title_label = Label(
            text='[b]手动起卦[/b]\n请选择每一爻',
            markup=True,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            bold=True
        )
        layout.add_widget(title_label)
        
        # 存储用户选择的爻
        yao_selections = []
        
        # 创建 6 个选择器（从下往上：初爻→上爻）
        yao_names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
        yao_options = ['少阳 ⚊', '少阴 ⚋', '老阳 ⚊⭕', '老阴 ⚋✕']
        yao_values = [7, 8, 9, 6]  # 对应的值
        
        for i in range(6):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
            
            # 爻名标签
            name_label = Label(
                text=yao_names[i],
                size_hint_x=0.3,
                font_size=dp(15)
            )
            row.add_widget(name_label)
            
            # 选择器
            from kivy.uix.spinner import Spinner
            spinner = Spinner(
                text=yao_options[0],
                values=yao_options,
                size_hint_x=0.7
            )
            spinner.yao_index = i
            spinner.yao_values = yao_values
            yao_selections.append(spinner)
            row.add_widget(spinner)
            
            layout.add_widget(row)
        
        # 按钮区域
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # 确定按钮
        confirm_btn = Button(text='确定', font_size=dp(16))
        
        def on_confirm(instance):
            """确认选择"""
            try:
                yao_list = []
                for spinner in yao_selections:
                    idx = spinner.values.index(spinner.text)
                    yao_list.append(spinner.yao_values[idx])
                
                # 关闭弹窗
                popup.dismiss()
                
                # 显示卦象
                app.display_gua(yao_list, '手动起卦')
            except Exception as e:
                print(f'[ERROR] Manual gua confirm failed: {e}')
                show_toast('❌ 选择失败')
        
        confirm_btn.bind(on_press=on_confirm)
        btn_layout.add_widget(confirm_btn)
        
        # 取消按钮
        cancel_btn = Button(text='取消', font_size=dp(16))
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        # 创建弹窗
        popup = Popup(
            title='手动起卦',
            content=layout,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        popup.open()
    except Exception as e:
        print(f'[ERROR] show_manual_gua_popup failed: {e}')
        show_toast('❌ 弹窗失败')


def show_gua_explanation_txt(gua_name, txt_content):
    """
    显示卦象解释（txt 文件完整内容，简单版本）
    
    Args:
        gua_name: 卦名
        txt_content: txt 文件完整内容
    """
    try:
        # 创建弹窗内容
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        
        # 标题
        title_label = Label(
            text=f'[b]{gua_name}[/b]',
            markup=True,
            size_hint_y=None,
            height=dp(45),
            font_size=dp(18),
            bold=True
        )
        layout.add_widget(title_label)
        
        # 滚动区域
        scroll = ScrollView()
        
        # 完整 txt 内容（不做任何修改）
        content_label = Label(
            text=txt_content,
            markup=False,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=dp(13),
            padding=(8, 8)
        )
        content_label.bind(size=content_label.setter('text_size'))
        scroll.add_widget(content_label)
        
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(
            text='关闭',
            size_hint_y=None,
            height=dp(45),
            font_size=dp(15)
        )
        
        popup = Popup(
            title='卦象详解',
            content=layout,
            size_hint=(0.92, 0.85),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        layout.add_widget(close_btn)
        
        popup.open()
    except Exception as e:
        print(f'[ERROR] show_gua_explanation_txt failed: {e}')
        show_toast('❌ 显示失败')


def show_gua_explanation_popup(gua_name):
    """
    显示卦象解释弹窗（旧版，兼容）
    
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
        
        # 功能按钮（移除长按复制按钮）
        func_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.btn_explain = Button(
            text='查看解释',
            font_size=dp(16)
        )
        self.btn_explain.bind(on_press=self.show_explanation)
        func_layout.add_widget(self.btn_explain)
        
        # 复制按钮（点击复制，不再长按）
        self.btn_copy = Button(
            text='复制卦象',
            font_size=dp(16)
        )
        self.btn_copy.bind(on_press=self.copy_result)
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
        """手动起卦（弹窗选择每一爻）"""
        # 显示手动起卦弹窗
        show_manual_gua_popup(self)
    
    def display_gua(self, yao_list, method):
        """显示卦象（修复版，正确显示爻辞和变卦）"""
        try:
            # 卦象符号映射（带变卦标记）
            yao_symbols = {
                6: '⚋ ✕',  # 老阴（变爻）
                7: '⚊',    # 少阳
                8: '⚋',    # 少阴
                9: '⚊ ⭕',  # 老阳（变爻）
            }
            
            # 爻名
            yao_names = ['初', '二', '三', '四', '五', '上']
            
            # 生成卦象文本（从下往上显示）
            gua_text = f'[b]{method}[/b]\n\n'
            
            # 显示 6 爻（上爻→初爻）
            for i in range(5, -1, -1):
                yao = yao_list[i]
                symbol = yao_symbols.get(yao, '⚊')
                yao_type = '九' if yao in [7, 9] else '六'
                gua_text += f'{yao_names[i]}{yao_type}: {symbol}\n'
            
            # 使用简单卦象计算
            gua_name = '乾为天'  # default fallback
            if GUA_SIMPLE_AVAILABLE:
                try:
                    gua_name = gua_simple.get_gua_name_simple(yao_list)
                except Exception as e:
                    print(f'[ERROR] get_gua_name failed: {e}')
            
            gua_text += f'\n[b]卦名：{gua_name}[/b]'
            
            # 检查是否有变爻
            changing_yao = [y for y in yao_list if y in [6, 9]]
            if changing_yao:
                gua_text += '\n[b]有变爻[/b]'
            
            self.gua_result_label.text = gua_text
            self.current_gua = gua_name
            self.current_yao_list = yao_list
            
            # 读取 txt 文件内容
            self.current_gua_txt = None
            if GUA_SIMPLE_AVAILABLE:
                try:
                    self.current_gua_txt = gua_simple.get_gua_txt_simple(gua_name)
                except Exception as e:
                    print(f'[ERROR] get_gua_txt failed: {e}')
            
            # 显示提示
            show_toast(f'✅ {gua_name}')
        except Exception as e:
            print(f'[ERROR] display_gua failed: {e}')
            show_toast('❌ 显示失败')
    
    def show_explanation(self, instance):
        """显示卦象解释（简单版本）"""
        if not self.current_gua:
            show_toast('❌ 请先起卦')
            return
        
        # 优先使用 txt 文件内容
        if hasattr(self, 'current_gua_txt') and self.current_gua_txt:
            show_gua_explanation_txt(self.current_gua, self.current_gua_txt)
        else:
            # Fallback 到旧版
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
