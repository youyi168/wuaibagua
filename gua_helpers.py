#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卦象辅助模块
宫位映射、二进制解析、每日卦象算法
"""

import random
import hashlib
from datetime import datetime
from android_jni import get_device_id

# ==================== 8 宫映射 ====================
GUA_PALACE_MAP = {
    # 乾宫
    '乾为天': '乾宫', '天风姤': '乾宫', '天山遁': '乾宫', '天地否': '乾宫',
    '风地观': '乾宫', '山地剥': '乾宫', '火地晋': '乾宫', '火天大有': '乾宫',
    # 坎宫
    '坎为水': '坎宫', '水泽节': '坎宫', '水雷屯': '坎宫', '水火既济': '坎宫',
    '泽火革': '坎宫', '雷火丰': '坎宫', '地火明夷': '坎宫', '地水师': '坎宫',
    # 艮宫
    '艮为山': '艮宫', '山火贲': '艮宫', '山天大畜': '艮宫', '山泽损': '艮宫',
    '火泽睽': '艮宫', '天泽履': '艮宫', '风泽中孚': '艮宫', '风山渐': '艮宫',
    # 震宫
    '震为雷': '震宫', '雷地豫': '震宫', '雷水解': '震宫', '雷风恒': '震宫',
    '地风升': '震宫', '水风井': '震宫', '泽风大过': '震宫', '泽雷随': '震宫',
    # 巽宫
    '巽为风': '巽宫', '风天小畜': '巽宫', '风火家人': '巽宫', '风雷益': '巽宫',
    '天雷无妄': '巽宫', '火雷噬嗑': '巽宫', '山雷颐': '巽宫', '山风蛊': '巽宫',
    # 离宫
    '离为火': '离宫', '火山旅': '离宫', '火风鼎': '离宫', '火水未济': '离宫',
    '山水蒙': '离宫', '风水涣': '离宫', '天水讼': '离宫', '天火同人': '离宫',
    # 坤宫
    '坤为地': '坤宫', '地雷复': '坤宫', '地泽临': '坤宫', '地天泰': '坤宫',
    '雷天大壮': '坤宫', '泽天夬': '坤宫', '水天需': '坤宫', '水地比': '坤宫',
    # 兑宫
    '兑为泽': '兑宫', '泽水困': '兑宫', '泽地萃': '兑宫', '泽山咸': '兑宫',
    '水山蹇': '兑宫', '地山谦': '兑宫', '雷山小过': '兑宫', '雷泽归妹': '兑宫',
}


def get_gua_palace(gua_name):
    """获取卦象所属宫位"""
    return GUA_PALACE_MAP.get(gua_name, '')


def get_all_gua_with_palace():
    """获取所有卦象及宫位信息"""
    try:
        import gua_db
        names = gua_db.get_all_gua_names()
        result = []
        for item in names:
            name = item['name']
            palace = get_gua_palace(name)
            result.append({'name': name, 'short': item.get('short_name', name[:2]), 'palace': palace})
        return result
    except Exception as e:
        print(f'[Error] get_all_gua_with_palace: {e}')
        return []


def get_binary_from_name(gua_name):
    """通过卦名获取二进制表示"""
    try:
        import gua_db
        names = gua_db.get_all_gua_names()
        for item in names:
            if item['name'] == gua_name:
                return item.get('binary', '')
    except Exception:
        pass
    try:
        import gua_calculator
        for binary, name in gua_calculator.HEXAGRAM_NAMES.items():
            if name == gua_name:
                return binary
    except Exception:
        pass
    return ''


def yao_lines_from_binary(binary_str):
    """将 6 位二进制字符串转为 6 爻列表（从下往上）"""
    if not binary_str or len(binary_str) != 6:
        return [7, 7, 7, 7, 7, 7]
    return [7 if b == '1' else 8 for b in binary_str]


def gua_name_to_yao(gua_name):
    """通过卦名生成 6 爻列表（无变爻）"""
    try:
        binary = get_binary_from_name(gua_name)
        if not binary or len(binary) != 6:
            return None
        return [7 if b == '1' else 8 for b in binary]
    except Exception:
        return None


def get_daily_gua():
    """
    今日运势算法
    根据日期 + 设备 ID 生成 deterministic 卦象
    """
    try:
        today = datetime.now().strftime('%Y%m%d')
        device_id = get_device_id()
        seed_str = f"{today}_{device_id}"
        seed_hash = hashlib.sha256(seed_str.encode()).hexdigest()
        yao_list = []
        for i in range(6):
            byte_val = int(seed_hash[i * 4:(i + 1) * 4], 16)
            mod = byte_val % 100
            if mod < 10:
                yao = 6
            elif mod < 45:
                yao = 7
            elif mod < 55:
                yao = 8
            else:
                yao = 9
            yao_list.append(yao)
        return yao_list
    except Exception as e:
        print(f'[Error] get_daily_gua: {e}')
        return [random.randint(6, 9) for _ in range(6)]
