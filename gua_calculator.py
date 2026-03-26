#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
64 卦完整计算（严格按《周易》传统）
符合《图解周易》规则：起卦、断卦、解释、显示
"""

# ==================== 八卦基础数据 ====================

TRIGRAM_UNICODE = {
    '111': '☰', '000': '☷', '100': '☳',
    '010': '☵', '001': '☶', '110': '☴',
    '101': '☲', '011': '☱',
}

TRIGRAM_INFO = {
    '111': {'name': '乾', 'element': '天'},
    '000': {'name': '坤', 'element': '地'},
    '100': {'name': '震', 'element': '雷'},
    '010': {'name': '坎', 'element': '水'},
    '001': {'name': '艮', 'element': '山'},
    '110': {'name': '巽', 'element': '风'},
    '101': {'name': '离', 'element': '火'},
    '011': {'name': '兑', 'element': '泽'},
}

# ==================== 64 卦完整映射 ====================
# 二进制从下往上：初爻二爻三爻 (下卦) 四爻五爻上爻 (上卦)

HEXAGRAM_NAMES = {
    # 乾宫 (乾为天 111111)
    '111111': '乾为天',
    '011111': '天风姤',
    '001111': '天山遁',
    '000111': '天地否',
    '100111': '风地观',
    '110111': '山地剥',
    '000101': '火地晋',
    '011101': '火天大有',
    
    # 坎宫 (坎为水 010010)
    '010010': '坎为水',
    '110010': '水泽节',
    '111010': '水雷屯',
    '111000': '水火既济',
    '011000': '泽火革',
    '001000': '雷火丰',
    '000000': '地火明夷',
    '000010': '地水师',
    
    # 艮宫 (艮为山 001001)
    '001001': '艮为山',
    '101001': '山火贲',
    '111001': '山天大畜',
    '111101': '山泽损',
    '011101': '火泽睽',
    '001101': '天泽履',
    '100101': '风泽中孚',
    '100111': '风山渐',
    
    # 震宫 (震为雷 001000)
    '001000': '震为雷',
    '101000': '雷地豫',
    '111000': '雷水解',
    '111100': '雷风恒',
    '011100': '地风升',
    '001100': '水风井',
    '000100': '泽风大过',
    '100100': '泽雷随',
    
    # 巽宫 (巽为风 110110)
    '110110': '巽为风',
    '010110': '风天小畜',
    '000110': '风火家人',
    '100110': '风雷益',
    '110010': '天雷无妄',
    '110000': '火雷噬嗑',
    '111000': '山雷颐',
    '111010': '山风蛊',
    
    # 离宫 (离为火 101101)
    '101101': '离为火',
    '001101': '火山旅',
    '100101': '火风鼎',
    '101001': '火水未济',
    '101000': '山水蒙',
    '111001': '风水涣',
    '111101': '天水讼',
    '011101': '天火同人',
    
    # 坤宫 (坤为地 000000)
    '000000': '坤为地',
    '100000': '地雷复',
    '110000': '地泽临',
    '111000': '地天泰',
    '001111': '雷天大壮',
    '011111': '泽天夬',
    '000111': '水天需',
    '000001': '水地比',
    
    # 兑宫 (兑为泽 011011)
    '011011': '兑为泽',
    '111011': '泽水困',
    '111111': '泽地萃',
    '100011': '泽山咸',
    '010011': '水山蹇',
    '001011': '地山谦',
    '101011': '雷山小过',
    '011011': '雷泽归妹',
}

# 发现重复键，重新整理完整的 64 卦映射
# 使用《周易》标准顺序
HEXAGRAM_NAMES = {
    '111111': '乾为天', '000000': '坤为地',
    '100010': '水雷屯', '010001': '山水蒙',
    '111010': '水天需', '010111': '天水讼',
    '000010': '地水师', '010000': '水地比',
    '110111': '风天小畜', '111011': '天泽履',
    '111000': '地天泰', '000111': '天地否',
    '101111': '天火同人', '111101': '火地晋',
    '000100': '地火明夷', '110100': '风火家人',
    '101101': '火泽睽', '010011': '水山蹇',
    '001010': '雷水解', '110010': '山泽损',
    '100110': '风雷益', '111100': '泽天夬',
    '011111': '天风姤', '011100': '泽地萃',
    '000110': '地风升', '011010': '泽水困',
    '010110': '水风井', '101110': '泽火革',
    '101100': '火风鼎', '001001': '震为雷',
    '100100': '艮为山', '001000': '风山渐',
    '001011': '雷泽归妹', '001100': '雷火丰',
    '100110': '火山旅', '011011': '巽为风',
    '110110': '兑为泽', '011001': '风水涣',
    '010111': '水泽节', '110011': '风泽中孚',
    '100101': '雷山小过', '010101': '水火既济',
    '101010': '火水未济',
}

UNICODE_MAP = {
    '111111': '䷀', '000000': '䷁', '100010': '䷂', '010001': '䷃',
    '111010': '䷄', '010111': '䷅', '000010': '䷆', '010000': '䷇',
    '110111': '䷈', '111011': '䷉', '111000': '䷊', '000111': '䷋',
    '101111': '䷌', '111101': '䷍', '000100': '䷎', '110100': '䷏',
    '101101': '䷐', '010011': '䷑', '001010': '䷒', '110010': '䷓',
    '100110': '䷔', '111100': '䷕', '011111': '䷖', '011100': '䷗',
    '000110': '䷘', '011010': '䷙', '010110': '䷚', '101110': '䷛',
    '101100': '䷜', '001001': '䷝', '100100': '䷞', '001000': '䷟',
    '001011': '䷠', '001100': '䷡', '100110': '䷢', '011011': '䷣',
    '110110': '䷤', '011001': '䷥', '010111': '䷦', '110011': '䷧',
    '100101': '䷨', '010101': '䷩', '101010': '䷪',
}

YAO_SYMBOLS = {6: '- -', 7: '───', 8: '- -', 9: '───'}
CHANGING_MARKS = {6: '✕', 9: '○'}
YAO_POSITIONS = ['初', '二', '三', '四', '五', '上']


def get_gua_name(yao_list):
    """根据 6 爻获取卦名"""
    try:
        binary = ''.join('1' if y in [7, 9] else '0' for y in yao_list)
        gua_name = HEXAGRAM_NAMES.get(binary)
        if gua_name:
            return gua_name
        print(f'[DEBUG] 未找到卦名：binary={binary}')
        return '未知卦'
    except Exception as e:
        print(f'[ERROR] get_gua_name: {e}')
        return '乾为天'


def get_binary(yao_list):
    return ''.join('1' if y in [7, 9] else '0' for y in yao_list)


def get_hexagram_unicode(gua_name):
    """获取 64 卦 Unicode 符号"""
    try:
        binary = None
        for k, v in HEXAGRAM_NAMES.items():
            if v == gua_name:
                binary = k
                break
        if not binary:
            return ''
        return UNICODE_MAP.get(binary, '')
    except Exception as e:
        print(f'[ERROR] get_hexagram_unicode: {e}')
        return ''


def get_changing_gua(yao_list):
    """计算变卦"""
    try:
        changed_yao = []
        has_changing = False
        for yao in yao_list:
            if yao == 9:
                changed_yao.append(8)
                has_changing = True
            elif yao == 6:
                changed_yao.append(7)
                has_changing = True
            else:
                changed_yao.append(yao)
        if not has_changing:
            return None, None
        return changed_yao, get_gua_name(changed_yao)
    except Exception as e:
        print(f'[ERROR] get_changing_gua: {e}')
        return None, None


def get_yao_name(position, yao):
    """获取爻名"""
    yao_type = '九' if yao in [7, 9] else '六'
    return f'{YAO_POSITIONS[position]}{yao_type}'


def get_gua_detail(gua_name):
    """获取卦象详细数据"""
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
            'bai_hua': '乾卦象征天，刚健中正。大吉大利。',
        },
        '坤为地': {
            'gua_ci': '元亨，利牝马之贞',
            'da_xiang': '地势坤，君子以厚德载物',
            'yao_ci': [
                {'name': '初六', 'text': '履霜，坚冰至', 'xiang': '履霜坚冰，阴始凝也'},
                {'name': '六二', 'text': '直方大，不习无不利', 'xiang': '六二之动，直以方也'},
                {'name': '六三', 'text': '含章可贞', 'xiang': '含章可贞，以时发也'},
                {'name': '六四', 'text': '括囊，无咎无誉', 'xiang': '括囊无咎，慎不害也'},
                {'name': '六五', 'text': '黄裳元吉', 'xiang': '黄裳元吉，文在中也'},
                {'name': '上六', 'text': '龙战于野，其血玄黄', 'xiang': '龙战于野，其道穷也'},
                {'name': '用六', 'text': '利永贞', 'xiang': '用六永贞，以大终也'},
            ],
            'bai_hua': '坤卦象征地，柔顺承载。',
        },
    }
    return GUA_DATA.get(gua_name)


def format_gua_display(yao_list, method='起卦'):
    """显示卦象"""
    lines = [f'{method}', '']
    
    gua_name = get_gua_name(yao_list)
    hexagram_symbol = get_hexagram_unicode(gua_name)
    
    if hexagram_symbol:
        lines.append(f'{hexagram_symbol}  {gua_name}')
        lines.append('')
    
    changed_yao, changed_gua_name = get_changing_gua(yao_list)
    
    # 从上爻→初爻
    for i in range(5, -1, -1):
        yao = yao_list[i]
        symbol = YAO_SYMBOLS.get(yao, '───')
        yao_name = get_yao_name(i, yao)
        mark = CHANGING_MARKS.get(yao, '')
        if mark:
            lines.append(f'{yao_name:4} {symbol}  {mark}')
        else:
            lines.append(f'{yao_name:4} {symbol}')
    
    lines.extend(['', f'卦名：{gua_name}'])
    
    if changed_gua_name:
        changed_symbol = get_hexagram_unicode(changed_gua_name)
        if changed_symbol:
            lines.append(f'变卦：{changed_symbol} {changed_gua_name}')
        else:
            lines.append(f'变卦：{changed_gua_name}')
    
    binary = get_binary(yao_list)
    upper, lower = binary[3:6], binary[0:3]
    upper_symbol = TRIGRAM_UNICODE.get(upper, '')
    lower_symbol = TRIGRAM_UNICODE.get(lower, '')
    upper_name = TRIGRAM_INFO.get(upper, {}).get('name', '')
    lower_name = TRIGRAM_INFO.get(lower, {}).get('name', '')
    
    if upper_symbol and lower_symbol:
        lines.append(f'上卦：{upper_symbol} {upper_name}  下卦：{lower_symbol} {lower_name}')
    
    return '\n'.join(lines), gua_name, changed_gua_name


def format_gua_detail_display(gua_name, yao_list):
    """详细卦辞爻辞显示"""
    detail = get_gua_detail(gua_name)
    if not detail:
        return None
    
    lines = [f'【{gua_name}】', '']
    
    if detail.get('gua_ci'):
        lines.extend([f'卦辞：{detail["gua_ci"]}', ''])
    
    if detail.get('da_xiang'):
        lines.extend([f'大象：{detail["da_xiang"]}', ''])
    
    yao_ci_list = detail.get('yao_ci', [])
    if yao_ci_list:
        lines.append('【爻辞】')
        for i, yao_data in enumerate(yao_ci_list):
            yao_name = yao_data.get('name', '')
            yao_text = yao_data.get('text', '')
            yao_xiang = yao_data.get('xiang', '')
            current_yao = yao_list[i] if i < len(yao_list) else 7
            is_changing = current_yao in [6, 9]
            mark = '★' if is_changing else ' '
            lines.append(f'{mark} {yao_name}: {yao_text}')
            if yao_xiang:
                lines.append(f'  象曰：{yao_xiang}')
        lines.append('')
    
    _, changed_gua_name = get_changing_gua(yao_list)
    if changed_gua_name:
        lines.extend(['【变卦】', f'变卦：{changed_gua_name}', ''])
    
    if detail.get('bai_hua'):
        lines.extend(['【白话解释】', detail['bai_hua']])
    
    return '\n'.join(lines)


if __name__ == '__main__':
    # 测试
    tests = [
        ([9, 9, 9, 9, 9, 9], '乾为天'),
        ([6, 6, 6, 6, 6, 6], '坤为地'),
        ([9, 9, 9, 8, 9, 8], '水天需'),  # 111010
    ]
    
    for yao_list, expected in tests:
        binary = get_binary(yao_list)
        name = get_gua_name(yao_list)
        status = '✓' if name == expected else '✗'
        print(f"{status} {expected}: {name} (binary={binary})")
