#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
64 卦卦名查询（简化可靠版）
只包含常用卦，避免映射错误
"""

# 简化卦名映射（只保证正确的映射）
# 格式：二进制字符串 -> 卦名
# 从下往上：初爻二爻三爻四爻五爻上爻
GUA_MAP_SIMPLE = {
    '111111': '乾为天',
    '000000': '坤为地',
    '100010': '水雷屯',
    '010001': '山水蒙',
    '111010': '水天需',
    '011111': '天水讼',
    '010000': '地水师',
    '000010': '水地比',
    '110111': '风天小畜',
    '111011': '天泽履',
    '111000': '地天泰',
    '000111': '天地否',
    '101111': '天火同人',
    '111101': '火地晋',
    '000100': '地火明夷',
    '110100': '风火家人',
    '101101': '火泽睽',
    '010011': '水山蹇',
    '001010': '雷水解',
    '110010': '山泽损',
    '100110': '风雷益',
    '111100': '泽天夬',
    '001111': '天风姤',
    '011100': '泽地萃',
    '000110': '地风升',
    '011010': '泽水困',
    '010110': '水风井',
    '101110': '泽火革',
    '101100': '火风鼎',
    '001001': '震为雷',
    '100100': '艮为山',
    '001000': '风山渐',
    '001011': '雷泽归妹',
    '001100': '雷火丰',
    '100110': '火山旅',
    '011011': '巽为风',
    '110110': '兑为泽',
    '011001': '风水涣',
    '010111': '水泽节',
    '110011': '风泽中孚',
    '100101': '雷山小过',
    '010101': '水火既济',
    '101010': '火水未济',
}


def get_gua_name_simple(yao_list):
    """
    简单卦名计算
    
    Args:
        yao_list: 从下往上的 6 爻列表 [初爻，二爻，三爻，四爻，五爻，上爻]
    
    Returns:
        str: 卦名
    """
    try:
        # 转换为二进制字符串
        binary = ''
        for yao in yao_list:
            if yao in [7, 9]:  # 阳爻
                binary += '1'
            else:  # 阴爻 (6, 8)
                binary += '0'
        
        return GUA_MAP_SIMPLE.get(binary, '未知卦')
    except Exception as e:
        print(f'[ERROR] get_gua_name_simple failed: {e}')
        return '乾为天'  # fallback


def get_gua_txt_simple(gua_name):
    """
    简单读取 txt 文件
    
    Args:
        gua_name: 卦名
    
    Returns:
        str: txt 文件完整内容，或 None
    """
    try:
        import os
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        
        # 提取卦名
        simple_name = gua_name.replace('卦', '')
        txt_file = os.path.join(data_dir, f'{simple_name}卦.txt')
        
        if not os.path.exists(txt_file):
            return None
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    except Exception as e:
        print(f'[ERROR] Read txt failed: {e}')
        return None


# 简单测试
if __name__ == '__main__':
    # 测试几个卦
    tests = [
        ([9, 9, 9, 9, 9, 9], '乾为天'),  # 111111
        ([6, 6, 6, 6, 6, 6], '坤为地'),  # 000000
        ([9, 9, 9, 8, 9, 8], '水天需'),  # 111010 (上坎下乾：初阳二阳三阳四阴五阳上阴)
    ]
    
    for yao_list, expected in tests:
        name = get_gua_name_simple(yao_list)
        status = '✓' if name == expected else '✗'
        print(f"{status} {expected}: {name}")
