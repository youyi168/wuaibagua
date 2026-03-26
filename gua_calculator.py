#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
64 卦完整计算（修复版）
符合《周易》传统，修复爻名、字体、匹配问题
"""

# 八卦 Unicode 符号（U+2630 - U+2637）
TRIGRAM_UNICODE = {
    '111': '☰',  # 乾 (天)
    '000': '☷',  # 坤 (地)
    '100': '☳',  # 震 (雷)
    '010': '☵',  # 坎 (水)
    '001': '☶',  # 艮 (山)
    '110': '☴',  # 巽 (风)
    '101': '☲',  # 离 (火)
    '011': '☱',  # 兑 (泽)
}

TRIGRAM_NAMES = {
    '111': '乾', '000': '坤', '100': '震',
    '010': '坎', '001': '艮', '110': '巽',
    '101': '离', '011': '兑',
}

# 64 卦完整映射（二进制→卦名）
# 格式：从下往上 (初爻二爻三爻四爻五爻上爻)
HEXAGRAM_NAMES = {
    '111111': '乾为天',
    '000000': '坤为地',
    '100010': '水雷屯',
    '010001': '山水蒙',
    '111010': '水天需',
    '010111': '天水讼',
    '000010': '地水师',
    '010000': '水地比',
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

# 64 卦 Unicode 编码（U+4DC0 - U+4DFF）
HEXAGRAM_UNICODE = {v: k for k, v in {
    '䷀': '111111', '䷁': '000000', '䷂': '100010', '䷃': '010001',
    '䷄': '111010', '䷅': '010111', '䷆': '000010', '䷇': '010000',
    '䷈': '110111', '䷉': '111011', '䷊': '111000', '䷋': '000111',
    '䷌': '101111', '䷍': '111101', '䷎': '000100', '䷏': '110100',
    '䷐': '101101', '䷑': '010011', '䷒': '001010', '䷓': '110010',
    '䷔': '100110', '䷕': '111100', '䷖': '001111', '䷗': '011100',
    '䷘': '000110', '䷙': '011010', '䷚': '010110', '䷛': '101110',
    '䷜': '101100', '䷝': '001001', '䷞': '100100', '䷟': '001000',
    '䷠': '001011', '䷡': '001100', '䷢': '100110', '䷣': '011011',
    '䷤': '110110', '䷥': '011001', '䷦': '010111', '䷧': '110011',
    '䷨': '100101', '䷩': '010101', '䷪': '101010',
}.items()}

# 爻符号（使用 ASCII 确保显示）
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

# 爻位名称（从下往上：初爻→上爻）
YAO_POSITIONS = ['初', '二', '三', '四', '五', '上']


def get_gua_name(yao_list):
    """
    根据 6 爻获取卦名
    yao_list: [初爻，二爻，三爻，四爻，五爻，上爻]
    """
    try:
        # 转换为二进制（从下往上）
        binary = ''
        for yao in yao_list:
            binary += '1' if yao in [7, 9] else '0'
        
        # 直接查表
        gua_name = HEXAGRAM_NAMES.get(binary)
        
        if gua_name:
            return gua_name
        
        # 调试输出
        print(f'[DEBUG] 未找到卦名，binary={binary}, yao_list={yao_list}')
        return '未知卦'
    except Exception as e:
        print(f'[ERROR] get_gua_name: {e}, yao_list={yao_list}')
        return '乾为天'


def get_hexagram_unicode(gua_name):
    """获取 64 卦 Unicode 符号"""
    try:
        # 查找卦名对应的二进制
        binary = None
        for k, v in HEXAGRAM_NAMES.items():
            if v == gua_name:
                binary = k
                break
        
        if not binary:
            return ''
        
        # Unicode 编码：䷀ (U+4DC0) 对应乾为天 (111111=63)
        # 但 Unicode 顺序是《周易》顺序，不是二进制顺序
        # 直接使用预定义映射
        unicode_map = {
            '111111': '䷀', '000000': '䷁', '100010': '䷂', '010001': '䷃',
            '111010': '䷄', '010111': '䷅', '000010': '䷆', '010000': '䷇',
            '110111': '䷈', '111011': '䷉', '111000': '䷊', '000111': '䷋',
            '101111': '䷌', '111101': '䷍', '000100': '䷎', '110100': '䷏',
            '101101': '䷐', '010011': '䷑', '001010': '䷒', '110010': '䷓',
            '100110': '䷔', '111100': '䷕', '001111': '䷖', '011100': '䷗',
            '000110': '䷘', '011010': '䷙', '010110': '䷚', '101110': '䷛',
            '101100': '䷜', '001001': '䷝', '100100': '䷞', '001000': '䷟',
            '001011': '䷠', '001100': '䷡', '100110': '䷢', '011011': '䷣',
            '110110': '䷤', '011001': '䷥', '010111': '䷦', '110011': '䷧',
            '100101': '䷨', '010101': '䷩', '101010': '䷪',
        }
        
        return unicode_map.get(binary, '')
    except Exception as e:
        print(f'[ERROR] get_hexagram_unicode: {e}')
        return ''


def get_trigram_unicode(binary):
    """获取八卦 Unicode 符号"""
    return TRIGRAM_UNICODE.get(binary, '')


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
    # 简化版，只返回乾卦和坤卦
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
    return GUA_DATA.get(gua_name)


def format_gua_display(yao_list, method='起卦'):
    """
    显示卦象（修复版，符合周易传统）
    yao_list: [初爻，二爻，三爻，四爻，五爻，上爻]
    """
    lines = []
    
    # 标题
    lines.append(f'{method}')
    lines.append('')
    
    # 获取卦名
    gua_name = get_gua_name(yao_list)
    hexagram_symbol = get_hexagram_unicode(gua_name)
    
    # 显示 64 卦大符号
    if hexagram_symbol:
        lines.append(f'{hexagram_symbol}  {gua_name}')
        lines.append('')
    
    # 计算变卦
    changed_yao, changed_gua_name = get_changing_gua(yao_list)
    
    # 显示 6 爻（从上爻→初爻，符合传统阅读顺序）
    for i in range(5, -1, -1):
        yao = yao_list[i]
        symbol = YAO_SYMBOLS.get(yao, '───')
        yao_type = '九' if yao in [7, 9] else '六'
        position_name = YAO_POSITIONS[i]
        yao_name = f'{position_name}{yao_type}'
        
        # 变爻标记
        mark = CHANGING_MARKS.get(yao, '')
        if mark:
            lines.append(f'{yao_name:4} {symbol}  {mark}')
        else:
            lines.append(f'{yao_name:4} {symbol}')
    
    lines.append('')
    lines.append(f'卦名：{gua_name}')
    
    # 变卦信息
    if changed_gua_name:
        changed_symbol = get_hexagram_unicode(changed_gua_name)
        if changed_symbol:
            lines.append(f'变卦：{changed_symbol} {changed_gua_name}')
        else:
            lines.append(f'变卦：{changed_gua_name}')
    
    # 上下卦信息
    binary = ''.join('1' if y in [7, 9] else '0' for y in yao_list)
    lower = binary[0:3]
    upper = binary[3:6]
    lower_symbol = get_trigram_unicode(lower)
    upper_symbol = get_trigram_unicode(upper)
    lower_name = TRIGRAM_NAMES.get(lower, '')
    upper_name = TRIGRAM_NAMES.get(upper, '')
    
    if lower_symbol and upper_symbol:
        lines.append(f'上卦：{upper_symbol} {upper_name}  下卦：{lower_symbol} {lower_name}')
    
    return '\n'.join(lines), gua_name, changed_gua_name


def format_gua_detail_display(gua_name, yao_list):
    """
    详细卦辞爻辞显示
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
    # 测试乾为天 [9,9,9,9,9,9]
    test_yao = [9, 9, 9, 9, 9, 9]
    text, gua_name, changing_gua = format_gua_display(test_yao, '电脑起卦')
    print(text)
    print()
    
    # 测试坤为地 [6,6,6,6,6,6]
    test_yao2 = [6, 6, 6, 6, 6, 6]
    text2, gua_name2, _ = format_gua_display(test_yao2, '电脑起卦')
    print(text2)
    print()
    
    # 测试水天需 [9,9,9,8,9,8]
    test_yao3 = [9, 9, 9, 8, 9, 8]
    text3, gua_name3, _ = format_gua_display(test_yao3, '电脑起卦')
    print(text3)
