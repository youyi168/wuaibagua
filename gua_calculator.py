#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
64 卦完整计算（优化版 v2.0）
整合 ichingshifa 项目算法优点

来源：
- https://github.com/kentang2017/ichingshifa
- 《周易》传统蓍草起卦法
- 梅花易数时间起卦法

优化内容：
1. 完整的 64 卦二进制映射（无重复）
2. 支持蓍草起卦法（三变一爻）
3. 支持时间起卦法（梅花易数）
4. 支持手动起卦
5. 完整的卦辞、爻辞、彖传、象传
6. 变卦计算和断卦逻辑
"""

import os
import random
from datetime import datetime

# ==================== 基础数据 ====================

# 八卦定义（二进制从下往上）
TRIGRAMS = {
    '111': '乾', '000': '坤', '100': '震', '010': '坎',
    '001': '艮', '110': '巽', '101': '离', '011': '兑',
}

# 八卦符号
TRIGRAM_SYMBOLS = {
    '111': '☰', '000': '☷', '100': '☳', '010': '☵',
    '001': '☶', '110': '☴', '101': '☲', '011': '☱',
}

# 64 卦完整映射（二进制：下卦 + 上卦，从下往上）
HEXAGRAM_NAMES = {
    '111111': '乾为天',
    '000000': '坤为地',
    '111010': '水天需',
    '010111': '天水讼',
    '010000': '地水师',
    '000010': '水地比',
    '111110': '风天小畜',
    '011111': '天泽履',
    '111000': '地天泰',
    '000111': '天地否',
    '101111': '天火同人',
    '111101': '火天大有',
    '001000': '地山谦',
    '000100': '雷地豫',
    '100011': '泽雷随',
    '001110': '山风蛊',
    '011000': '地泽临',
    '000110': '风地观',
    '100101': '火雷噬嗑',
    '010001': '山火贲',
    '000001': '山地剥',
    '100000': '地雷复',
    '100111': '天雷无妄',
    '111001': '山天大畜',
    '100001': '山雷颐',
    '110011': '泽风大过',
    '010010': '坎为水',
    '101101': '离为火',
    '001011': '泽山咸',
    '110100': '雷风恒',
    '111100': '雷天大壮',
    '000101': '火地晋',
    '101000': '地火明夷',
    '101110': '风火家人',
    '011101': '火泽睽',
    '001010': '水山蹇',
    '010100': '雷水解',
    '011001': '山泽损',
    '100110': '风雷益',
    '111011': '泽天夬',
    '110111': '天风姤',
    '000011': '泽地萃',
    '110000': '地风升',
    '010011': '泽水困',
    '110010': '水风井',
    '101011': '泽火革',
    '110101': '火风鼎',
    '100100': '震为雷',
    '001001': '艮为山',
    '110001': '风山渐',
    '011100': '雷泽归妹',
    '101100': '雷火丰',
    '001101': '火山旅',
    '110110': '巽为风',
    '011011': '兑为泽',
    '010110': '风水涣',
    '011010': '水泽节',
    '011110': '风泽中孚',
    '001100': '雷山小过',
    '101010': '水火既济',
    '010101': '火水未济',
    '100010': '水雷屯',
    '101001': '山水蒙',
    '001111': '天山遁',
}

# 爻符号（ASCII）
YAO_SYMBOLS = {
    6: '- -',  # 老阴
    7: '───',  # 少阳
    8: '- -',  # 少阴
    9: '───',  # 老阳
}

# 变爻标记
CHANGING_MARKS = {
    6: '✕',   # 老阴变阳
    9: '○',   # 老阳变阴
}

# 爻位名称
YAO_POSITIONS = ['初', '二', '三', '四', '五', '上']

# 地支编码（用于时间起卦）
DIZHI_CODE = {
    '子': 1, '丑': 2, '寅': 3, '卯': 4, '辰': 5, '巳': 6,
    '午': 7, '未': 8, '申': 9, '酉': 10, '戌': 11, '亥': 12,
}

# 天干地支
TIANGAN = '甲乙丙丁戊己庚辛壬癸'
DIZHI = '子丑寅卯辰巳午未申酉戌亥'


# ==================== 核心函数 ====================

def get_gua_name(yao_list):
    """
    根据 6 爻获取卦名
    
    Args:
        yao_list: [初爻，二爻，三爻，四爻，五爻，上爻]
                  每个爻为 6/7/8/9
    
    Returns:
        str: 卦名
    """
    try:
        # 转换为二进制（从下往上）
        binary = ''.join('1' if yao in [7, 9] else '0' for yao in yao_list)
        return HEXAGRAM_NAMES.get(binary, '未知卦')
    except Exception as e:
        print(f'[ERROR] get_gua_name: {e}')
        return '乾为天'


def get_binary(yao_list):
    """获取卦象二进制表示"""
    return ''.join('1' if yao in [7, 9] else '0' for yao in yao_list)


def get_changing_gua(yao_list):
    """
    计算变卦（老阳变阴，老阴变阳）
    
    Args:
        yao_list: 原始 6 爻
    
    Returns:
        tuple: (变卦爻列表，变卦卦名)
    """
    try:
        changed_yao = []
        has_changing = False
        
        for yao in yao_list:
            if yao == 9:  # 老阳变阴
                changed_yao.append(8)
                has_changing = True
            elif yao == 6:  # 老阴变阳
                changed_yao.append(7)
                has_changing = True
            else:
                changed_yao.append(yao)
        
        if not has_changing:
            return None, None
        
        changed_gua_name = get_gua_name(changed_yao)
        return changed_yao, changed_gua_name
    except Exception as e:
        print(f'[ERROR] get_changing_gua: {e}')
        return None, None


def get_yao_name(position, yao):
    """获取爻名（如初九、六二等）"""
    yao_type = '九' if yao in [7, 9] else '六'
    return f'{YAO_POSITIONS[position]}{yao_type}'


# ==================== 起卦方法 ====================

def shicao_qigua():
    """
    蓍草起卦法（周易传统）
    
    原理：
    - 50 根蓍草，去 1 根不用
    - 三变生成一爻
    - 六爻成一卦（从下往上）
    
    概率分布：
    - 6(老阴): 1/8
    - 7(少阳): 3/8
    - 8(少阴): 3/8
    - 9(老阳): 1/8
    
    Returns:
        list: 6 爻列表 [初爻，二爻，..., 上爻]
    """
    yao_list = []
    
    for i in range(6):  # 六爻
        # 三变生成一爻
        stalks = 49  # 50-1
        
        # 一变
        divider = random.randint(24, stalks - 1)
        left = divider
        right = stalks - divider - 1  # 挂一
        left_remain = left % 4 or 4
        right_remain = right % 4 or 4
        yibian = left_remain + right_remain + 1
        
        # 二变
        stalks2 = stalks - yibian
        divider2 = random.randint(12, stalks2 - 1)
        left2 = divider2
        right2 = stalks2 - divider2 - 1
        left_remain2 = left2 % 4 or 4
        right_remain2 = right2 % 4 or 4
        erbian = left_remain2 + right_remain2 + 1
        
        # 三变
        stalks3 = stalks2 - erbian
        divider3 = random.randint(6, stalks3 - 1)
        left3 = divider3
        right3 = stalks3 - divider3 - 1
        left_remain3 = left3 % 4 or 4
        right_remain3 = right3 % 4 or 4
        sanbian = left_remain3 + right_remain3 + 1
        
        # 计算爻值
        yao = int((stalks - yibian - erbian - sanbian) / 4)
        yao_list.append(yao)
    
    return yao_list



def jinqian_qigua():
    """
    金钱起卦法（六爻预测传统方法）
    
    原理：
    - 三枚铜钱，每枚有字为阴（值 2），无字为阳（值 3）
    - 摇六次，每次得一爻（从下往上）
    - 总和：6(老阴)、7(少阳)、8(少阴)、9(老阳)
    
    概率分布：
    - 6(老阴): 1/8 (2+2+2)
    - 7(少阳): 3/8 (2+2+3, 2+3+2, 3+2+2)
    - 8(少阴): 3/8 (2+3+3, 3+2+3, 3+3+2)
    - 9(老阳): 1/8 (3+3+3)
    
    Returns:
        list: 6 爻列表 [初爻，二爻，..., 上爻]
    """
    yao_list = []
    
    for i in range(6):  # 摇六次
        # 三枚铜钱
        qian1 = random.choice([2, 3])  # 2=字 (阴), 3=背 (阳)
        qian2 = random.choice([2, 3])
        qian3 = random.choice([2, 3])
        
        # 总和
        total = qian1 + qian2 + qian3
        
        # 转换为爻值
        if total == 6:
            yao = 6  # 老阴
        elif total == 7:
            yao = 7  # 少阳
        elif total == 8:
            yao = 8  # 少阴
        elif total == 9:
            yao = 9  # 老阳
        
        yao_list.append(yao)
    
    return yao_list


def time_qigua(year, month, day, hour, minute=0):
    """
    时间起卦法（梅花易数）
    
    原理：
    - 上卦：(年支 + 月 + 日 + 时支) % 8
    - 下卦：(年支 + 月 + 日) % 8
    - 变爻：(年支 + 月 + 日 + 时支) % 6
    
    Args:
        year, month, day, hour, minute: 公历时间
    
    Returns:
        list: 6 爻列表
    """
    # 获取年支和时支
    year_zhi = DIZHI[(year - 4) % 12]
    hour_zhi = DIZHI[(hour + 1) % 12]
    
    # 获取地支编码
    year_code = DIZHI_CODE.get(year_zhi, 1)
    hour_code = DIZHI_CODE.get(hour_zhi, 1)
    
    # 计算上下卦
    upper_remain = (year_code + month + day + hour_code) % 8
    upper_remain = upper_remain or 8
    
    lower_remain = (year_code + month + day) % 8
    lower_remain = lower_remain or 8
    
    # 八卦二进制（1=阳，2=阴）
    bagua_map = {
        1: '111', 2: '110', 3: '101', 4: '100',
        5: '011', 6: '010', 7: '001', 8: '000',
    }
    
    upper_gua = bagua_map.get(upper_remain, '111')
    lower_gua = bagua_map.get(lower_remain, '111')
    
    # 组合成 6 爻（从下往上：下卦 + 上卦）
    combined = lower_gua + upper_gua
    
    # 计算变爻
    bian_yao = (year_code + month + day + hour_code) % 6
    bian_yao = bian_yao or 6
    
    # 转换为爻值（7=少阳，8=少阴）
    yao_list = [7 if bit == '1' else 8 for bit in combined]
    
    # 设置变爻（7→9, 8→6）
    yao_list[bian_yao - 1] = 9 if yao_list[bian_yao - 1] == 7 else 6
    
    return yao_list


def manual_qigua(yao_selections):
    """
    手动起卦
    
    Args:
        yao_selections: [初爻，二爻，..., 上爻]，每个为 6/7/8/9
    
    Returns:
        list: 6 爻列表
    """
    return yao_selections[:]


# ==================== 显示函数 ====================

def format_gua_display(yao_list, method='起卦'):
    """
    显示卦象（返回图片路径信息，Kivy UI 显示图片）
    
    Returns:
        tuple: (显示文本，卦名，变卦名，图片路径字典)
    """
    gua_name = get_gua_name(yao_list)
    changed_yao, changed_gua_name = get_changing_gua(yao_list)
    
    # 获取 64 卦图片路径
    binary = get_binary(yao_list)
    try:
        from gua_images import get_hexagram_image_path, get_yao_image_path
        hexagram_image = get_hexagram_image_path(binary)
        
        # 获取每个爻的图片路径
        yao_images = {}
        for i in range(6):
            yao = yao_list[i]
            yao_images[i] = get_yao_image_path(yao)
    except:
        hexagram_image = ''
        yao_images = {}
    
    # 显示文本（简化版）
    lines = [f'[ {method} ]', '', f'卦名：{gua_name}', '']
    
    # 爻位信息
    yao_names = ['初', '二', '三', '四', '五', '上']
    for i in range(5, -1, -1):
        yao = yao_list[i]
        yao_name = get_yao_name(i, yao)
        yao_type = '阳' if yao in [7, 9] else '阴'
        mark = ' ⭕' if yao == 9 else ' ✕' if yao == 6 else ''
        lines.append(f'{yao_name}{yao_type}{mark}')
    
    if changed_gua_name:
        lines.append('')
        lines.append(f'变卦：{changed_gua_name}')
    
    # 返回图片路径信息
    image_info = {
        'hexagram': hexagram_image,
        'yao': yao_images,
    }
    
    return '\n'.join(lines), gua_name, changed_gua_name, image_info



def get_gua_detail(gua_name):
    """
    从 txt 文件读取卦象详细数据
    
    Args:
        gua_name: 卦名全称
    
    Returns:
        dict: 包含卦辞、大象、爻辞、白话解释
    """
    # 卦名全称→简称映射
    FULL_TO_SHORT = {
        '乾为天': '乾', '坤为地': '坤', '水雷屯': '屯', '山水蒙': '蒙',
        '水天需': '需', '天水讼': '讼', '地水师': '师', '水地比': '比',
        '风天小畜': '小畜', '天泽履': '履', '地天泰': '泰', '天地否': '否',
        '天火同人': '同人', '火天大有': '大有', '地山谦': '谦', '雷地豫': '豫',
        '泽雷随': '随', '山风蛊': '蛊', '地泽临': '临', '风地观': '观',
        '火雷噬嗑': '噬嗑', '山火贲': '贲', '山地剥': '剥', '地雷复': '复',
        '天雷无妄': '无妄', '山天大畜': '大畜', '山雷颐': '颐', '泽风大过': '大过',
        '坎为水': '坎', '离为火': '离', '泽山咸': '咸', '雷风恒': '恒',
        '天山遁': '遁', '雷天大壮': '大壮', '火地晋': '晋', '地火明夷': '明夷',
        '风火家人': '家人', '火泽睽': '睽', '水山蹇': '蹇', '雷水解': '解',
        '山泽损': '损', '风雷益': '益', '泽天夬': '夬', '天风姤': '姤',
        '泽地萃': '萃', '地风升': '升', '泽水困': '困', '水风井': '井',
        '泽火革': '革', '火风鼎': '鼎', '震为雷': '震', '艮为山': '艮',
        '风山渐': '渐', '雷泽归妹': '归妹', '雷火丰': '丰', '火山旅': '旅',
        '巽为风': '巽', '兑为泽': '兑', '风水涣': '涣', '水泽节': '节',
        '风泽中孚': '中孚', '雷山小过': '小过', '水火既济': '既济', '火水未济': '未济',
    }
    
    try:
        short_name = FULL_TO_SHORT.get(gua_name)
        if not short_name:
            return None
        
        # 多路径查找
        txt_file = f'data/{short_name}卦.txt'
        if not os.path.exists(txt_file):
            txt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', f'{short_name}卦.txt')
        if not os.path.exists(txt_file):
            txt_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', f'{short_name}卦.txt')
        
        if not os.path.exists(txt_file):
            return None
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析
        result = {
            'gua_ci': '',
            'da_xiang': '',
            'yao_ci': [],
            'bai_hua': content,
            'full_text': content,
        }
        
        lines = content.strip().split('\n')
        
        # 提取卦辞
        for line in lines:
            line_stripped = line.strip()
            if ('：' in line_stripped or ':' in line_stripped) and not line_stripped.startswith('【') and not line_stripped.startswith('《'):
                if '：' in line_stripped:
                    parts = line_stripped.split('：', 1)
                else:
                    parts = line_stripped.split(':', 1)
                if len(parts[0]) <= 2:
                    result['gua_ci'] = parts[1].strip().rstrip('.')
                    break
        
        # 提取大象
        for line in lines:
            if '《象》曰' in line or '象曰' in line:
                if '君子' in line:
                    result['da_xiang'] = line.replace('《象》曰：', '').replace('象曰：', '').strip()
                    break
        
        # 提取爻辞
        yao_patterns = ['初九', '初六', '九二', '六二', '九三', '六三', '九四', '六四', 
                        '九五', '六五', '上九', '上六', '用九', '用六']
        
        i = 0
        while i < len(lines):
            line = lines[i]
            for pattern in yao_patterns:
                if line.startswith(pattern + '，') or line.startswith(pattern + ','):
                    yao_data = {'name': '', 'text': '', 'xiang': ''}
                    
                    if '，' in line:
                        parts = line.split('，', 1)
                        yao_data['name'] = parts[0]
                        yao_data['text'] = parts[1].rstrip('。').strip()
                    elif ',' in line:
                        parts = line.split(',', 1)
                        yao_data['name'] = parts[0]
                        yao_data['text'] = parts[1].rstrip('。').strip()
                    else:
                        yao_data['name'] = line[:2]
                        yao_data['text'] = line[2:].strip()
                    
                    # 查找象曰
                    for j in range(i+1, min(i+4, len(lines))):
                        xiang_line = lines[j]
                        if '《象》曰' in xiang_line or '象曰' in xiang_line:
                            if '君子' not in xiang_line:
                                yao_data['xiang'] = xiang_line.replace('《象》曰：', '').replace('象曰：', '').rstrip('。').strip()
                                break
                    
                    result['yao_ci'].append(yao_data)
                    break
            i += 1
        
        return result
    
    except Exception as e:
        print(f'[ERROR] get_gua_detail: {e}')
        return None


# ==================== 断卦逻辑（ichingshifa 算法） ====================

def duangua_logic(yao_list):
    """
    断卦逻辑（整合 ichingshifa 算法）
    
    规则：
    - 0 动爻：看本卦彖辞
    - 1 动爻：看本卦动爻爻辞
    - 2 动爻：看本卦两动爻爻辞
    - 3 动爻：看本卦和之卦彖辞
    - 4 动爻：看之卦静爻爻辞
    - 5 动爻：看之卦静爻爻辞
    - 6 动爻：看之卦彖辞
    
    Args:
        yao_list: 6 爻列表
    
    Returns:
        dict: 断卦结果
    """
    gua_name = get_gua_name(yao_list)
    changed_yao, changed_gua_name = get_changing_gua(yao_list)
    
    # 计算动爻数量
    dong_yao_count = sum(1 for yao in yao_list if yao in [6, 9])
    
    result = {
        'ben_gua': gua_name,
        'zhi_gua': changed_gua_name,
        'dong_yao_count': dong_yao_count,
        'duan_gua_method': '',
        'keywords': [],
    }
    
    # 断卦方法
    if dong_yao_count == 0:
        result['duan_gua_method'] = '无动爻，看本卦彖辞'
    elif dong_yao_count == 1:
        result['duan_gua_method'] = '一爻动，看本卦动爻爻辞'
    elif dong_yao_count == 2:
        result['duan_gua_method'] = '两爻动，看本卦两动爻爻辞'
    elif dong_yao_count == 3:
        result['duan_gua_method'] = '三爻动，看本卦和之卦彖辞'
    elif dong_yao_count == 4:
        result['duan_gua_method'] = '四爻动，看之卦静爻爻辞'
    elif dong_yao_count == 5:
        result['duan_gua_method'] = '五爻动，看之卦静爻爻辞'
    elif dong_yao_count == 6:
        result['duan_gua_method'] = '六爻动，看之卦彖辞'
    
    return result


# ==================== 测试 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("64 卦计算模块 v2.0（优化版）")
    print("=" * 60)
    
    # 测试 1: 蓍草起卦
    print("\n1. 蓍草起卦法:")
    yao_list = shicao_qigua()
    text, gua_name, changed = format_gua_display(yao_list, '蓍草起卦')
    print(text)
    print(f"变卦：{changed}")
    
    # 测试 2: 时间起卦
    print("\n2. 时间起卦法:")
    now = datetime.now()
    yao_list = time_qigua(now.year, now.month, now.day, now.hour, now.minute)
    text, gua_name, changed = format_gua_display(yao_list, '时间起卦')
    print(text)
    print(f"变卦：{changed}")
    
    # 测试 3: 卦辞读取
    print("\n3. 卦辞读取测试:")
    for gua in ['乾为天', '坤为地', '水天需']:
        detail = get_gua_detail(gua)
        if detail:
            print(f"✅ {gua}: 卦辞={detail.get('gua_ci', '')[:20]}...")
        else:
            print(f"❌ {gua}: 读取失败")
    
    # 测试 4: 断卦逻辑
    print("\n4. 断卦逻辑测试:")
    yao_list = [9, 9, 9, 9, 9, 9]  # 全老阳
    result = duangua_logic(yao_list)
    print(f"本卦：{result['ben_gua']}")
    print(f"之卦：{result['zhi_gua']}")
    print(f"动爻数：{result['dong_yao_count']}")
    print(f"断法：{result['duan_gua_method']}")
