#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
起卦历史管理模块
保存、查询、管理用户的起卦记录
"""

import json
import os
import threading
import tempfile
from datetime import datetime
from config import Config


class HistoryManager:
    """起卦历史管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.history_file = Config.get_history_file()
        self.max_records = Config.HISTORY_MAX_RECORDS
        self._history_lock = threading.Lock()  # 保护历史记录操作
        self.history = self._load_history()
    
    @classmethod
    def get_instance(cls):
        """线程安全的单例获取方法"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
    
    def _load_history(self):
        """加载历史记录"""
        if not Config.HISTORY_ENABLED:
            return []
        
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 限制最大记录数
                    return data[:self.max_records]
            except Exception as e:
                print(f'[HISTORY] 加载历史记录失败：{e}')
                return []
        return []
    
    def _save_history(self):
        """保存历史记录（使用原子操作）"""
        if not Config.HISTORY_ENABLED:
            return
        
        with self._history_lock:
            try:
                # 确保目录存在
                history_dir = os.path.dirname(self.history_file)
                os.makedirs(history_dir, exist_ok=True)
                
                # 限制最大记录数
                records = self.history[:self.max_records]
                
                # 原子写入：先写临时文件，再重命名
                fd, temp_path = tempfile.mkstemp(suffix='.json.tmp', dir=history_dir)
                try:
                    with os.fdopen(fd, 'w', encoding='utf-8') as f:
                        json.dump(records, f, ensure_ascii=False, indent=2)
                    # 原子重命名
                    os.replace(temp_path, self.history_file)
                except:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    raise
            except Exception as e:
                print(f'[HISTORY] 保存历史记录失败：{e}')
    
    def add_record(self, result, manual_mode=False, topic=''):
        """添加起卦记录
        
        Args:
            result: 起卦结果字典（包含 ben_gua, bian_gua, dong_yao 等）
            manual_mode: 是否为手动起卦
            topic: 占卜事项
        """
        if not Config.HISTORY_ENABLED:
            return
        
        with self._history_lock:
            try:
                ben_gua = result.get('ben_gua', {})
                bian_gua = result.get('bian_gua')
                dong_yao = result.get('dong_yao', [])
                yao_list = result.get('yao_list', [])
                
                # 构建记录
                record = {
                    'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
                    'timestamp': datetime.now().isoformat(),
                    'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    
                    # 本卦信息
                    'ben_gua_name': ben_gua.get('name', '未知'),
                    'ben_gua_upper': ben_gua.get('upper_name', ''),
                    'ben_gua_lower': ben_gua.get('lower_name', ''),
                    
                    # 变卦信息
                    'bian_gua_name': bian_gua.get('name') if bian_gua else None,
                    
                    # 动爻信息
                    'dong_yao': dong_yao,
                    'dong_yao_count': len(dong_yao),
                    
                    # 起卦方式
                    'mode': 'manual' if manual_mode else 'auto',
                    
                    # 占卜事项
                    'topic': topic if topic else None,
                    
                    # 六爻详情（可选，占用空间较大）
                    # 'yao_list': yao_list
                }
                
                # 添加到开头（最新的在前）
                self.history.insert(0, record)
                
                # 保存
                self._save_history()
                
                print(f'[HISTORY] 已添加记录：{record["ben_gua_name"]}（动爻：{len(dong_yao)}）')
                
            except Exception as e:
                print(f'[HISTORY] 添加记录失败：{e}')
    
    def get_history(self, limit=10):
        """获取历史记录
        
        Args:
            limit: 返回记录数量
            
        Returns:
            历史记录列表
        """
        with self._history_lock:
            return self.history[:limit]
    
    def get_record(self, record_id):
        """获取单条记录
        
        Args:
            record_id: 记录 ID
            
        Returns:
            记录字典，不存在返回 None
        """
        with self._history_lock:
            for record in self.history:
                if record.get('id') == record_id:
                    return record
            return None
    
    def delete_record(self, record_id):
        """删除记录
        
        Args:
            record_id: 记录 ID
            
        Returns:
            是否删除成功
        """
        with self._history_lock:
            for i, record in enumerate(self.history):
                if record.get('id') == record_id:
                    del self.history[i]
                    self._save_history()
                    print(f'[HISTORY] 已删除记录：{record_id}')
                    return True
            return False
    
    def clear_history(self):
        """清空历史记录"""
        with self._history_lock:
            self.history = []
            self._save_history()
            print('[HISTORY] 已清空历史记录')
    
    def get_statistics(self):
        """获取统计信息"""
        with self._history_lock:
            if not self.history:
                return {
                    'total': 0,
                    'auto_count': 0,
                    'manual_count': 0,
                    'dong_gua_count': 0,
                    'jing_gua_count': 0
                }
            
            total = len(self.history)
            auto_count = sum(1 for r in self.history if r.get('mode') == 'auto')
            manual_count = sum(1 for r in self.history if r.get('mode') == 'manual')
            dong_gua_count = sum(1 for r in self.history if r.get('dong_yao_count', 0) > 0)
            jing_gua_count = sum(1 for r in self.history if r.get('dong_yao_count', 0) == 0)
            
            # 统计最常见的卦
            gua_count = {}
            for record in self.history:
                gua_name = record.get('ben_gua_name', '未知')
                gua_count[gua_name] = gua_count.get(gua_name, 0) + 1
            
            # 出现次数最多的卦
            most_common_gua = None
            max_count = 0
            for gua_name, count in gua_count.items():
                if count > max_count:
                    max_count = count
                    most_common_gua = gua_name
            
            return {
                'total': total,
                'auto_count': auto_count,
                'manual_count': manual_count,
                'dong_gua_count': dong_gua_count,
                'jing_gua_count': jing_gua_count,
                'most_common_gua': most_common_gua,
                'most_common_count': max_count
            }
    
    def search_by_gua(self, gua_name, limit=10):
        """根据卦名搜索历史记录
        
        Args:
            gua_name: 卦名
            limit: 返回数量
            
        Returns:
            匹配的记录列表
        """
        with self._history_lock:
            results = []
            for record in self.history:
                if record.get('ben_gua_name') == gua_name:
                    results.append(record)
                    if len(results) >= limit:
                        break
            return results
    
    def export_to_json(self, output_file=None):
        """导出历史记录为 JSON 文件
        
        Args:
            output_file: 输出文件路径（默认导出到配置目录）
            
        Returns:
            导出文件路径
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(
                Config.get_config_dir(),
                f'history_export_{timestamp}.json'
            )
        
        with self._history_lock:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.history, f, ensure_ascii=False, indent=2)
                
                print(f'[HISTORY] 已导出 {len(self.history)} 条记录到：{output_file}')
                return output_file
            except Exception as e:
                print(f'[HISTORY] 导出失败：{e}')
                return None


# 全局单例（使用线程安全的 get_instance）
def get_history_manager():
    """获取历史记录管理器单例（线程安全）"""
    return HistoryManager.get_instance()
