#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户识别模块
生成和管理用户唯一识别码，用于个性化运势测算
"""

import uuid
import os
import hashlib
from datetime import datetime
from config import Config
from logger import info, debug


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self.user_id = None
        self.device_id = None
        self.user_file = self._get_user_file()
        self._load_or_create_user()
    
    def _get_user_file(self):
        """获取用户配置文件路径"""
        config_dir = Config.get_config_dir()
        return os.path.join(config_dir, 'user.json')
    
    def _load_or_create_user(self):
        """加载或创建用户"""
        if os.path.exists(self.user_file):
            try:
                import json
                with open(self.user_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_id = data.get('user_id')
                    self.device_id = data.get('device_id')
                    info(f'已加载用户 ID: {self.user_id[:8]}...')
            except Exception as e:
                error(f'加载用户信息失败：{e}')
                self._create_user()
        else:
            self._create_user()
    
    def _create_user(self):
        """创建新用户"""
        # 生成用户 ID（UUID）
        self.user_id = str(uuid.uuid4())
        
        # 生成设备 ID（基于设备信息 + 时间戳）
        device_info = f"{os.uname().nodename}-{os.getpid()}-{datetime.now().isoformat()}"
        self.device_id = hashlib.sha256(device_info.encode()).hexdigest()[:16]
        
        # 保存用户信息
        self._save_user()
        
        info(f'创建新用户：{self.user_id[:8]}... (设备：{self.device_id})')
    
    def _save_user(self):
        """保存用户信息"""
        try:
            import json
            config_dir = Config.get_config_dir()
            os.makedirs(config_dir, exist_ok=True)
            
            data = {
                'user_id': self.user_id,
                'device_id': self.device_id,
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(self.user_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            debug(f'用户信息已保存：{self.user_file}')
            
        except Exception as e:
            error(f'保存用户信息失败：{e}')
    
    def get_user_id(self):
        """获取用户 ID"""
        return self.user_id
    
    def get_device_id(self):
        """获取设备 ID"""
        return self.device_id
    
    def get_daily_seed(self, date=None):
        """获取每日运势种子
        
        Args:
            date: 日期（datetime 对象），默认为今天
            
        Returns:
            个性化种子值（整数）
        """
        if date is None:
            date = datetime.now()
        
        # 日期字符串（YYYYMMDD）
        date_str = date.strftime('%Y%m%d')
        
        # 组合种子：用户 ID + 日期
        seed_string = f"{self.user_id}-{date_str}"
        
        # 生成哈希值
        hash_value = hashlib.sha256(seed_string.encode()).hexdigest()
        
        # 转换为整数（取前 8 位十六进制）
        seed = int(hash_value[:8], 16)
        
        debug(f'生成每日种子：{date_str} -> {seed}')
        
        return seed
    
    def get_user_info(self):
        """获取用户信息"""
        return {
            'user_id': self.user_id,
            'user_id_short': self.user_id[:8] + '...',
            'device_id': self.device_id,
            'created_at': self._get_created_at()
        }
    
    def _get_created_at(self):
        """获取创建时间"""
        try:
            import json
            with open(self.user_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('created_at', '未知')
        except:
            return '未知'
    
    def reset_user(self):
        """重置用户（生成新的用户 ID）"""
        if os.path.exists(self.user_file):
            os.remove(self.user_file)
        
        self._create_user()
        info('用户已重置')
    
    def get_fortune_id(self, fortune_type='daily', date=None):
        """获取运势 ID（用于区分不同类型的运势）
        
        Args:
            fortune_type: 运势类型（daily/weekly/monthly）
            date: 日期
            
        Returns:
            运势唯一标识
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y%m%d')
        
        # 运势 ID = 用户 ID + 类型 + 日期
        fortune_id = f"{self.user_id[:8]}-{fortune_type}-{date_str}"
        
        return fortune_id


# 全局单例
_user_manager = None

def get_user_manager():
    """获取用户管理器单例"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager


# 快捷函数
def get_user_id():
    """获取当前用户 ID"""
    return get_user_manager().get_user_id()

def get_daily_seed(date=None):
    """获取每日种子"""
    return get_user_manager().get_daily_seed(date)

def get_fortune_id(fortune_type='daily', date=None):
    """获取运势 ID"""
    return get_user_manager().get_fortune_id(fortune_type, date)
