#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卦象数据库查询模块
"""

import sqlite3
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_data_path():
    """
    获取数据目录路径
    
    回退优先级：
    1. 环境变量 WUAIBAGUA_DATA
    2. Android 应用私有目录
    3. 开发环境（项目目录）
    4. 用户主目录（最后回退）
    """
    # 1. 环境变量
    if os.getenv('WUAIBAGUA_DATA'):
        data_path = Path(os.getenv('WUAIBAGUA_DATA'))
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path
    
    # 2. Android 环境
    try:
        from android.storage import app_storage_path
        android_path = Path(app_storage_path()) / 'data'
        android_path.mkdir(parents=True, exist_ok=True)
        return android_path
    except ImportError:
        pass
    
    # 3. 开发环境（项目目录）
    dev_path = Path(__file__).parent / 'data'
    if dev_path.exists():
        return dev_path
    
    # 4. 用户主目录（最后回退）
    user_path = Path.home() / '.wuaibagua' / 'data'
    user_path.mkdir(parents=True, exist_ok=True)
    return user_path

DB_PATH = get_data_path() / 'gua_optimized.db'

def get_connection():
    """获取数据库连接"""
    try:
        return sqlite3.connect(DB_PATH)
    except Exception as e:
        logger.error(f'get_connection error: {e}')
        return None

def get_gua_by_name(gua_name):
    """
    根据卦名查询卦象信息
    
    Args:
        gua_name: 卦名全称（如'乾为天'）
    
    Returns:
        dict: 卦象信息，不存在则返回 None
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT h.*, b.content as bai_hua
                FROM hexagrams h
                LEFT JOIN bai_hua b ON h.id = b.hexagram_id
                WHERE h.name = ?
            ''', (gua_name,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f'get_gua_by_name error: {e}')
        return None

def get_gua_by_short_name(short_name):
    """根据卦名简称查询"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM hexagrams WHERE short_name = ?', (short_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f'get_gua_by_short_name error: {e}')
        return None

def get_gua_by_binary(binary):
    """根据二进制查询"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM hexagrams WHERE binary = ?', (binary,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f'get_gua_by_binary error: {e}')
        return None

def get_yao_ci(gua_name):
    """
    获取卦象的所有爻辞
    
    Args:
        gua_name: 卦名全称
    
    Returns:
        list: 爻辞列表，按爻位排序
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT y.*
                FROM yao_ci y
                JOIN hexagrams h ON y.hexagram_id = h.id
                WHERE h.name = ?
                ORDER BY y.position
            ''', (gua_name,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f'get_yao_ci error: {e}')
        return []

def get_all_gua_names():
    """获取所有卦名"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT name, short_name, binary FROM hexagrams ORDER BY id')
            rows = cursor.fetchall()
            return [{'name': r[0], 'short_name': r[1], 'binary': r[2]} for r in rows]
    except Exception as e:
        logger.error(f'get_all_gua_names error: {e}')
        return []

def search_gua(keyword):
    """
    搜索卦象
    
    Args:
        keyword: 搜索关键词
    
    Returns:
        list: 匹配的卦象列表
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT h.name, h.short_name, h.description
                FROM hexagrams h
                WHERE h.name LIKE ? OR h.short_name LIKE ? OR h.description LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f'search_gua error: {e}')
        return []

# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("卦象数据库查询测试")
    print("=" * 60)
    
    # 测试 1: 按名称查询
    print("\n1. 按名称查询 - 乾为天:")
    gua = get_gua_by_name('乾为天')
    if gua:
        print(f"   卦名：{gua['name']}")
        print(f"  简称：{gua['short_name']}")
        print(f"  二进制：{gua['binary']}")
        print(f"  卦辞：{gua['description'][:30]}...")
        print(f"  大象：{gua['da_xiang']}")
    
    # 测试 2: 获取爻辞
    print("\n2. 获取爻辞 - 乾为天:")
    yao_list = get_yao_ci('乾为天')
    for yao in yao_list[:3]:
        print(f"   {yao['yao_name']}: {yao['yao_text'][:20]}...")
    
    # 测试 3: 获取所有卦名
    print(f"\n3. 卦象总数：{len(get_all_gua_names())}")
    
    # 测试 4: 搜索
    print("\n4. 搜索'龙':")
    results = search_gua('龙')
    for r in results[:3]:
        print(f"   {r['name']}: {r['description'][:20]}...")
