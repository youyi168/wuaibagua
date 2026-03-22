#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运势提醒模块
提供每日运势提醒功能
"""

import os
import json
from datetime import datetime, timedelta
from utils.config import Config
from utils.logger import info, debug


class ReminderManager:
    """提醒管理器"""
    
    def __init__(self):
        self.reminder_file = self._get_reminder_file()
        self.reminders = self._load_reminders()
    
    def _get_reminder_file(self):
        """获取提醒配置文件路径"""
        config_dir = Config.get_config_dir()
        return os.path.join(config_dir, 'reminders.json')
    
    def _load_reminders(self):
        """加载提醒配置"""
        if os.path.exists(self.reminder_file):
            try:
                with open(self.reminder_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                debug(f'加载提醒配置失败：{e}')
                return self._get_default_reminders()
        return self._get_default_reminders()
    
    def _get_default_reminders(self):
        """获取默认提醒配置"""
        return {
            'daily_enabled': False,  # 每日运势提醒开关
            'daily_time': '08:00',   # 每日提醒时间
            'last_reminded': None,   # 上次提醒时间
        }
    
    def _save_reminders(self):
        """保存提醒配置"""
        try:
            config_dir = Config.get_config_dir()
            os.makedirs(config_dir, exist_ok=True)
            
            with open(self.reminder_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, ensure_ascii=False, indent=2)
            
            debug('提醒配置已保存')
        except Exception as e:
            debug(f'保存提醒配置失败：{e}')
    
    def set_daily_reminder(self, enabled, time='08:00'):
        """设置每日运势提醒
        
        Args:
            enabled: True/False
            time: 提醒时间（HH:MM 格式）
        """
        self.reminders['daily_enabled'] = enabled
        self.reminders['daily_time'] = time
        self._save_reminders()
        
        status = '已启用' if enabled else '已禁用'
        info(f'每日运势提醒{status}，时间：{time}')
    
    def should_remind(self):
        """检查是否应该提醒
        
        Returns:
            bool: 是否应该提醒
        """
        if not self.reminders.get('daily_enabled', False):
            return False
        
        # 检查是否今天已经提醒过
        last_reminded = self.reminders.get('last_reminded')
        if last_reminded:
            last_date = datetime.fromisoformat(last_reminded).date()
            today = datetime.now().date()
            if last_date == today:
                return False  # 今天已经提醒过了
        
        # 检查当前时间是否到达提醒时间
        reminder_time = self.reminders.get('daily_time', '08:00')
        try:
            hour, minute = map(int, reminder_time.split(':'))
            now = datetime.now()
            reminder_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 如果当前时间已过提醒时间且今天未提醒
            if now >= reminder_datetime:
                return True
        except Exception as e:
            debug(f'检查提醒时间失败：{e}')
        
        return False
    
    def mark_reminded(self):
        """标记已提醒"""
        self.reminders['last_reminded'] = datetime.now().isoformat()
        self._save_reminders()
        info('已标记今日运势提醒')
    
    def get_reminder_status(self):
        """获取提醒状态"""
        return {
            'enabled': self.reminders.get('daily_enabled', False),
            'time': self.reminders.get('daily_time', '08:00'),
            'last_reminded': self.reminders.get('last_reminded'),
            'next_remind': self._get_next_remind_time()
        }
    
    def _get_next_remind_time(self):
        """获取下次提醒时间"""
        if not self.reminders.get('daily_enabled', False):
            return None
        
        reminder_time = self.reminders.get('daily_time', '08:00')
        try:
            hour, minute = map(int, reminder_time.split(':'))
            now = datetime.now()
            next_remind = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 如果今天的提醒时间已过，则是明天
            if now >= next_remind:
                next_remind += timedelta(days=1)
            
            return next_remind.isoformat()
        except:
            return None
    
    def get_notification_text(self):
        """获取通知文本"""
        return {
            'title': '📅 今日运势提醒',
            'body': '点击查看您的今日运势',
        }


# 全局单例
_reminder_manager = None

def get_reminder_manager():
    """获取提醒管理器单例"""
    global _reminder_manager
    if _reminder_manager is None:
        _reminder_manager = ReminderManager()
    return _reminder_manager
