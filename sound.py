#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音效管理模块
提供起卦音效、成功音效等音频反馈
"""

import os
from kivy.core.audio import SoundLoader
from logger import info, debug


class SoundManager:
    """音效管理器"""
    
    # 音效文件路径
    SOUND_FILES = {
        'cast': 'sounds/coin_toss.wav',      # 投掷音效
        'result': 'sounds/reveal.wav',       # 显示结果音效
        'success': 'sounds/success.wav',     # 成功音效
        'click': 'sounds/click.wav',         # 点击音效
        'copy': 'sounds/copy.wav',           # 复制音效
    }
    
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.volume = 0.5
        self._load_sounds()
    
    def _load_sounds(self):
        """加载音效"""
        for name, filepath in self.SOUND_FILES.items():
            # 检查文件是否存在
            if os.path.exists(filepath):
                try:
                    sound = SoundLoader.load(filepath)
                    if sound:
                        sound.volume = self.volume
                        self.sounds[name] = sound
                        debug(f'已加载音效：{name}')
                except Exception as e:
                    debug(f'加载音效失败 {name}: {e}')
            else:
                debug(f'音效文件不存在：{filepath}')
    
    def play(self, sound_name):
        """播放音效
        
        Args:
            sound_name: 音效名称
        """
        if not self.enabled:
            return
        
        if sound_name in self.sounds:
            try:
                sound = self.sounds[sound_name]
                sound.seek(0)  # 从头播放
                sound.play()
                debug(f'播放音效：{sound_name}')
            except Exception as e:
                debug(f'播放音效失败：{e}')
    
    def play_cast(self):
        """播放起卦音效"""
        self.play('cast')
    
    def play_result(self):
        """播放结果显示音效"""
        self.play('result')
    
    def play_success(self):
        """播放成功音效"""
        self.play('success')
    
    def play_click(self):
        """播放点击音效"""
        self.play('click')
    
    def play_copy(self):
        """播放复制音效"""
        self.play('copy')
    
    def set_enabled(self, enabled):
        """设置音效开关
        
        Args:
            enabled: True/False
        """
        self.enabled = enabled
        info(f'音效已{"启用" if enabled else "禁用"}')
    
    def set_volume(self, volume):
        """设置音量
        
        Args:
            volume: 0.0 - 1.0
        """
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.volume = self.volume
        info(f'音量设置为：{int(volume * 100)}%')
    
    def get_status(self):
        """获取音效状态"""
        return {
            'enabled': self.enabled,
            'volume': self.volume,
            'loaded_count': len(self.sounds),
            'total_count': len(self.SOUND_FILES)
        }


# 全局单例
_sound_manager = None

def get_sound_manager():
    """获取音效管理器单例"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


# 快捷函数
def play_sound(name):
    """播放音效"""
    get_sound_manager().play(name)

def play_cast():
    """播放起卦音效"""
    get_sound_manager().play_cast()

def play_result():
    """播放结果音效"""
    get_sound_manager().play_result()

def play_success():
    """播放成功音效"""
    get_sound_manager().play_success()
