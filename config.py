#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置管理类
统一管理版本、路径、搜索等配置
"""

import os
import sys

class Config:
    """应用配置"""
    
    # ========== 版本信息 ==========
    VERSION = '1.1.0'
    VERSION_CODE = 6
    VERSION_NAME = '功能增强版'
    
    # ========== 应用信息 ==========
    APP_NAME = '我爱八卦'
    APP_PACKAGE = 'org.woaibagua'
    APP_DOMAIN = 'org.woaibagua'
    
    # ========== 路径配置 ==========
    @staticmethod
    def get_app_dir():
        """获取应用根目录"""
        if getattr(sys, 'frozen', False):
            # PyInstaller 打包后的环境
            if hasattr(sys, '_MEIPASS'):
                return sys._MEIPASS
            return os.path.dirname(sys.executable)
        else:
            # 开发环境
            return os.path.dirname(os.path.abspath(__file__))
    
    @classmethod
    def get_data_dir(cls):
        """获取数据目录"""
        return os.path.join(cls.get_app_dir(), 'data')
    
    @classmethod
    def get_fonts_dir(cls):
        """获取字体目录"""
        return os.path.join(cls.get_app_dir(), 'fonts')
    
    @classmethod
    def get_config_dir(cls):
        """获取配置目录（用户数据）"""
        if sys.platform == 'win32':
            return os.path.join(os.getenv('APPDATA'), cls.APP_NAME)
        elif sys.platform == 'darwin':
            return os.path.join(os.path.expanduser('~/Library/Application Support'), cls.APP_NAME)
        else:
            return os.path.join(os.path.expanduser('~'), '.' + cls.APP_NAME.lower())
    
    @classmethod
    def get_history_file(cls):
        """获取历史记录文件路径"""
        config_dir = cls.get_config_dir()
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'history.json')
    
    @classmethod
    def get_cache_file(cls):
        """获取缓存文件路径"""
        config_dir = cls.get_config_dir()
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, '.gua_cache.json')
    
    # ========== UI 配置 ==========
    BASE_WIDTH = 390    # iPhone 13/14/15 标准版宽度
    BASE_HEIGHT = 844   # iPhone 13/14/15 标准版高度
    
    # ========== 搜索配置 ==========
    SEARCH_ENGINES = {
        'baidu': {
            'name': '百度',
            'url': 'https://www.baidu.com/s?wd={query}',
            'icon': '🔍'
        },
        'wiki': {
            'name': '维基百科',
            'url': 'https://zh.wikipedia.org/wiki/{query}',
            'icon': '📖'
        },
        'bing': {
            'name': 'Bing',
            'url': 'https://www.bing.com/search?q={query}',
            'icon': '🌐'
        }
    }
    
    # ========== 断卦规则 ==========
    DIVINATION_RULES_VERSION = '图解周易_标准版'
    DIVINATION_RULES_DESC = '完全遵循《图解周易》传统金钱卦断卦规则'
    
    # ========== 缓存配置 ==========
    CACHE_ENABLED = True
    CACHE_MAX_AGE = 86400  # 缓存有效期 24 小时（秒）
    CACHE_MAX_SIZE = 100   # 最多缓存 100 条记录
    
    # ========== 历史记录配置 ==========
    HISTORY_ENABLED = True
    HISTORY_MAX_RECORDS = 100  # 最多保存 100 条记录
    
    # ========== 日志配置 ==========
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
    
    # ========== 调试配置 ==========
    DEBUG = False
    DEBUG_SHOW_FPS = False
    DEBUG_LOG_NETWORK = False
    
    @classmethod
    def enable_debug(cls):
        """启用调试模式"""
        cls.DEBUG = True
        cls.LOG_LEVEL = 'DEBUG'
        print(f'[CONFIG] 调试模式已启用 - 版本 {cls.VERSION}')
    
    @classmethod
    def disable_debug(cls):
        """禁用调试模式"""
        cls.DEBUG = False
        cls.LOG_LEVEL = 'INFO'
    
    @classmethod
    def get_info(cls):
        """获取应用信息"""
        return {
            'name': cls.APP_NAME,
            'version': cls.VERSION,
            'version_code': cls.VERSION_CODE,
            'version_name': cls.VERSION_NAME,
            'package': cls.APP_PACKAGE,
            'rules': cls.DIVINATION_RULES_VERSION
        }
    
    @classmethod
    def print_info(cls):
        """打印应用信息"""
        info = cls.get_info()
        print('=' * 50)
        print(f"{info['name']} v{info['version']} ({info['version_name']})")
        print(f"断卦规则：{info['rules']}")
        print(f"数据目录：{cls.get_data_dir()}")
        print(f"配置目录：{cls.get_config_dir()}")
        print('=' * 50)


# 快捷访问
VERSION = Config.VERSION
APP_NAME = Config.APP_NAME
