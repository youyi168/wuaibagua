#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录查看界面
支持查看、搜索、删除历史记录
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp, sp
from features.history.history import get_history_manager
from utils.config import Config
from utils.logger import info


class HistoryItem(BoxLayout):
    """单条历史记录项"""
    
    def __init__(self, record, on_select_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.record = record
        self.on_select_callback = on_select_callback
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(100)
        
        # 背景色
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        self._init_ui()
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def _init_ui(self):
        """初始化 UI"""
        # 第一行：日期 + 卦名
        top_layout = BoxLayout(size_hint_y=None, height=dp(30))
        
        datetime_str = self.record.get('datetime', '')
        ben_gua_name = self.record.get('ben_gua_name', '')
        
        date_label = Label(
            text=f"📅 {datetime_str}",
            font_size=sp(13),
            size_hint_x=0.6,
            halign='left'
        )
        top_layout.add_widget(date_label)
        
        gua_label = Label(
            text=f"🔮 {ben_gua_name}",
            font_size=sp(14),
            size_hint_x=0.4,
            halign='right',
            bold=True
        )
        top_layout.add_widget(gua_label)
        
        self.add_widget(top_layout)
        
        # 第二行：动爻 + 事项
        bottom_layout = BoxLayout(size_hint_y=None, height=dp(30))
        
        dong_yao = self.record.get('dong_yao', [])
        dong_count = len(dong_yao)
        topic = self.record.get('topic', '')
        mode = self.record.get('mode', 'auto')
        
        info_text = f"{'⚡' if dong_count > 0 else '⚪'} {dong_count}爻动"
        if topic:
            info_text += f" | 📝 {topic}"
        info_text += f" | {'✋' if mode == 'manual' else '🤖'}"
        
        info_label = Label(
            text=info_text,
            font_size=sp(13),
            halign='left'
        )
        bottom_layout.add_widget(info_label)
        
        # 查看详情按钮
        detail_btn = Button(
            text="👁️ 查看",
            font_size=sp(13),
            size_hint_x=None,
            width=dp(60),
            background_color=(0.2, 0.4, 0.6, 1)
        )
        detail_btn.bind(on_press=lambda x: self.on_select())
        bottom_layout.add_widget(detail_btn)
        
        self.add_widget(bottom_layout)
    
    def on_select(self):
        """选中此记录"""
        if self.on_select_callback:
            self.on_select_callback(self.record)


class HistoryScreen(Screen):
    """历史记录屏幕"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'history'
        self.history_manager = get_history_manager()
        self.selected_record = None
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 标题栏
        title_layout = BoxLayout(size_hint_y=None, height=dp(50))
        
        title_label = Label(
            text="📜 历史记录",
            font_size=sp(20),
            bold=True,
            halign='left'
        )
        title_layout.add_widget(title_label)
        
        # 清空按钮
        clear_btn = Button(
            text="🗑️ 清空",
            font_size=sp(15),
            size_hint_x=None,
            width=dp(80),
            background_color=(0.6, 0.2, 0.2, 1)
        )
        clear_btn.bind(on_press=self.on_clear_history)
        title_layout.add_widget(clear_btn)
        
        main_layout.add_widget(title_layout)
        
        # 统计信息
        stats = self.history_manager.get_statistics()
        stats_label = Label(
            text=f"共 {stats['total']} 条记录 | 电脑 {stats['auto_count']} | 手动 {stats['manual_count']}",
            font_size=sp(14),
            size_hint_y=None,
            height=dp(30),
            color=(0.5, 0.5, 0.5, 1)
        )
        main_layout.add_widget(stats_label)
        
        # 历史记录列表（滚动）
        self.history_scroll = ScrollView()
        self.history_list = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(10),
            padding=dp(5)
        )
        self.history_list.bind(minimum_height=self.history_list.setter('height'))
        self.history_scroll.add_widget(self.history_list)
        
        main_layout.add_widget(self.history_scroll)
        
        # 底部按钮
        bottom_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # 刷新按钮
        refresh_btn = Button(
            text="🔄 刷新",
            font_size=sp(16),
            background_color=(0.2, 0.5, 0.2, 1)
        )
        refresh_btn.bind(on_press=lambda x: self.load_history())
        bottom_layout.add_widget(refresh_btn)
        
        # 导出按钮
        export_btn = Button(
            text="📤 导出",
            font_size=sp(16),
            background_color=(0.2, 0.4, 0.6, 1)
        )
        export_btn.bind(on_press=lambda x: self.on_export())
        bottom_layout.add_widget(export_btn)
        
        # 返回按钮
        back_btn = Button(
            text="⬅️ 返回",
            font_size=sp(16),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        bottom_layout.add_widget(back_btn)
        
        main_layout.add_widget(bottom_layout)
        
        self.add_widget(main_layout)
        
        # 加载历史记录
        self.load_history()
    
    def load_history(self):
        """加载历史记录"""
        # 清空现有列表
        self.history_list.clear_widgets()
        
        # 获取历史记录
        history = self.history_manager.get_history(limit=50)
        
        if not history:
            # 无记录提示
            empty_label = Label(
                text="暂无历史记录\n快去起卦吧～",
                font_size=sp(16),
                color=(0.7, 0.7, 0.7, 1)
            )
            self.history_list.add_widget(empty_label)
            return
        
        # 添加记录项
        for record in history:
            item = HistoryItem(
                record,
                on_select_callback=self.on_record_select
            )
            self.history_list.add_widget(item)
        
        info(f'加载了 {len(history)} 条历史记录')
    
    def on_record_select(self, record):
        """选择历史记录"""
        self.selected_record = record
        
        # 显示详情弹窗
        from kivy.uix.popup import Popup
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # 卦名
        ben_gua_name = record.get('ben_gua_name', '')
        bian_gua_name = record.get('bian_gua_name', '')
        
        title = Label(
            text=f"🔮 {ben_gua_name}" + (f" → {bian_gua_name}" if bian_gua_name else ""),
            font_size=sp(20),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(title)
        
        # 详情
        details = f"""
📅 时间：{record.get('datetime', '')}
📝 事项：{record.get('topic', '无')}
⚡ 动爻：{record.get('dong_yao_count', 0)}爻
🤖 方式：{'手动起卦' if record.get('mode') == 'manual' else '电脑起卦'}
        """.strip()
        
        detail_label = Label(
            text=details,
            font_size=sp(15),
            halign='left',
            valign='top'
        )
        detail_label.bind(texture_size=detail_label.setter('size'))
        content.add_widget(detail_label)
        
        # 按钮
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # 重新起卦按钮
        replay_btn = Button(
            text="🔮 重新起此卦",
            font_size=sp(15),
            background_color=(0.55, 0.27, 0.07, 1)
        )
        replay_btn.bind(on_press=lambda x: self.on_replay(record))
        btn_layout.add_widget(replay_btn)
        
        # 删除按钮
        delete_btn = Button(
            text="🗑️ 删除",
            font_size=sp(15),
            background_color=(0.6, 0.2, 0.2, 1)
        )
        delete_btn.bind(on_press=lambda x: self.on_delete(record))
        btn_layout.add_widget(delete_btn)
        
        content.add_widget(btn_layout)
        
        # 关闭按钮
        close_btn = Button(
            text="❌ 关闭",
            font_size=sp(15),
            size_hint_y=None,
            height=dp(45)
        )
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        popup = Popup(
            title='历史记录详情',
            content=content,
            size_hint=(0.9, 0.7),
            auto_dismiss=False
        )
        popup.open()
    
    def on_replay(self, record):
        """重新起此卦"""
        # TODO: 跳转到主界面并重新起卦
        info(f'重新起卦：{record.get("ben_gua_name", "")}')
    
    def on_delete(self, record):
        """删除记录"""
        record_id = record.get('id', '')
        if self.history_manager.delete_record(record_id):
            info(f'删除记录：{record_id}')
            self.load_history()  # 刷新列表
    
    def on_clear_history(self, instance):
        """清空历史记录"""
        # 显示确认弹窗
        from kivy.uix.popup import Popup
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        label = Label(
            text="⚠️ 确定要清空所有历史记录吗？\n\n此操作不可恢复！",
            font_size=sp(16),
            halign='center'
        )
        content.add_widget(label)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        cancel_btn = Button(
            text="❌ 取消",
            font_size=sp(15),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        confirm_btn = Button(
            text="✅ 确定清空",
            font_size=sp(15),
            background_color=(0.6, 0.2, 0.2, 1)
        )
        confirm_btn.bind(on_press=lambda x: self.confirm_clear())
        btn_layout.add_widget(confirm_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='确认清空',
            content=content,
            size_hint=(0.9, 0.5),
            auto_dismiss=False
        )
        popup.open()
    
    def confirm_clear(self):
        """确认清空"""
        self.history_manager.clear_history()
        info('已清空历史记录')
        self.load_history()  # 刷新列表
    
    def on_export(self):
        """导出历史记录"""
        output_file = self.history_manager.export_to_json()
        if output_file:
            info(f'已导出到：{output_file}')
    
    def go_back(self):
        """返回主界面"""
        from kivy.factory import Factory
        app = Factory.App.get_running_app()
        if app:
            app.root.current = 'main'
    
    def on_enter(self):
        """进入屏幕时刷新"""
        self.load_history()
