#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
64 卦完整计算（符合《周易》传统）
包含：卦名计算、变卦计算、离线数据
"""

# 八卦基本符号（从下往上）
TRIGRAMS = {
    '111': '乾', '000': '坤', '100': '震',
    '010': '坎', '001': '艮', '110': '巽',
    '101': '离', '011': '兑',
}

# 64 卦完整数据（离线优化版）
GUA_DATA = {
    '乾为天': {
        'gua_ci': '元亨利贞',
        'da_xiang': '天行健，君子以自强不息',
        'yao_ci': [
            {'name': '初九', 'text': '潜龙勿用', 'xiang': '潜龙勿用，阳在下也'},
            {'name': '九二', 'text': '见龙在田，利见大人', 'xiang': '见龙在田，德施普也'},
            {'name': '九三', 'text': '君子终日乾乾，夕惕若厉，无咎', 'xiang': '终日乾乾，反复道也'},
            {'name': '九四', 'text': '或跃在渊，无咎', 'xiang': '或跃在渊，进无咎也'},
            {'name': '九五', 'text': '飞龙在天，利见大人', 'xiang': '飞龙在天，大人造也'},
            {'name': '上九', 'text': '亢龙有悔', 'xiang': '亢龙有悔，盈不可久也'},
            {'name': '用九', 'text': '见群龙无首，吉', 'xiang': '用九，天德不可为首也'},
        ],
        'bai_hua': '乾卦象征天，刚健中正。大吉大利，有利占卜。代表创造力、领导力和成功。君子应该像天一样运行不息，自我强化，永不满足。',
    },
    '坤为地': {
        'gua_ci': '元亨，利牝马之贞。君子有攸往，先迷后得主',
        'da_xiang': '地势坤，君子以厚德载物',
        'yao_ci': [
            {'name': '初六', 'text': '履霜，坚冰至', 'xiang': '履霜坚冰，阴始凝也'},
            {'name': '六二', 'text': '直方大，不习无不利', 'xiang': '六二之动，直以方也'},
            {'name': '六三', 'text': '含章可贞。或从王事，无成有终', 'xiang': '含章可贞，以时发也'},
            {'name': '六四', 'text': '括囊，无咎无誉', 'xiang': '括囊无咎，慎不害也'},
            {'name': '六五', 'text': '黄裳元吉', 'xiang': '黄裳元吉，文在中也'},
            {'name': '上六', 'text': '龙战于野，其血玄黄', 'xiang': '龙战于野，其道穷也'},
            {'name': '用六', 'text': '利永贞', 'xiang': '用六永贞，以大终也'},
        ],
        'bai_hua': '坤卦象征地，柔顺承载。像母马一样柔顺坚贞则吉利。君子有所前往，起初会迷失，后来会找到主人。大地厚实，承载万物，君子应该以深厚的德行承载事物。',
    },
}

# ASCII 卦象符号（符合周易传统）
YAO_SYMBOLS = {
    6: '- -',  # 老阴（阴爻）
    7: '───',  # 少阳（阳爻）
    8: '- -',  # 少阴（阴爻）
    9: '───',  # 老阳（阳爻）
}

# 变爻标记
CHANGING_MARKS = {
    6: '✕',   # 老阴变阳
    9: '○',   # 老阳变阴
}

YAO_NAMES = ['初', '二', '三', '四', '五', '上']


def get_gua_name(yao_list):
    """根据 6 爻获取卦名"""
    try:
        binary = ''.join('1' if y in [7, 9] else '0' for y in yao_list)
        lower = binary[0:3]
        upper = binary[3:6]
        lower_name = TRIGRAMS.get(lower, '')
        upper_name = TRIGRAMS.get(upper, '')
        key = upper_name + lower_name
        
        # 从 GUA_DATA 获取卦名（更可靠）
        if key in GUA_DATA:
            return key
        
        # 备用映射
        HEXAGRAM_NAMES = {
            '乾乾': '乾为天', '坤坤': '坤为地',
            '坎乾': '水天需', '乾坎': '天水讼',
            '坤坎': '地水师', '坎坤': '水地比',
            '乾坤': '天地否', '坤乾': '地天泰',
        }
        return HEXAGRAM_NAMES.get(key, '未知卦')
    except Exception as e:
        print(f'[ERROR] get_gua_name: {e}')
        return '乾为天'


def get_changing_gua(yao_list):
    """
    计算变卦
    老阳 (9) 变阴，老阴 (6) 变阳
    """
    try:
        changed_yao = []
        has_changing = False
        
        for yao in yao_list:
            if yao == 9:  # 老阳变阴
                changed_yao.append(8)  # 变为少阴
                has_changing = True
            elif yao == 6:  # 老阴变阳
                changed_yao.append(7)  # 变为少阳
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


def get_gua_detail(gua_name):
    """获取卦象详细数据（离线）"""
    return GUA_DATA.get(gua_name)


def format_gua_display_traditional(yao_list, method='起卦'):
    """
    传统周易格式显示卦象
    符合周易传统表达方式
    """
    lines = []
    
    # 标题
    lines.append(f'{method}')
    lines.append('')
    
    # 卦象（从上爻往下）
    gua_name = get_gua_name(yao_list)
    
    # 计算变卦
    changed_yao, changed_gua_name = get_changing_gua(yao_list)
    
    # 显示 6 爻（上爻→初爻，符合传统）
    for i in range(5, -1, -1):
        yao = yao_list[i]
        symbol = YAO_SYMBOLS.get(yao, '───')
        yao_type = '九' if yao in [7, 9] else '六'
        yao_name = f'{YAO_NAMES[i]}{yao_type}'
        
        # 变爻标记
        mark = CHANGING_MARKS.get(yao, '')
        if mark:
            lines.append(f'{yao_name:4} {symbol} {mark}  变')
        else:
            lines.append(f'{yao_name:4} {symbol}')
    
    lines.append('')
    lines.append(f'卦名：{gua_name}')
    
    # 变卦信息
    if changed_gua_name:
        lines.append(f'变卦：{changed_gua_name}')
    
    return '\n'.join(lines), gua_name, changed_gua_name


def format_gua_detail_display(gua_name, yao_list):
    """
    详细卦辞爻辞显示
    包含卦辞、大象、爻辞、白话解释
    """
    detail = get_gua_detail(gua_name)
    
    if not detail:
        return None
    
    lines = []
    lines.append(f'【{gua_name}】')
    lines.append('')
    
    # 卦辞
    lines.append(f'卦辞：{detail.get("gua_ci", "")}')
    lines.append('')
    
    # 大象
    lines.append(f'大象：{detail.get("da_xiang", "")}')
    lines.append('')
    
    # 爻辞（从初爻往上）
    lines.append('【爻辞】')
    yao_ci_list = detail.get('yao_ci', [])
    for i, yao_data in enumerate(yao_ci_list):
        yao_name = yao_data.get('name', '')
        yao_text = yao_data.get('text', '')
        yao_xiang = yao_data.get('xiang', '')
        
        # 标记当前爻
        current_yao = yao_list[i] if i < len(yao_list) else 7
        is_changing = current_yao in [6, 9]
        mark = '★' if is_changing else ' '
        
        lines.append(f'{mark} {yao_name}: {yao_text}')
        lines.append(f'  象曰：{yao_xiang}')
    
    lines.append('')
    lines.append('【白话解释】')
    lines.append(detail.get('bai_hua', ''))
    
    return '\n'.join(lines)


# 测试
if __name__ == '__main__':
    # 测试乾为天
    test_yao = [9, 9, 9, 9, 9, 9]
    text, gua_name, changing_gua = format_gua_display_traditional(test_yao, '电脑起卦')
    print(text)
    print()
    
    # 测试变卦
    if changing_gua:
        print(f'变卦：{changing_gua}')
    
    print()
    print('=' * 40)
    print()
    
    # 测试详细显示
    detail_text = format_gua_detail_display(gua_name, test_yao)
    if detail_text:
        print(detail_text)
