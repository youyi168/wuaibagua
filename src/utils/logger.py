#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统模块
提供统一的日志记录功能，支持文件日志和控制台输出
"""

import logging
import os
import sys
from datetime import datetime
from utils.config import Config


class LoggerManager:
    """日志管理器"""
    
    def __init__(self, log_dir=None, log_level=None):
        self.log_dir = log_dir or self._get_default_log_dir()
        self.log_level = log_level or Config.LOG_LEVEL
        self.logger = None
        self._setup_logger()
    
    def _get_default_log_dir(self):
        """获取默认日志目录"""
        config_dir = Config.get_config_dir()
        log_dir = os.path.join(config_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    def _get_log_file(self):
        """获取日志文件路径"""
        date_str = datetime.now().strftime('%Y%m%d')
        return os.path.join(self.log_dir, f'woaibagua_{date_str}.log')
    
    def _setup_logger(self):
        """配置日志系统"""
        # 创建 logger
        self.logger = logging.getLogger('Wuaibagua')
        self.logger.setLevel(getattr(logging, self.log_level.upper(), logging.INFO))
        
        # 避免重复添加 handler
        if self.logger.handlers:
            return
        
        # 日志格式
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台 handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件 handler（仅在不使用 PyInstaller 时启用）
        if not getattr(sys, 'frozen', False):
            try:
                file_handler = logging.FileHandler(
                    self._get_log_file(),
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                self.logger.warning(f'文件日志创建失败：{e}')
    
    def debug(self, message):
        """调试日志"""
        self.logger.debug(message)
    
    def info(self, message):
        """信息日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告日志"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """错误日志"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=False):
        """严重错误日志"""
        self.logger.critical(message, exc_info=exc_info)
    
    def success(self, message):
        """成功日志"""
        self.logger.info(f'✅ {message}')
    
    def divider(self, text='', char='='):
        """分隔线"""
        line = char * 50
        if text:
            self.logger.info(f'{line} {text} {line}')
        else:
            self.logger.info(line)
    
    def get_log_file(self):
        """获取当前日志文件路径"""
        return self._get_log_file()
    
    def get_logs(self, lines=100):
        """获取最近的日志
        
        Args:
            lines: 返回行数
            
        Returns:
            日志内容字符串
        """
        log_file = self._get_log_file()
        if not os.path.exists(log_file):
            return "日志文件不存在"
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception as e:
            return f"读取日志失败：{e}"
    
    def clear_old_logs(self, days=7):
        """清理旧日志
        
        Args:
            days: 保留天数
        """
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days * 86400)
            
            cleaned = 0
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(self.log_dir, filename)
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        cleaned += 1
            
            if cleaned > 0:
                self.info(f'清理了 {cleaned} 个旧日志文件')
            
        except Exception as e:
            self.error(f'清理日志失败：{e}')


# 全局单例
_logger_manager = None

def get_logger():
    """获取日志管理器单例"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


# 快捷函数
def debug(msg): get_logger().debug(msg)
def info(msg): get_logger().info(msg)
def warning(msg): get_logger().warning(msg)
def error(msg, exc=False): get_logger().error(msg, exc_info=exc)
def success(msg): get_logger().success(msg)
