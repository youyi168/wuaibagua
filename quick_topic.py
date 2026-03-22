#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事项快捷输入组件
提供常用占卜事项快捷选择
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp, sp


# 常用事项列表
QUICK_TOPICS = [
    '求财运', '问感情', '测事业',
    '问健康', '测学业', '问婚姻',
    '测投资', '问工作', '问人际',
    '测考试', '问出行', '其他'
]


class QuickTopicPicker(Popup):
    """事项快捷选择器"""
    
    def __init__(self, on_select_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_select_callback = on_select_callback
        
        self.title = "📝 选择占卜事项"
        self.size_hint = (0.9, 0.6)
        self.auto_dismiss = True
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # 说明文字
        label = Label(
            text="请选择占卜事项（可手动修改）",
            font_size=sp(15),
            size_hint_y=None,
            height=dp(35)
        )
        main_layout.add_widget(label)
        
        # 事项网格（3 列）
        grid = GridLayout(cols=3, spacing=dp(10), size_hint_y=0.8)
        
        for topic in QUICK_TOPICS:
            btn = Button(
                text=topic,
                font_size=sp(14),
                background_color=(0.3, 0.5, 0.7, 1) if topic != '其他' else (0.5, 0.5, 0.5, 1)
            )
            btn.bind(on_press=lambda x, t=topic: self.on_topic_select(t))
            grid.add_widget(btn)
        
        main_layout.add_widget(grid)
        
        # 取消按钮
        cancel_btn = Button(
            text="❌ 取消",
            font_size=sp(15),
            size_hint_y=None,
            height=dp(45),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        cancel_btn.bind(on_press=lambda x: self.dismiss())
        main_layout.add_widget(cancel_btn)
        
        self.content = main_layout
    
    def on_topic_select(self, topic):
        """选择事项"""
        if self.on_select_callback:
            self.on_select_callback(topic)
        self.dismiss()


class QuickTopicBar(BoxLayout):
    """事项快捷输入栏"""
    
    def __init__(self, on_topic_select_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_topic_select_callback = on_topic_select_callback
        self.orientation = 'vertical'
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(100)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        # 标题
        title = Label(
            text="📝 快捷事项",
            font_size=sp(14),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            color=(0.5, 0.3, 0.1, 1)
        )
        self.add_widget(title)
        
        # 事项按钮（第一行）
        row1 = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(35))
        
        topics_row1 = ['求财运', '问感情', '测事业', '问健康']
        for topic in topics_row1:
            btn = Button(
                text=topic,
                font_size=sp(13),
                background_color=(0.3, 0.5, 0.7, 1)
            )
            btn.bind(on_press=lambda x, t=topic: self._on_topic_click(t))
            row1.add_widget(btn)
        
        self.add_widget(row1)
        
        # 事项按钮（第二行）
        row2 = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(35))
        
        topics_row2 = ['测学业', '问婚姻', '测投资', '更多▼']
        for topic in topics_row2:
            btn = Button(
                text=topic,
                font_size=sp(13),
                background_color=(0.5, 0.5, 0.5, 1) if topic == '更多▼' else (0.3, 0.5, 0.7, 1)
            )
            if topic == '更多▼':
                btn.bind(on_press=lambda x: self.show_more())
            else:
                btn.bind(on_press=lambda x, t=topic: self._on_topic_click(t))
            row2.add_widget(btn)
        
        self.add_widget(row2)
    
    def _on_topic_click(self, topic):
        """点击事项"""
        if self.on_topic_select_callback:
            self.on_topic_select_callback(topic)
    
    def show_more(self):
        """显示更多事项"""
        def on_select(topic):
            if self.on_topic_select_callback:
                self.on_topic_select_callback(topic)
        
        picker = QuickTopicPicker(on_select_callback=on_select)
        picker.open()


def create_quick_topic_bar(callback):
    """创建事项快捷输入栏
    
    Args:
        callback: 选择事项后的回调函数
    
    Returns:
        QuickTopicBar 实例
    """
    return QuickTopicBar(on_topic_select_callback=callback)
