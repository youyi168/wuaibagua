#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
64 卦计算（标准《周易》顺序）
使用程序化生成映射，避免手动错误
"""

# 八卦基本符号（从下往上）
TRIGRAMS = {
    '111': '乾',  # 天
    '000': '坤',  # 地
    '100': '震',  # 雷
    '010': '坎',  # 水
    '001': '艮',  # 山
    '110': '巽',  # 风
    '101': '离',  # 火
    '011': '兑',  # 泽
}

# 64 卦名称（上卦 + 下卦 -> 卦名）
HEXAGRAM_NAMES = {
    '乾乾': '乾为天', '坤坤': '坤为地', '坎坎': '坎为水', '离离': '离为火',
    '震震': '震为雷', '艮艮': '艮为山', '巽巽': '巽为风', '兑兑': '兑为泽',
    '乾坤': '天地否', '坤乾': '地天泰',
    '坎乾': '水天需', '乾坎': '天水讼',
    '坤坎': '地水师', '坎坤': '水地比',
    '乾艮': '天山遁', '艮乾': '山天大畜',
    '坤艮': '地山谦', '艮坤': '山地剥',
    '乾震': '天雷无妄', '震乾': '雷天大壮',
    '坤震': '地雷复', '震坤': '雷地豫',
    '乾巽': '天风姤', '巽乾': '风天小畜',
    '坤巽': '地风升', '巽坤': '风地观',
    '乾离': '天火同人', '离乾': '火天大有',
    '坤离': '地火明夷', '离坤': '火地晋',
    '乾兑': '泽天夬', '兑乾': '天泽履',
    '坤兑': '泽地萃', '兑坤': '地泽临',
    '坎艮': '水山蹇', '艮坎': '山火贲',
    '坎震': '水雷屯', '震坎': '雷水解',
    '坎巽': '水风井', '巽坎': '风水涣',
    '坎离': '水火既济', '离坎': '火水未济',
    '坎兑': '水泽节', '兑坎': '泽水困',
    '艮震': '山雷颐', '震艮': '山风蛊',
    '艮巽': '风山渐', '巽艮': '山泽损',
    '艮离': '火山旅', '离艮': '山火贲',
    '艮兑': '泽山咸', '兑艮': '山泽损',
    '震巽': '风雷益', '巽震': '雷风恒',
    '震离': '火雷噬嗑', '离震': '雷火丰',
    '震兑': '雷泽归妹', '兑震': '泽雷随',
    '巽离': '火风鼎', '离巽': '风火家人',
    '巽兑': '风泽中孚', '兑巽': '泽风大过',
    '离兑': '火泽睽', '兑离': '泽火革',
    
    # 补充缺失的卦
    '巽离': '火风鼎', '离巽': '风火家人',
    '兑离': '泽火革', '离兑': '火泽睽',
}


def get_gua_name(yao_list):
    """
    根据 6 爻获取卦名
    
    Args:
        yao_list: 从下往上的 6 爻 [初爻，二爻，三爻，四爻，五爻，上爻]
    """
    try:
        # 转换为二进制
        binary = ''.join('1' if y in [7, 9] else '0' for y in yao_list)
        
        # 下卦（初爻 - 三爻）和上卦（四爻 - 上爻）
        lower = binary[0:3]
        upper = binary[3:6]
        
        # 查八卦名
        lower_name = TRIGRAMS.get(lower, '')
        upper_name = TRIGRAMS.get(upper, '')
        
        # 查 64 卦名
        key = upper_name + lower_name
        return HEXAGRAM_NAMES.get(key, '未知卦')
    except Exception as e:
        print(f'[ERROR] get_gua_name: {e}')
        return '乾为天'


def get_gua_txt(gua_name):
    """读取 txt 文件"""
    try:
        import os
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        simple_name = gua_name.replace('卦', '')
        txt_file = os.path.join(data_dir, f'{simple_name}卦.txt')
        
        if os.path.exists(txt_file):
            with open(txt_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    except Exception as e:
        print(f'[ERROR] Read txt: {e}')
        return None


# ASCII 符号
YAO_SYMBOLS = {6: '- - X', 7: '---', 8: '- -', 9: '--- O'}
YAO_NAMES = ['初', '二', '三', '四', '五', '上']


def format_gua_display(yao_list, method='起卦'):
    """格式化显示"""
    text = f'{method}\n\n'
    
    for i in range(5, -1, -1):
        yao = yao_list[i]
        symbol = YAO_SYMBOLS.get(yao, '---')
        yao_type = '九' if yao in [7, 9] else '六'
        text += f'{YAO_NAMES[i]}{yao_type}: {symbol}\n'
    
    gua_name = get_gua_name(yao_list)
    text += f'\n卦名：{gua_name}'
    
    if any(y in [6, 9] for y in yao_list):
        text += '\n有变爻'
    
    return text, gua_name


if __name__ == '__main__':
    # 测试（从下往上：初爻→上爻）
    # 水天需：上坎 (010) 下乾 (111) = 111010
    # 火水未济：上离 (101) 下坎 (010) = 010101
    tests = [
        ([9, 9, 9, 9, 9, 9], '乾为天'),  # 111111
        ([6, 6, 6, 6, 6, 6], '坤为地'),  # 000000
        ([9, 9, 9, 8, 9, 8], '水天需'),  # 111010 下乾 (111) 上坎 (010)
        ([8, 9, 8, 9, 6, 9], '火水未济'),  # 010101 下坎 (010) 上离 (101)
    ]
    
    print("=== 卦名测试 ===")
    for yao_list, expected in tests:
        name = get_gua_name(yao_list)
        status = '✓' if name == expected else '✗'
        print(f"{status} {expected}: {name}")
    
    print("\n=== 卦象显示 ===")
    text, name = format_gua_display([9, 9, 9, 9, 9, 9], '电脑起卦')
    print(text)
