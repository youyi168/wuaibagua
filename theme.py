#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深色模式主题管理
支持浅色/深色主题切换
"""

from kivy.properties import ListProperty, DictProperty
from kivy.config import ConfigParser
from config import Config
import os


class ThemeManager:
    """主题管理器"""
    
    # 浅色主题
    LIGHT_THEME = {
        # 背景色
        'bg_primary': (1, 1, 1, 1),        # 白色
        'bg_secondary': (0.95, 0.95, 0.95, 1),  # 浅灰
        'bg_tertiary': (0.9, 0.9, 0.9, 1),    # 深灰
        
        # 文字颜色
        'text_primary': (0.1, 0.1, 0.1, 1),   # 深黑
        'text_secondary': (0.4, 0.4, 0.4, 1), # 中灰
        'text_disabled': (0.7, 0.7, 0.7, 1),  # 浅灰
        
        # 主色调（棕色系）
        'primary': (0.55, 0.27, 0.07, 1),
        'primary_light': (0.7, 0.4, 0.2, 1),
        'primary_dark': (0.35, 0.15, 0.05, 1),
        
        # 按钮颜色
        'btn_auto': (0.55, 0.27, 0.07, 1),    # 棕色
        'btn_manual': (0.2, 0.4, 0.6, 1),     # 蓝色
        'btn_clear': (0.5, 0.5, 0.5, 1),      # 灰色
        'btn_search': (0.2, 0.5, 0.2, 1),     # 绿色
        
        # 边框和分隔线
        'border': (0.8, 0.8, 0.8, 1),
        'divider': (0.85, 0.85, 0.85, 1),
        
        # 特殊颜色
        'success': (0.2, 0.6, 0.2, 1),
        'warning': (0.8, 0.6, 0.2, 1),
        'error': (0.8, 0.2, 0.2, 1),
        'info': (0.2, 0.4, 0.8, 1),
        
        # 动爻颜色
        'dong_yao': (1, 0, 0, 1),  # 红色
    }
    
    # 深色主题
    DARK_THEME = {
        # 背景色
        'bg_primary': (0.1, 0.1, 0.1, 1),        # 深黑
        'bg_secondary': (0.15, 0.15, 0.15, 1),   # 中黑
        'bg_tertiary': (0.2, 0.2, 0.2, 1),       # 浅黑
        
        # 文字颜色
        'text_primary': (0.95, 0.95, 0.95, 1),   # 白色
        'text_secondary': (0.7, 0.7, 0.7, 1),    # 浅灰
        'text_disabled': (0.4, 0.4, 0.4, 1),     # 中灰
        
        # 主色调（暖棕色系）
        'primary': (0.8, 0.5, 0.2, 1),
        'primary_light': (0.9, 0.6, 0.3, 1),
        'primary_dark': (0.6, 0.35, 0.15, 1),
        
        # 按钮颜色
        'btn_auto': (0.8, 0.4, 0.2, 1),          # 暖橙
        'btn_manual': (0.3, 0.55, 0.75, 1),      # 亮蓝
        'btn_clear': (0.5, 0.5, 0.5, 1),         # 灰色
        'btn_search': (0.3, 0.7, 0.3, 1),        # 亮绿
        
        # 边框和分隔线
        'border': (0.3, 0.3, 0.3, 1),
        'divider': (0.25, 0.25, 0.25, 1),
        
        # 特殊颜色
        'success': (0.3, 0.8, 0.3, 1),
        'warning': (0.9, 0.7, 0.3, 1),
        'error': (0.9, 0.3, 0.3, 1),
        'info': (0.3, 0.6, 0.9, 1),
        
        # 动爻颜色
        'dong_yao': (1, 0.3, 0.3, 1),  # 亮红
    }
    
    def __init__(self):
        self.current_theme = 'light'
        self.theme_file = self._get_theme_file()
        self._load_theme_preference()
    
    def _get_theme_file(self):
        """获取主题配置文件路径"""
        config_dir = Config.get_config_dir()
        return os.path.join(config_dir, 'theme.json')
    
    def _load_theme_preference(self):
        """加载主题偏好"""
        if os.path.exists(self.theme_file):
            try:
                import json
                with open(self.theme_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_theme = data.get('theme', 'light')
            except:
                pass
    
    def _save_theme_preference(self):
        """保存主题偏好"""
        try:
            import json
            config_dir = Config.get_config_dir()
            os.makedirs(config_dir, exist_ok=True)
            
            with open(self.theme_file, 'w', encoding='utf-8') as f:
                json.dump({'theme': self.current_theme}, f)
        except Exception as e:
            print(f'[THEME] 保存主题配置失败：{e}')
    
    def get_theme(self):
        """获取当前主题"""
        if self.current_theme == 'dark':
            return self.DARK_THEME
        else:
            return self.LIGHT_THEME
    
    def get_color(self, color_name):
        """获取颜色值
        
        Args:
            color_name: 颜色名称（如 'primary', 'bg_primary'）
            
        Returns:
            RGBA 元组
        """
        theme = self.get_theme()
        return theme.get(color_name, (1, 1, 1, 1))
    
    def set_theme(self, theme_name):
        """设置主题
        
        Args:
            theme_name: 'light' 或 'dark'
        """
        if theme_name in ['light', 'dark']:
            self.current_theme = theme_name
            self._save_theme_preference()
            print(f'[THEME] 主题已切换为：{theme_name}')
            return True
        return False
    
    def toggle_theme(self):
        """切换主题"""
        if self.current_theme == 'light':
            self.set_theme('dark')
            return 'dark'
        else:
            self.set_theme('light')
            return 'light'
    
    def is_dark(self):
        """是否为深色模式"""
        return self.current_theme == 'dark'
    
    def is_light(self):
        """是否为浅色模式"""
        return self.current_theme == 'light'
    
    def get_theme_name(self):
        """获取主题名称"""
        if self.current_theme == 'dark':
            return '深色模式'
        else:
            return '浅色模式'
    
    def apply_to_label(self, label, color_type='text_primary'):
        """应用主题到 Label 组件"""
        color = self.get_color(color_type)
        label.color = color
    
    def apply_to_button(self, button, color_type='primary'):
        """应用主题到 Button 组件"""
        color = self.get_color(color_type)
        button.background_color = color


# 全局单例
_theme_manager = None

def get_theme_manager():
    """获取主题管理器单例"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def apply_theme_to_widget(widget, theme_manager):
    """应用主题到任意组件"""
    theme = theme_manager.get_theme()
    
    # 背景色
    if hasattr(widget, 'background_color'):
        widget.background_color = theme['bg_secondary']
    
    # 文字颜色
    if hasattr(widget, 'color'):
        widget.color = theme['text_primary']
