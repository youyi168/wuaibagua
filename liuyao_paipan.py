#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六爻排盘模块
整合 ichingshifa 完整功能
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'gua_optimized.db')

# 六亲基础（根据卦宫五行推算）
LIUQIN_BASE = {
    '金': ['父母', '兄弟', '子孫', '官鬼', '妻財'],
    '木': ['兄弟', '子孫', '妻財', '官鬼', '父母'],
    '水': ['妻財', '官鬼', '父母', '兄弟', '子孫'],
    '火': ['官鬼', '父母', '兄弟', '子孫', '妻財'],
    '土': ['子孫', '妻財', '官鬼', '父母', '兄弟'],
}

# 六神基础（根据日干）
LIUSHEN_BASE = ['青龍', '朱雀', '勾陳', '螣蛇', '白虎', '玄武']

# 日干对应六神起始
RIANGAN_LIUSHEN = {
    '甲': 0, '乙': 0,  # 甲乙起青龍
    '丙': 1, '丁': 1,  # 丙丁起朱雀
    '戊': 2,           # 戊起勾陳
    '己': 3,           # 己起螣蛇
    '庚': 4, '辛': 4,  # 庚辛起白虎
    '壬': 5, '癸': 5,  # 壬癸起玄武
}

# 世应位置
SHIYING_MAP = {
    0: (0, 3),  # 一世卦：世在初爻，应在四爻
    1: (1, 4),  # 二世卦：世在二爻，应在五爻
    2: (2, 5),  # 三世卦：世在三爻，应在上爻
    3: (3, 0),  # 四世卦：世在四爻，应在初爻
    4: (4, 1),  # 五世卦：世在五爻，应在二爻
    5: (5, 2),  # 六世卦：世在上爻，应在三爻
}


def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def get_liuqin(gua_name, day_gan=None):
    """
    获取六亲（根据卦宫五行推算）
    
    卦宫五行 → 六亲顺序：
    - 金：父母→兄弟→子孙→官鬼→妻财
    - 木：兄弟→子孙→妻财→官鬼→父母
    - 水：妻财→官鬼→父母→兄弟→子孙
    - 火：官鬼→父母→兄弟→子孙→妻财
    - 土：子孙→妻财→官鬼→父母→兄弟
    
    Args:
        gua_name: 卦名
        day_gan: 日干（可选）
    
    Returns:
        list: 六亲列表 [初爻，二爻，..., 上爻]
    """
    # 卦宫五行映射
    GUA_GONG_WUXING = {
        '乾为天': '金', '天风姤': '金', '天山遁': '金', '天地否': '金',
        '风地观': '金', '山地剥': '金', '火地晋': '金', '火天大有': '金',
        '坎为水': '水', '水泽节': '水', '水雷屯': '水', '水火既济': '水',
        '泽火革': '水', '雷火丰': '水', '地火明夷': '水', '地水师': '水',
        '艮为山': '土', '山火贲': '土', '山天大畜': '土', '山泽损': '土',
        '火泽睽': '土', '天泽履': '土', '风泽中孚': '土', '风山渐': '土',
        '震为雷': '木', '雷地豫': '木', '雷水解': '木', '雷风恒': '木',
        '地风升': '木', '水风井': '木', '泽风大过': '木', '泽雷随': '木',
        '巽为风': '木', '风天小畜': '木', '风火家人': '木', '风雷益': '木',
        '天雷无妄': '木', '火雷噬嗑': '木', '山雷颐': '木', '山风蛊': '木',
        '离为火': '火', '火山旅': '火', '火风鼎': '火', '火水未济': '火',
        '山水蒙': '火', '风水涣': '火', '天水讼': '火', '天火同人': '火',
        '坤为地': '土', '地雷复': '土', '地泽临': '土', '地天泰': '土',
        '雷天大壮': '土', '泽天夬': '土', '水天需': '土', '水地比': '土',
        '兑为泽': '金', '泽水困': '金', '泽地萃': '金', '泽山咸': '金',
        '水山蹇': '金', '地山谦': '金', '雷山小过': '金', '雷泽归妹': '金',
    }
    
    # 六亲基础顺序（根据卦宫五行）
    LIUQIN_BASE = {
        '金': ['父母', '兄弟', '子孙', '官鬼', '妻财'],
        '木': ['兄弟', '子孙', '妻财', '官鬼', '父母'],
        '水': ['妻财', '官鬼', '父母', '兄弟', '子孙'],
        '火': ['官鬼', '父母', '兄弟', '子孙', '妻财'],
        '土': ['子孙', '妻财', '官鬼', '父母', '兄弟'],
    }
    
    # 获取卦宫五行
    wuxing = GUA_GONG_WUXING.get(gua_name, '金')
    base = LIUQIN_BASE.get(wuxing, LIUQIN_BASE['金'])
    
    # 6 爻的六亲（循环使用基础顺序）
    liuqin = []
    for i in range(6):
        liuqin.append(base[i % len(base)])
    
    return liuqin


def get_liushen(day_gan=None):
    """
    获取六神
    
    Args:
        day_gan: 日干
    
    Returns:
        list: 六神列表
    """
    if not day_gan:
        now = datetime.now()
        # 简化处理，默认从青龍开始
        return LIUSHEN_BASE
    
    start = RIANGAN_LIUSHEN.get(day_gan, 0)
    return [LIUSHEN_BASE[(start + i) % 6] for i in range(6)]


def get_shiying(gua_name):
    """
    获取世应爻位置
    
    Args:
        gua_name: 卦名
    
    Returns:
        tuple: (世爻位置，应爻位置) 0-5
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT shi_position, ying_position FROM shiying
        WHERE hexagram_id = (SELECT id FROM hexagrams WHERE name = ?)
    ''', (gua_name,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row
    
    # 默认返回一世卦
    return (0, 3)


def get_guagong(gua_name):
    """
    获取卦宫信息
    
    Args:
        gua_name: 卦名
    
    Returns:
        dict: {palace_name, palace_element}
    """
    # 卦宫映射
    GUA_GONG = {
        '乾为天': ('乾宫', '金'), '天风姤': ('乾宫', '金'), '天山遁': ('乾宫', '金'), '天地否': ('乾宫', '金'),
        '风地观': ('乾宫', '金'), '山地剥': ('乾宫', '金'), '火地晋': ('乾宫', '金'), '火天大有': ('乾宫', '金'),
        '坎为水': ('坎宫', '水'), '水泽节': ('坎宫', '水'), '水雷屯': ('坎宫', '水'), '水火既济': ('坎宫', '水'),
        '泽火革': ('坎宫', '水'), '雷火丰': ('坎宫', '水'), '地火明夷': ('坎宫', '水'), '地水师': ('坎宫', '水'),
        '艮为山': ('艮宫', '土'), '山火贲': ('艮宫', '土'), '山天大畜': ('艮宫', '土'), '山泽损': ('艮宫', '土'),
        '火泽睽': ('艮宫', '土'), '天泽履': ('艮宫', '土'), '风泽中孚': ('艮宫', '土'), '风山渐': ('艮宫', '土'),
        '震为雷': ('震宫', '木'), '雷地豫': ('震宫', '木'), '雷水解': ('震宫', '木'), '雷风恒': ('震宫', '木'),
        '地风升': ('震宫', '木'), '水风井': ('震宫', '木'), '泽风大过': ('震宫', '木'), '泽雷随': ('震宫', '木'),
        '巽为风': ('巽宫', '木'), '风天小畜': ('巽宫', '木'), '风火家人': ('巽宫', '木'), '风雷益': ('巽宫', '木'),
        '天雷无妄': ('巽宫', '木'), '火雷噬嗑': ('巽宫', '木'), '山雷颐': ('巽宫', '木'), '山风蛊': ('巽宫', '木'),
        '离为火': ('离宫', '火'), '火山旅': ('离宫', '火'), '火风鼎': ('离宫', '火'), '火水未济': ('离宫', '火'),
        '山水蒙': ('离宫', '火'), '风水涣': ('离宫', '火'), '天水讼': ('离宫', '火'), '天火同人': ('离宫', '火'),
        '坤为地': ('坤宫', '土'), '地雷复': ('坤宫', '土'), '地泽临': ('坤宫', '土'), '地天泰': ('坤宫', '土'),
        '雷天大壮': ('坤宫', '土'), '泽天夬': ('坤宫', '土'), '水天需': ('坤宫', '土'), '水地比': ('坤宫', '土'),
        '兑为泽': ('兑宫', '金'), '泽水困': ('兑宫', '金'), '泽地萃': ('兑宫', '金'), '泽山咸': ('兑宫', '金'),
        '水山蹇': ('兑宫', '金'), '地山谦': ('兑宫', '金'), '雷山小过': ('兑宫', '金'), '雷泽归妹': ('兑宫', '金'),
    }
    
    return GUA_GONG.get(gua_name, ('', ''))


def format_liuyao_full(yao_list, gua_name, day_gan=None):
    """
    完整六爻排盘显示
    
    Args:
        yao_list: 6 爻列表
        gua_name: 卦名
        day_gan: 日干
    
    Returns:
        str: 排盘文本
    """
    lines = []
    lines.append(f'【六爻排盘】{gua_name}')
    lines.append('')
    
    # 获取六亲、六神、世应
    liuqin = get_liuqin(gua_name, day_gan)
    liushen = get_liushen(day_gan)
    shi_pos, ying_pos = get_shiying(gua_name)
    guagong = get_guagong(gua_name)
    
    # 爻符号
    yao_symbols = {6: '- -', 7: '───', 8: '- -', 9: '───'}
    yao_marks = {6: '✕', 9: '○'}
    yao_names = ['初', '二', '三', '四', '五', '上']
    
    # 表头
    lines.append('六神   六亲   爻位   爻象   世应')
    lines.append('─' * 50)
    
    # 从上爻往下显示
    for i in range(5, -1, -1):
        yao = yao_list[i]
        symbol = yao_symbols.get(yao, '───')
        mark = yao_marks.get(yao, '')
        yao_name = yao_names[i]
        
        # 六神、六亲
        ls = liushen[i] if i < len(liushen) else ''
        lq = liuqin[i] if i < len(liuqin) else ''
        
        # 世应标记
        sy = ''
        if i == shi_pos:
            sy = '世'
        elif i == ying_pos:
            sy = '应'
        
        line = f'{ls:4} {lq:4} {yao_name}{yao:2} {symbol} {mark:2} {sy}'
        lines.append(line)
    
    lines.append('')
    palace_name, palace_element = get_guagong(gua_name)
    lines.append(f'卦宫：{palace_name} ({palace_element})')
    lines.append(f'世爻：{yao_names[shi_pos]}爻  应爻：{yao_names[ying_pos]}爻')
    
    return '\n'.join(lines)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("六爻排盘模块测试")
    print("=" * 60)
    
    # 测试乾为天
    yao_list = [9, 9, 9, 9, 9, 9]
    text = format_liuyao_full(yao_list, '乾为天')
    print("\n乾为天:")
    print(text)
