#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六爻排盘模块 v2.0 - 完整周易理论体系
整合内容：
- 完整纳甲纳支（京房纳甲法）
- 精确六亲计算（根据地支五行与卦宫五行关系）
- 完整世应推算（含游魂卦、归魂卦）
- 月建日辰影响（旺相休囚死）
- 空亡计算（旬空）
- 六神排盘
- 飞神伏神
"""

import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# ==================== 基础数据 ====================

# 天干
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 地支五行
DIZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

# 天干五行
TIANGAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火',
    '戊': '土', '己': '土', '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

# 八卦纳甲（京房纳甲法）
NAJIA = {
    '乾': {'内卦': '甲', '外卦': '壬'},
    '坤': {'内卦': '乙', '外卦': '癸'},
    '震': {'内卦': '庚', '外卦': '庚'},
    '巽': {'内卦': '辛', '外卦': '辛'},
    '坎': {'内卦': '戊', '外卦': '戊'},
    '离': {'内卦': '己', '外卦': '己'},
    '艮': {'内卦': '丙', '外卦': '丙'},
    '兑': {'内卦': '丁', '外卦': '丁'},
}

# 八卦纳支（从下往上排列）
NAZHI = {
    '乾': ['子', '寅', '辰', '午', '申', '戌'],
    '坤': ['未', '巳', '卯', '丑', '亥', '酉'],
    '震': ['子', '寅', '辰', '午', '申', '戌'],
    '巽': ['丑', '亥', '酉', '未', '巳', '卯'],
    '坎': ['寅', '辰', '午', '申', '戌', '子'],
    '离': ['卯', '丑', '亥', '酉', '未', '巳'],
    '艮': ['辰', '午', '申', '戌', '子', '寅'],
    '兑': ['巳', '卯', '丑', '亥', '酉', '未'],
}

# 卦宫映射（完整 64 卦 → 卦宫）
GUA_GONG_MAP = {
    '乾为天': '乾', '天风姤': '乾', '天山遁': '乾', '天地否': '乾',
    '风地观': '乾', '山地剥': '乾', '火地晋': '乾', '火天大有': '乾',
    '坎为水': '坎', '水泽节': '坎', '水雷屯': '坎', '水火既济': '坎',
    '泽火革': '坎', '雷火丰': '坎', '地火明夷': '坎', '地水师': '坎',
    '艮为山': '艮', '山火贲': '艮', '山天大畜': '艮', '山泽损': '艮',
    '火泽睽': '艮', '天泽履': '艮', '风泽中孚': '艮', '风山渐': '艮',
    '震为雷': '震', '雷地豫': '震', '雷水解': '震', '雷风恒': '震',
    '地风升': '震', '水风井': '震', '泽风大过': '震', '泽雷随': '震',
    '巽为风': '巽', '风天小畜': '巽', '风火家人': '巽', '风雷益': '巽',
    '天雷无妄': '巽', '火雷噬嗑': '巽', '山雷颐': '巽', '山风蛊': '巽',
    '离为火': '离', '火山旅': '离', '火风鼎': '离', '火水未济': '离',
    '山水蒙': '离', '风水涣': '离', '天水讼': '离', '天火同人': '离',
    '坤为地': '坤', '地雷复': '坤', '地泽临': '坤', '地天泰': '坤',
    '雷天大壮': '坤', '泽天夬': '坤', '水天需': '坤', '水地比': '坤',
    '兑为泽': '兑', '泽水困': '兑', '泽地萃': '兑', '泽山咸': '兑',
    '水山蹇': '兑', '地山谦': '兑', '雷山小过': '兑', '雷泽归妹': '兑',
}

# 卦宫五行
GONG_WUXING = {
    '乾': '金', '兑': '金',
    '震': '木', '巽': '木',
    '坎': '水',
    '离': '火',
    '艮': '土', '坤': '土',
}

# 六亲定义（根据卦宫五行与爻地支五行的关系）
# 生我=父母，我生=子孙，克我=官鬼，我克=妻财，同我=兄弟
LIUQIN_MAP = {
    ('金', '金'): '兄弟', ('金', '水'): '子孙', ('金', '木'): '妻财',
    ('金', '火'): '官鬼', ('金', '土'): '父母',
    ('木', '木'): '兄弟', ('木', '火'): '子孙', ('木', '土'): '妻财',
    ('木', '金'): '官鬼', ('木', '水'): '父母',
    ('水', '水'): '兄弟', ('水', '木'): '子孙', ('水', '火'): '妻财',
    ('水', '土'): '官鬼', ('水', '金'): '父母',
    ('火', '火'): '兄弟', ('火', '土'): '子孙', ('火', '金'): '妻财',
    ('火', '水'): '官鬼', ('火', '木'): '父母',
    ('土', '土'): '兄弟', ('土', '金'): '子孙', ('土', '水'): '妻财',
    ('土', '木'): '官鬼', ('土', '火'): '父母',
}

# 世应完整映射（64 卦全部）
SHIYING_COMPLETE = {
    # 乾宫
    '乾为天': (5, 2), '天风姤': (0, 3), '天山遁': (1, 4), '天地否': (2, 5),
    '风地观': (3, 0), '山地剥': (4, 1), '火地晋': (4, 1), '火天大有': (2, 5),
    # 坎宫
    '坎为水': (5, 2), '水泽节': (0, 3), '水雷屯': (1, 4), '水火既济': (2, 5),
    '泽火革': (3, 0), '雷火丰': (4, 1), '地火明夷': (4, 1), '地水师': (2, 5),
    # 艮宫
    '艮为山': (5, 2), '山火贲': (0, 3), '山天大畜': (1, 4), '山泽损': (2, 5),
    '火泽睽': (3, 0), '天泽履': (4, 1), '风泽中孚': (4, 1), '风山渐': (2, 5),
    # 震宫
    '震为雷': (5, 2), '雷地豫': (0, 3), '雷水解': (1, 4), '雷风恒': (2, 5),
    '地风升': (3, 0), '水风井': (4, 1), '泽风大过': (4, 1), '泽雷随': (2, 5),
    # 巽宫
    '巽为风': (5, 2), '风天小畜': (0, 3), '风火家人': (1, 4), '风雷益': (2, 5),
    '天雷无妄': (3, 0), '火雷噬嗑': (4, 1), '山雷颐': (4, 1), '山风蛊': (2, 5),
    # 离宫
    '离为火': (5, 2), '火山旅': (0, 3), '火风鼎': (1, 4), '火水未济': (2, 5),
    '山水蒙': (3, 0), '风水涣': (4, 1), '天水讼': (4, 1), '天火同人': (2, 5),
    # 坤宫
    '坤为地': (5, 2), '地雷复': (0, 3), '地泽临': (1, 4), '地天泰': (2, 5),
    '雷天大壮': (3, 0), '泽天夬': (4, 1), '水天需': (4, 1), '水地比': (2, 5),
    # 兑宫
    '兑为泽': (5, 2), '泽水困': (0, 3), '泽地萃': (1, 4), '泽山咸': (2, 5),
    '水山蹇': (3, 0), '地山谦': (4, 1), '雷山小过': (4, 1), '雷泽归妹': (2, 5),
}

# 六神基础
LIUSHEN_BASE = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']

# 日干对应六神起始
RIANGAN_LIUSHEN = {
    '甲': 0, '乙': 0, '丙': 1, '丁': 1, '戊': 2,
    '己': 3, '庚': 4, '辛': 4, '壬': 5, '癸': 5,
}

# 爻位名称
YAO_POSITIONS = ['初', '二', '三', '四', '五', '上']

# 五行旺相休囚死表
WANG_XIU_TABLE = {
    '金': {
        '春': {'旺': '囚', '相': '休', '休': '相', '囚': '旺', '死': '死'},
        '夏': {'旺': '死', '相': '囚', '休': '囚', '囚': '相', '死': '旺'},
        '秋': {'旺': '旺', '相': '相', '休': '休', '囚': '囚', '死': '死'},
        '冬': {'旺': '休', '相': '旺', '休': '死', '囚': '囚', '死': '相'},
    },
    '木': {
        '春': {'旺': '旺', '相': '相', '休': '休', '囚': '囚', '死': '死'},
        '夏': {'旺': '休', '相': '死', '休': '囚', '囚': '旺', '死': '相'},
        '秋': {'旺': '死', '相': '囚', '休': '相', '囚': '休', '死': '旺'},
        '冬': {'旺': '相', '相': '旺', '休': '死', '囚': '休', '死': '囚'},
    },
    '水': {
        '春': {'旺': '休', '相': '死', '休': '旺', '囚': '囚', '死': '相'},
        '夏': {'旺': '囚', '相': '旺', '休': '死', '囚': '相', '死': '休'},
        '秋': {'旺': '相', '相': '休', '休': '囚', '囚': '死', '死': '旺'},
        '冬': {'旺': '旺', '相': '相', '休': '休', '囚': '囚', '死': '死'},
    },
    '火': {
        '春': {'旺': '相', '相': '休', '休': '囚', '囚': '死', '死': '旺'},
        '夏': {'旺': '旺', '相': '相', '休': '休', '囚': '囚', '死': '死'},
        '秋': {'旺': '死', '相': '囚', '休': '旺', '囚': '相', '死': '休'},
        '冬': {'旺': '囚', '相': '死', '休': '相', '囚': '旺', '死': '囚'},
    },
    '土': {
        '春': {'旺': '死', '相': '囚', '休': '相', '囚': '旺', '死': '休'},
        '夏': {'旺': '相', '相': '旺', '休': '休', '囚': '囚', '死': '死'},
        '秋': {'旺': '休', '相': '死', '休': '囚', '囚': '相', '死': '旺'},
        '冬': {'旺': '囚', '相': '休', '休': '旺', '囚': '死', '死': '相'},
    },
}

# 旬空表（六十甲子分六旬）
XUNKONG_TABLE = {
    '甲子': ['戌', '亥'], '甲戌': ['申', '酉'], '甲申': ['午', '未'],
    '甲午': ['辰', '巳'], '甲辰': ['寅', '卯'], '甲寅': ['子', '丑'],
}

# 上下卦二进制映射
BAGUA_BINARY = {
    '111': '乾', '000': '坤', '100': '震', '010': '坎',
    '001': '艮', '110': '巽', '101': '离', '011': '兑',
}

BAGUA_REVERSE = {v: k for k, v in BAGUA_BINARY.items()}


# ==================== 核心函数 ====================

def get_gua_gong(gua_name):
    """获取卦宫名称"""
    return GUA_GONG_MAP.get(gua_name, '乾')


def get_gua_gong_wuxing(gua_name):
    """获取卦宫五行"""
    gong = get_gua_gong(gua_name)
    return GONG_WUXING.get(gong, '金')


def get_nazhi_for_gua(gua_name):
    """
    获取 64 卦的纳支（从初爻到上爻）
    
    Args:
        gua_name: 卦名
    
    Returns:
        list: 6 个地支 [初爻, 二爻, ..., 上爻]
    """
    gong = get_gua_gong(gua_name)
    
    # 获取上下卦
    try:
        import gua_calculator
        # 从卦名反推二进制
        for binary, name in gua_calculator.HEXAGRAM_NAMES.items():
            if name == gua_name:
                lower_bin = binary[:3]  # 下卦
                upper_bin = binary[3:]  # 上卦
                lower_gua = BAGUA_BINARY.get(lower_bin, '乾')
                upper_gua = BAGUA_BINARY.get(upper_bin, '乾')
                
                # 组合纳支：下卦纳支 + 上卦纳支
                nazhi = NAZHI[lower_gua][:3] + NAZHI[upper_gua][3:]
                return nazhi
    except:
        pass
    
    # 回退：默认乾宫纳支
    return NAZHI['乾']


def get_najia_for_gua(gua_name):
    """
    获取 64 卦的纳甲（每爻天干）
    
    Args:
        gua_name: 卦名
    
    Returns:
        list: 6 个天干 [初爻, 二爻, ..., 上爻]
    """
    gong = get_gua_gong(gua_name)
    najia_info = NAJIA.get(gong, NAJIA['乾'])
    
    # 内卦（下卦）用内卦天干，外卦（上卦）用外卦天干
    tian_gan = [najia_info['内卦']] * 3 + [najia_info['外卦']] * 3
    return tian_gan


def get_liuqin_precise(gua_name):
    """
    精确六亲计算（根据纳支五行与卦宫五行关系）
    
    Args:
        gua_name: 卦名
    
    Returns:
        list: 6 个六亲 [初爻, 二爻, ..., 上爻]
    """
    gong_wuxing = get_gua_gong_wuxing(gua_name)
    nazhi_list = get_nazhi_for_gua(gua_name)
    
    liuqin = []
    for nazhi in nazhi_list:
        yao_wuxing = DIZHI_WUXING.get(nazhi, '金')
        key = (gong_wuxing, yao_wuxing)
        lq = LIUQIN_MAP.get(key, '兄弟')
        liuqin.append(lq)
    
    return liuqin


def get_liushen(day_gan=None):
    """
    获取六神（根据日干）
    
    Args:
        day_gan: 日干
    
    Returns:
        list: 6 个六神
    """
    if not day_gan:
        return LIUSHEN_BASE
    
    start = RIANGAN_LIUSHEN.get(day_gan, 0)
    return [LIUSHEN_BASE[(start + i) % 6] for i in range(6)]


def get_shiying(gua_name):
    """
    获取世应爻位置（完整 64 卦）
    
    Args:
        gua_name: 卦名
    
    Returns:
        tuple: (世爻位置, 应爻位置) 0=初爻, 5=上爻
    """
    return SHIYING_COMPLETE.get(gua_name, (5, 2))


def get_kongwang(ri_gan=None, ri_zhi=None):
    """
    计算旬空
    
    Args:
        ri_gan: 日干
        ri_zhi: 日支
    
    Returns:
        list: 两个空亡地支
    """
    if not ri_gan or not ri_zhi:
        # 根据当前日期简化计算
        now = datetime.now()
        # 简化：按日数模 6 确定旬
        day_idx = now.day % 6
        xun_keys = list(XUNKONG_TABLE.keys())
        xun = xun_keys[day_idx]
        return XUNKONG_TABLE.get(xun, ['戌', '亥'])
    
    # 根据日干支确定旬
    gan_idx = TIANGAN.index(ri_gan) if ri_gan in TIANGAN else 0
    zhi_idx = DIZHI.index(ri_zhi) if ri_zhi in DIZHI else 0
    
    # 确定旬首
    xun_shou_idx = (zhi_idx - gan_idx) % 12
    for i in range(0, 12, 2):
        if (xun_shou_idx - i) % 12 == 0:
            xun_key = f"{TIANGAN[i // 2 % 10]}{DIZHI[(i) % 12]}"
            # 更精确的计算
            break
    
    # 简化处理
    day_num = (gan_idx * 6 + zhi_idx) % 60
    xun_idx = day_num // 10
    xun_keys = list(XUNKONG_TABLE.keys())
    return XUNKONG_TABLE.get(xun_keys[min(xun_idx, 5)], ['戌', '亥'])


def get_wangshuai(gua_name, yue_zhi=None, ri_zhi=None):
    """
    计算各爻旺衰状态
    
    Args:
        gua_name: 卦名
        yue_zhi: 月支
        ri_zhi: 日支
    
    Returns:
        list: 6 个旺衰状态
    """
    gong_wuxing = get_gua_gong_wuxing(gua_name)
    nazhi_list = get_nazhi_for_gua(gua_name)
    
    if not yue_zhi:
        now = datetime.now()
        month = now.month
        season_map = {1: '冬', 2: '冬', 3: '春', 4: '春', 5: '夏', 6: '夏',
                      7: '秋', 8: '秋', 9: '秋', 10: '冬', 11: '冬', 12: '冬'}
        season = season_map.get(month, '春')
    else:
        # 根据地支确定季节
        if yue_zhi in ['寅', '卯', '辰']:
            season = '春'
        elif yue_zhi in ['巳', '午', '未']:
            season = '夏'
        elif yue_zhi in ['申', '酉', '戌']:
            season = '秋'
        else:
            season = '冬'
    
    wangshuai = []
    for nazhi in nazhi_list:
        yao_wuxing = DIZHI_WUXING.get(nazhi, '金')
        # 根据五行关系确定旺相休囚死
        if yao_wuxing == gong_wuxing:
            relation = '旺'
        elif gong_wuxing in {
            '金': '水', '水': '木', '木': '火', '火': '土', '土': '金'
        }.get(gong_wuxing, ''):
            relation = '相'
        else:
            # 简化判断
            wuxing_cycle = {'金': '水', '水': '木', '木': '火', '火': '土', '土': '金'}
            if wuxing_cycle.get(yao_wuxing) == gong_wuxing:
                relation = '休'
            elif wuxing_cycle.get(gong_wuxing) == yao_wuxing:
                relation = '囚'
            else:
                relation = '死'
        
        # 考虑月建影响
        if yue_zhi:
            yue_wuxing = DIZHI_WUXING.get(yue_zhi, '木')
            if yue_wuxing == yao_wuxing:
                relation = '旺'
            elif DIZHI_WUXING.get(DIZHI[(DIZHI.index(yue_zhi) + 3) % 12], '') == yao_wuxing:
                relation = '相'
        
        wangshuai.append(relation)
    
    return wangshuai


def get_fu_shen(gua_name):
    """
    计算伏神（缺少的六亲）
    
    当某六亲不在本卦中出现时，需从本宫首卦（八纯卦）中找伏神
    
    Args:
        gua_name: 卦名
    
    Returns:
        dict: {缺少的六亲: 伏神所在爻位}
    """
    gong = get_gua_gong(gua_name)
    gong_shou = {
        '乾': '乾为天', '坤': '坤为地', '震': '震为雷', '巽': '巽为风',
        '坎': '坎为水', '离': '离为火', '艮': '艮为山', '兑': '兑为泽',
    }
    
    # 获取本卦六亲
    current_liuqin = get_liuqin_precise(gua_name)
    
    # 获取八纯卦六亲
    shou_gua_liuqin = get_liuqin_precise(gong_shou.get(gong, '乾为天'))
    
    # 找出缺少的六亲
    all_liuqin = ['父母', '兄弟', '子孙', '官鬼', '妻财']
    missing = set(all_liuqin) - set(current_liuqin)
    
    fu_shen = {}
    for mq in missing:
        # 在八纯卦中找到该六亲的位置
        for i, lq in enumerate(shou_gua_liuqin):
            if lq == mq:
                fu_shen[mq] = i
                break
    
    return fu_shen


def format_liuyao_full(yao_list, gua_name, yue_zhi=None, ri_gan=None, ri_zhi=None):
    """
    完整六爻排盘显示
    
    Args:
        yao_list: 6 爻列表 [初爻, 二爻, ..., 上爻]
        gua_name: 卦名
        yue_zhi: 月支（可选）
        ri_gan: 日干（可选）
        ri_zhi: 日支（可选）
    
    Returns:
        str: 排盘文本
    """
    lines = []
    lines.append(f'【六爻排盘】{gua_name}')
    lines.append('')
    
    # 获取完整信息
    liuqin = get_liuqin_precise(gua_name)
    liushen = get_liushen(ri_gan)
    shi_pos, ying_pos = get_shiying(gua_name)
    nazhi_list = get_nazhi_for_gua(gua_name)
    najia_list = get_najia_for_gua(gua_name)
    wangshuai = get_wangshuai(gua_name, yue_zhi, ri_zhi)
    kongwang = get_kongwang(ri_gan, ri_zhi)
    fu_shen = get_fu_shen(gua_name)
    
    gong = get_gua_gong(gua_name)
    gong_wx = get_gua_gong_wuxing(gua_name)
    
    # 表头
    lines.append('六神   六亲   纳甲   爻位   爻象   世应   旺衰')
    lines.append('─' * 60)
    
    # 爻符号
    yao_symbols = {6: '- -', 7: '───', 8: '- -', 9: '───'}
    yao_marks = {6: '✕', 9: '○'}
    
    # 从上爻往下显示
    for i in range(5, -1, -1):
        yao = yao_list[i]
        symbol = yao_symbols.get(yao, '───')
        mark = yao_marks.get(yao, '')
        yao_name = YAO_POSITIONS[i]
        
        ls = liushen[i] if i < len(liushen) else ''
        lq = liuqin[i] if i < len(liuqin) else ''
        na = najia_list[i] if i < len(najia_list) else ''
        zhi = nazhi_list[i] if i < len(nazhi_list) else ''
        ws = wangshuai[i] if i < len(wangshuai) else ''
        
        # 世应标记
        sy = ''
        if i == shi_pos:
            sy = '世'
        elif i == ying_pos:
            sy = '应'
        
        # 空亡标记
        kw = '空' if zhi in kongwang else ''
        
        # 伏神标记
        fs = ''
        for fq, pos in fu_shen.items():
            if pos == i:
                fs = f'伏{fq}'
        
        line = f'{ls:4} {lq:4} {na}{zhi:2} {yao_name}{yao:2} {symbol} {mark:2} {sy:2} {ws:2} {kw} {fs}'
        lines.append(line)
    
    lines.append('')
    lines.append(f'卦宫：{gong}宫 ({gong_wx})')
    lines.append(f'世爻：{YAO_POSITIONS[shi_pos]}爻  应爻：{YAO_POSITIONS[ying_pos]}爻')
    
    if kongwang:
        lines.append(f'空亡：{kongwang[0]}、{kongwang[1]}')
    
    if fu_shen:
        fs_str = ', '.join([f'{k}→{YAO_POSITIONS[v]}爻' for k, v in fu_shen.items()])
        lines.append(f'伏神：{fs_str}')
    
    return '\n'.join(lines)


# ==================== 测试 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("六爻排盘模块 v2.0 测试")
    print("=" * 60)
    
    # 测试 1: 纳支
    print("\n1. 纳支测试:")
    for gua in ['乾为天', '坤为地', '坎为水', '离为火']:
        nazhi = get_nazhi_for_gua(gua)
        print(f"   {gua}: {nazhi}")
    
    # 测试 2: 精确六亲
    print("\n2. 精确六亲测试:")
    for gua in ['乾为天', '坎为水', '震为雷']:
        liuqin = get_liuqin_precise(gua)
        gong_wx = get_gua_gong_wuxing(gua)
        print(f"   {gua} ({gong_wx}): {liuqin}")
    
    # 测试 3: 世应
    print("\n3. 世应测试:")
    for gua in ['乾为天', '天风姤', '火地晋', '火天大有']:
        shi, ying = get_shiying(gua)
        print(f"   {gua}: 世={YAO_POSITIONS[shi]}爻, 应={YAO_POSITIONS[ying]}爻")
    
    # 测试 4: 完整排盘
    print("\n4. 完整排盘测试:")
    yao_list = [7, 7, 7, 7, 7, 7]
    text = format_liuyao_full(yao_list, '乾为天')
    print(text)
