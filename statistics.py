#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计图表模块
提供卦象分布、吉凶分布等统计图表
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle
from utils.logger import info


class ProgressBar(BoxLayout):
    """进度条组件"""
    
    def __init__(self, label_text='', value=0, max_value=100, color=(0.3, 0.5, 0.7, 1), **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(30)
        
        # 标签
        self.label = Label(
            text=label_text,
            font_size=sp(14),
            size_hint_x=0.3,
            halign='left'
        )
        self.add_widget(self.label)
        
        # 进度条背景
        bg_layout = BoxLayout(
            size_hint_x=0.7,
            size_hint_y=None,
            height=dp(20)
        )
        
        with bg_layout.canvas.before:
            Color(0.8, 0.8, 0.8, 0.5)
            self.bg_rect = Rectangle(size=bg_layout.size, pos=bg_layout.pos)
        
        # 进度条前景
        with bg_layout.canvas.before:
            Color(*color)
            self.fg_rect = Rectangle(size=(0, dp(20)), pos=bg_layout.pos)
        
        self.bg_layout = bg_layout
        self.bg_layout.bind(size=self._update_bg_rect, pos=self._update_bg_rect)
        self.add_widget(bg_layout)
        
        # 设置值
        self.set_value(value, max_value)
    
    def _update_bg_rect(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    def set_value(self, value, max_value):
        """设置进度值"""
        if max_value > 0:
            ratio = value / max_value
            self.fg_rect.size = (self.bg_layout.width * ratio, dp(20))
            self.fg_rect.pos = self.bg_layout.pos


class GuaStatistics(ScrollView):
    """卦象统计组件"""
    
    def __init__(self, history_manager=None, favorite_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.history_manager = history_manager
        self.favorite_manager = favorite_manager
        
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(15)
        self.size_hint_y = None
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        # 主容器
        self.main_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(15)
        )
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))
        
        self.add_widget(self.main_layout)
        
        # 加载统计
        self.load_statistics()
    
    def load_statistics(self):
        """加载统计数据"""
        self.main_layout.clear_widgets()
        
        # 1. 总览统计
        self._add_overview_section()
        
        # 2. 卦象分布
        self._add_gua_distribution()
        
        # 3. 吉凶分布
        self._add_fortune_distribution()
        
        # 4. 事项分布
        self._add_topic_distribution()
        
        info('统计图表已加载')
    
    def _add_section_title(self, title):
        """添加章节标题"""
        title_label = Label(
            text=title,
            font_size=sp(18),
            bold=True,
            size_hint_y=None,
            height=dp(35),
            halign='left',
            color=(0.5, 0.3, 0.1, 1)
        )
        self.main_layout.add_widget(title_label)
    
    def _add_overview_section(self):
        """添加总览统计"""
        self._add_section_title('📊 总览')
        
        history_stats = self.history_manager.get_statistics() if self.history_manager else {}
        favorite_stats = self.favorite_manager.get_statistics() if self.favorite_manager else {}
        
        overview_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # 总记录数
        total = history_stats.get('total', 0)
        self._add_stat_card(overview_layout, '📜 总记录', str(total))
        
        # 电脑起卦
        auto_count = history_stats.get('auto_count', 0)
        self._add_stat_card(overview_layout, '🤖 电脑', str(auto_count))
        
        # 手动起卦
        manual_count = history_stats.get('manual_count', 0)
        self._add_stat_card(overview_layout, '✋ 手动', str(manual_count))
        
        # 有动爻
        dong_count = history_stats.get('dong_gua_count', 0)
        self._add_stat_card(overview_layout, '⚡ 动爻', str(dong_count))
        
        self.main_layout.add_widget(overview_layout)
    
    def _add_stat_card(self, parent, label_text, value_text):
        """添加统计卡片"""
        card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        
        with card.canvas.before:
            Color(0.9, 0.9, 0.95, 1)
            card.rect = Rectangle(size=card.size, pos=card.pos)
            card.bind(size=lambda x, y: setattr(card.rect, 'size', y),
                     pos=lambda x, y: setattr(card.rect, 'pos', y))
        
        label = Label(
            text=label_text,
            font_size=sp(14),
            color=(0.5, 0.5, 0.5, 1)
        )
        card.add_widget(label)
        
        value = Label(
            text=value_text,
            font_size=sp(24),
            bold=True,
            color=(0.3, 0.5, 0.7, 1)
        )
        card.add_widget(value)
        
        parent.add_widget(card)
    
    def _add_gua_distribution(self):
        """添加卦象分布"""
        self._add_section_title('🔮 卦象分布 (Top 10)')
        
        if self.history_manager:
            history = self.history_manager.get_history(limit=100)
            
            # 统计卦名
            gua_count = {}
            for record in history:
                gua_name = record.get('ben_gua_name', '未知')
                gua_count[gua_name] = gua_count.get(gua_name, 0) + 1
            
            # 排序取前 10
            sorted_gua = sorted(gua_count.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if sorted_gua:
                max_count = sorted_gua[0][1]
                
                for gua_name, count in sorted_gua:
                    progress = ProgressBar(
                        label_text=gua_name,
                        value=count,
                        max_value=max_count,
                        color=(0.3, 0.5, 0.7, 1)
                    )
                    self.main_layout.add_widget(progress)
            else:
                self.main_layout.add_widget(Label(
                    text='暂无数据',
                    font_size=sp(14),
                    color=(0.7, 0.7, 0.7, 1)
                ))
    
    def _add_fortune_distribution(self):
        """添加吉凶分布"""
        self._add_section_title('⚡ 动爻统计')
        
        if self.history_manager:
            history = self.history_manager.get_history(limit=100)
            
            # 统计动爻数量分布
            dong_distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            for record in history:
                dong_count = len(record.get('dong_yao', []))
                dong_distribution[dong_count] = dong_distribution.get(dong_count, 0) + 1
            
            total = len(history)
            
            if total > 0:
                for dong_count, count in sorted(dong_distribution.items()):
                    percentage = count / total * 100
                    progress = ProgressBar(
                        label_text=f'{dong_count}爻动',
                        value=count,
                        max_value=total,
                        color=(0.6, 0.3, 0.6, 1)
                    )
                    self.main_layout.add_widget(progress)
    
    def _add_topic_distribution(self):
        """添加事项分布"""
        self._add_section_title('📝 事项分布')
        
        if self.history_manager:
            history = self.history_manager.get_history(limit=100)
            
            # 统计事项
            topic_count = {}
            for record in history:
                topic = record.get('topic', '')
                if topic:
                    topic_count[topic] = topic_count.get(topic, 0) + 1
            
            if topic_count:
                sorted_topics = sorted(topic_count.items(), key=lambda x: x[1], reverse=True)[:10]
                max_count = sorted_topics[0][1]
                
                for topic, count in sorted_topics:
                    progress = ProgressBar(
                        label_text=topic,
                        value=count,
                        max_value=max_count,
                        color=(0.7, 0.4, 0.2, 1)
                    )
                    self.main_layout.add_widget(progress)
            else:
                self.main_layout.add_widget(Label(
                    text='暂无事项记录',
                    font_size=sp(14),
                    color=(0.7, 0.7, 0.7, 1)
                ))


def create_statistics_screen(history_manager, favorite_manager):
    """创建统计屏幕
    
    Args:
        history_manager: 历史管理器
        favorite_manager: 收藏管理器
    
    Returns:
        GuaStatistics 实例
    """
    return GuaStatistics(history_manager=history_manager, favorite_manager=favorite_manager)
