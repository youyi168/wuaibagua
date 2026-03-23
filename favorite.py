#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卦象收藏管理模块
支持收藏、标签、搜索等功能
"""

import json
import os
import threading
import tempfile
from datetime import datetime
from config import Config
from logger import info, debug


class FavoriteManager:
    """卦象收藏管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.favorites_file = self._get_favorites_file()
        self.favorites = self._load_favorites()
        self.tags = self._get_all_tags()
        self._favorites_lock = threading.Lock()  # 保护收藏操作
    
    @classmethod
    def get_instance(cls):
        """线程安全的单例获取方法"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
    
    def _get_favorites_file(self):
        """获取收藏文件路径"""
        config_dir = Config.get_config_dir()
        return os.path.join(config_dir, 'favorites.json')
    
    def _load_favorites(self):
        """加载收藏"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                debug(f'加载收藏失败：{e}')
                return []
        return []
    
    def _save_favorites(self):
        """保存收藏（使用原子操作）"""
        with self._favorites_lock:
            try:
                config_dir = Config.get_config_dir()
                os.makedirs(config_dir, exist_ok=True)
                
                # 原子写入：先写临时文件，再重命名
                fd, temp_path = tempfile.mkstemp(suffix='.json.tmp', dir=config_dir)
                try:
                    with os.fdopen(fd, 'w', encoding='utf-8') as f:
                        json.dump(self.favorites, f, ensure_ascii=False, indent=2)
                    # 原子重命名
                    os.replace(temp_path, self.favorites_file)
                except:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    raise
                
                debug(f'收藏已保存：{len(self.favorites)} 条')
            except Exception as e:
                debug(f'保存收藏失败：{e}')
    
    def add_favorite(self, result, tags=[], note=''):
        """收藏卦象
        
        Args:
            result: 起卦结果字典
            tags: 标签列表
            note: 备注
        
        Returns:
            收藏 ID
        """
        with self._favorites_lock:
            ben_gua = result.get('ben_gua', {})
            bian_gua = result.get('bian_gua')
            
            favorite = {
                'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
                'created_at': datetime.now().isoformat(),
                
                # 卦象信息
                'ben_gua_name': ben_gua.get('name', '未知'),
                'ben_gua_upper': ben_gua.get('upper_name', ''),
                'ben_gua_lower': ben_gua.get('lower_name', ''),
                'bian_gua_name': bian_gua.get('name') if bian_gua else None,
                
                # 动爻
                'dong_yao': result.get('dong_yao', []),
                'dong_yao_count': len(result.get('dong_yao', [])),
                
                # 收藏信息
                'tags': tags,
                'note': note,
                'topic': result.get('topic', ''),  # 占卜事项
                
                # 完整结果（可选）
                # 'result': result
            }
            
            self.favorites.insert(0, favorite)
            self._save_favorites()
            
            # 更新标签
            self._update_tags(tags)
            
            info(f'已收藏：{favorite["ben_gua_name"]}')
            
            return favorite['id']
    
    def remove_favorite(self, favorite_id):
        """删除收藏
        
        Args:
            favorite_id: 收藏 ID
        
        Returns:
            是否删除成功
        """
        with self._favorites_lock:
            for i, fav in enumerate(self.favorites):
                if fav.get('id') == favorite_id:
                    del self.favorites[i]
                    self._save_favorites()
                    info(f'已删除收藏：{favorite_id}')
                    return True
            return False
    
    def get_favorites(self, limit=50):
        """获取收藏列表
        
        Args:
            limit: 返回数量
        
        Returns:
            收藏列表
        """
        with self._favorites_lock:
            return self.favorites[:limit]
    
    def get_favorite(self, favorite_id):
        """获取单个收藏
        
        Args:
            favorite_id: 收藏 ID
        
        Returns:
            收藏字典，不存在返回 None
        """
        with self._favorites_lock:
            for fav in self.favorites:
                if fav.get('id') == favorite_id:
                    return fav
            return None
    
    def search_by_tag(self, tag):
        """按标签搜索
        
        Args:
            tag: 标签名
        
        Returns:
            匹配的收藏列表
        """
        with self._favorites_lock:
            results = []
            for fav in self.favorites:
                if tag in fav.get('tags', []):
                    results.append(fav)
            return results
    
    def search_by_gua(self, gua_name):
        """按卦名搜索
        
        Args:
            gua_name: 卦名
        
        Returns:
            匹配的收藏列表
        """
        with self._favorites_lock:
            results = []
            for fav in self.favorites:
                if fav.get('ben_gua_name') == gua_name:
                    results.append(fav)
            return results
    
    def update_tags(self, favorite_id, tags):
        """更新标签
        
        Args:
            favorite_id: 收藏 ID
            tags: 新标签列表
        
        Returns:
            是否更新成功
        """
        with self._favorites_lock:
            fav = self.get_favorite(favorite_id)
            if fav:
                fav['tags'] = tags
                self._save_favorites()
                self._update_tags(tags)
                info(f'已更新标签：{tags}')
                return True
            return False
    
    def update_note(self, favorite_id, note):
        """更新备注
        
        Args:
            favorite_id: 收藏 ID
            note: 新备注
        
        Returns:
            是否更新成功
        """
        with self._favorites_lock:
            fav = self.get_favorite(favorite_id)
            if fav:
                fav['note'] = note
                self._save_favorites()
                info(f'已更新备注：{note}')
                return True
            return False
    
    def _get_all_tags(self):
        """获取所有标签"""
        tags = set()
        for fav in self.favorites:
            for tag in fav.get('tags', []):
                tags.add(tag)
        return list(tags)
    
    def _update_tags(self, new_tags):
        """更新标签列表"""
        for tag in new_tags:
            if tag not in self.tags:
                self.tags.append(tag)
    
    def get_statistics(self):
        """获取统计信息"""
        with self._favorites_lock:
            total = len(self.favorites)
            
            # 按卦名统计
            gua_count = {}
            for fav in self.favorites:
                gua_name = fav.get('ben_gua_name', '未知')
                gua_count[gua_name] = gua_count.get(gua_name, 0) + 1
            
            # 按标签统计
            tag_count = {}
            for fav in self.favorites:
                for tag in fav.get('tags', []):
                    tag_count[tag] = tag_count.get(tag, 0) + 1
            
            # 动爻统计
            dong_count = sum(1 for fav in self.favorites if fav.get('dong_yao_count', 0) > 0)
            
            return {
                'total': total,
                'gua_count': gua_count,
                'tag_count': tag_count,
                'dong_count': dong_count,
                'jing_count': total - dong_count
            }
    
    def export_to_json(self, output_file=None):
        """导出收藏为 JSON
        
        Args:
            output_file: 输出文件路径
        
        Returns:
            导出文件路径
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(
                Config.get_config_dir(),
                f'favorites_export_{timestamp}.json'
            )
        
        with self._favorites_lock:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.favorites, f, ensure_ascii=False, indent=2)
                
                info(f'已导出 {len(self.favorites)} 条收藏到：{output_file}')
                return output_file
            except Exception as e:
                debug(f'导出失败：{e}')
                return None
    
    def clear_favorites(self):
        """清空所有收藏"""
        with self._favorites_lock:
            self.favorites = []
            self.tags = []
            self._save_favorites()
            info('已清空所有收藏')


# 全局单例（使用线程安全的 get_instance）
def get_favorite_manager():
    """获取收藏管理器单例（线程安全）"""
    return FavoriteManager.get_instance()
