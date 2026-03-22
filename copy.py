#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长按复制功能模块
支持长按文本复制和复制按钮
"""

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.button import Button
from logger import info


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


class CopyButton(Button):
    """复制按钮组件"""
    
    def __init__(self, text_to_copy='', **kwargs):
        super().__init__(**kwargs)
        self.text_to_copy = text_to_copy
        self.text = '📋 复制'
        self.size_hint_x = None
        self.width = dp(70)
        self.font_size = dp(14)
        self.background_color = (0.3, 0.5, 0.7, 1)
    
    def set_text(self, text):
        """设置要复制的文本"""
        self.text_to_copy = text


def copy_to_clipboard(text, show_toast=True):
    """复制文本到剪贴板
    
    Args:
        text: 要复制的文本
        show_toast: 是否显示提示
    
    Returns:
        是否成功
    """
    try:
        # Android 端
        from jnius import autoclass
        Clipboard = autoclass('android.content.ClipboardManager')
        ClipData = autoclass('android.content.ClipData')
        
        from kivy.app import App
        app = App.get_running_app()
        clipboard = app.root_window.canvas.context.get_clipboard()
        
        clip = ClipData.newPlainText('copy', text)
        clipboard.setPrimaryClip(clip)
        
        if show_toast:
            info('✅ 已复制到剪贴板')
        
        return True
        
    except ImportError:
        # 桌面端
        try:
            import pyperclip
            pyperclip.copy(text)
            
            if show_toast:
                info('✅ 已复制到剪贴板')
            
            return True
        except ImportError:
            error('剪贴板模块不可用')
            return False
    except Exception as e:
        error(f'复制失败：{e}')
        return False


def create_copy_button(text, callback=None):
    """创建复制按钮
    
    Args:
        text: 要复制的文本
        callback: 复制成功后的回调
    
    Returns:
        CopyButton 实例
    """
    btn = CopyButton(text_to_copy=text)
    
    if callback:
        btn.bind(on_press=lambda x: callback(text))
    else:
        btn.bind(on_press=lambda x: copy_to_clipboard(text))
    
    return btn
