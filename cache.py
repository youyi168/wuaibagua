#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卦象数据缓存模块
缓存已加载的卦象数据，提升加载速度
"""

import json
import os
import hashlib
import time
from config import Config


class GuaDataCache:
    """卦象数据缓存管理器"""
    
    def __init__(self):
        self.cache_file = Config.get_cache_file()
        self.max_age = Config.CACHE_MAX_AGE  # 缓存有效期（秒）
        self.max_size = Config.CACHE_MAX_SIZE  # 最大缓存数量
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """加载缓存"""
        if not Config.CACHE_ENABLED:
            return {}
        
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                    # 清理过期缓存
                    current_time = time.time()
                    expired_keys = []
                    
                    for key, value in cache_data.items():
                        if isinstance(value, dict):
                            timestamp = value.get('timestamp', 0)
                            if current_time - timestamp > self.max_age:
                                expired_keys.append(key)
                    
                    # 删除过期缓存
                    for key in expired_keys:
                        del cache_data[key]
                    
                    if expired_keys:
                        self._save_cache(cache_data)
                        print(f'[CACHE] 清理了 {len(expired_keys)} 条过期缓存')
                    
                    return cache_data
                    
            except Exception as e:
                print(f'[CACHE] 加载缓存失败：{e}')
                return {}
        
        return {}
    
    def _save_cache(self, cache_data=None):
        """保存缓存"""
        if not Config.CACHE_ENABLED:
            return
        
        if cache_data is None:
            cache_data = self.cache
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            # 限制缓存大小
            if len(cache_data) > self.max_size:
                # 按时间戳排序，保留最新的
                sorted_items = sorted(
                    cache_data.items(),
                    key=lambda x: x[1].get('timestamp', 0),
                    reverse=True
                )[:self.max_size]
                cache_data = dict(sorted_items)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f'[CACHE] 保存缓存失败：{e}')
    
    def _calculate_hash(self, content):
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get(self, gua_name, file_path):
        """获取卦象数据（带缓存）
        
        Args:
            gua_name: 卦名
            file_path: 数据文件路径
            
        Returns:
            卦象数据字符串
        """
        if not Config.CACHE_ENABLED:
            return self._read_file(gua_name, file_path)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"{gua_name}的数据文件不存在"
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 计算文件哈希
            file_hash = self._calculate_hash(content)
            
            # 检查缓存
            if gua_name in self.cache:
                cached = self.cache[gua_name]
                
                # 验证哈希是否匹配
                if cached.get('hash') == file_hash:
                    # 验证是否过期
                    current_time = time.time()
                    if current_time - cached.get('timestamp', 0) < self.max_age:
                        print(f'[CACHE] 命中缓存：{gua_name}')
                        return cached.get('content', content)
            
            # 更新缓存
            self.cache[gua_name] = {
                'hash': file_hash,
                'content': content,
                'timestamp': time.time(),
                'file_path': file_path
            }
            
            # 保存缓存
            self._save_cache()
            
            print(f'[CACHE] 已缓存：{gua_name}')
            return content
            
        except Exception as e:
            print(f'[CACHE] 读取失败：{e}')
            return f"{gua_name}的数据加载失败：{str(e)}"
    
    def _read_file(self, gua_name, file_path):
        """直接读取文件（不使用缓存）"""
        if not os.path.exists(file_path):
            return f"{gua_name}的数据文件不存在"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"{gua_name}的数据加载失败：{str(e)}"
    
    def clear(self, gua_name=None):
        """清空缓存
        
        Args:
            gua_name: 指定卦名（清空该卦的缓存），为 None 时清空所有
        """
        if gua_name:
            if gua_name in self.cache:
                del self.cache[gua_name]
                print(f'[CACHE] 已清除缓存：{gua_name}')
        else:
            self.cache = {}
            print('[CACHE] 已清空所有缓存')
        
        self._save_cache()
    
    def get_stats(self):
        """获取缓存统计信息"""
        total_size = len(self.cache)
        total_bytes = sum(
            len(json.dumps(v, ensure_ascii=False))
            for v in self.cache.values()
        )
        
        # 按卦名统计
        gua_names = list(self.cache.keys())
        
        return {
            'total_count': total_size,
            'total_size_bytes': total_bytes,
            'total_size_kb': round(total_bytes / 1024, 2),
            'gua_names': gua_names,
            'max_size': self.max_size,
            'usage_percent': round(total_size / self.max_size * 100, 1) if self.max_size > 0 else 0
        }
    
    def print_stats(self):
        """打印缓存统计信息"""
        stats = self.get_stats()
        print('=' * 50)
        print('📊 缓存统计')
        print(f'缓存数量：{stats["total_count"]} / {stats["max_size"]}')
        print(f'缓存大小：{stats["total_size_kb"]} KB')
        print(f'使用率：{stats["usage_percent"]}%')
        if stats['gua_names']:
            print(f'已缓存：{", ".join(stats["gua_names"][:10])}' + 
                  ('...' if len(stats['gua_names']) > 10 else ''))
        print('=' * 50)


# 全局单例
_cache_manager = None

def get_cache_manager():
    """获取缓存管理器单例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = GuaDataCache()
    return _cache_manager
