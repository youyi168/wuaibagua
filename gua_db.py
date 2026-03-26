#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卦象数据库查询模块
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'gua_database.db')

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)

def get_gua_by_name(gua_name):
    """
    根据卦名查询卦象信息
    
    Args:
        gua_name: 卦名全称（如'乾为天'）
    
    Returns:
        dict: 卦象信息
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT h.*, b.content as bai_hua
        FROM hexagrams h
        LEFT JOIN bai_hua b ON h.id = b.hexagram_id
        WHERE h.name = ?
    ''', (gua_name,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_gua_by_short_name(short_name):
    """根据卦名简称查询"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM hexagrams WHERE short_name = ?', (short_name,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def get_gua_by_binary(binary):
    """根据二进制查询"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM hexagrams WHERE binary = ?', (binary,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def get_yao_ci(gua_name):
    """
    获取卦象的所有爻辞
    
    Args:
        gua_name: 卦名全称
    
    Returns:
        list: 爻辞列表，按爻位排序
    """
    conn = get_connection()
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
    conn.close()
    
    return [dict(row) for row in rows]

def get_all_gua_names():
    """获取所有卦名"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name, short_name, binary FROM hexagrams ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    
    return [{'name': r[0], 'short_name': r[1], 'binary': r[2]} for r in rows]

def search_gua(keyword):
    """
    搜索卦象
    
    Args:
        keyword: 搜索关键词
    
    Returns:
        list: 匹配的卦象列表
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT h.name, h.short_name, h.description
        FROM hexagrams h
        WHERE h.name LIKE ? OR h.short_name LIKE ? OR h.description LIKE ?
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

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
