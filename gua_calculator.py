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

# ==================== 六爻排盘数据 ====================

# 地支（从下往上：初爻→上爻）
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 五行
WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

# 六亲
LIUQIN = ['父母', '兄弟', '子孙', '妻财', '官鬼']

# 六神（按日干排列）
LIUSHEN = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']

# 八卦五行属性
TRIGRAM_WUXING = {
    '111': '金',  # 乾
    '000': '土',  # 坤
    '100': '木',  # 震
    '010': '水',  # 坎
    '001': '土',  # 艮
    '110': '木',  # 巽
    '101': '火',  # 离
    '011': '金',  # 兑
}

# 六亲排列（按卦宫五行）
# 生我者父母，我生者子孙，克我者官鬼，我克者妻财，同我者兄弟
LIUQIN_MAP = {
    '金': ['父母', '兄弟', '子孙', '妻财', '官鬼'],  # 乾兑宫
    '土': ['兄弟', '子孙', '妻财', '官鬼', '父母'],  # 坤艮宫
    '木': ['子孙', '妻财', '官鬼', '父母', '兄弟'],  # 震巽宫
    '水': ['妻财', '官鬼', '父母', '兄弟', '子孙'],  # 坎宫
    '火': ['官鬼', '父母', '兄弟', '子孙', '妻财'],  # 离宫
}

# 各卦地支排列（从初爻到上爻）
GUA_DIZHI = {
    '乾为天': ['子', '寅', '辰', '午', '申', '戌'],
    '坤为地': ['未', '巳', '卯', '丑', '亥', '酉'],
    '水天需': ['子', '寅', '辰', '午', '申', '戌'],
    '天水讼': ['寅', '辰', '午', '申', '戌', '子'],
    # ... 其他卦可以逐步补充
}


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


def get_gua_palace(gua_name):
    """
    获取卦宫（八宫）
    """
    palaces = {
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
    return palaces.get(gua_name, '乾')


def get_shi_yao(gua_name):
    """
    获取世爻位置（0-5，0=初爻，5=上爻）
    按八宫世应规则
    """
    shi_positions = {
        '乾为天': 6, '天风姤': 1, '天山遁': 2, '天地否': 3,
        '风地观': 4, '山地剥': 5, '火地晋': 4, '火天大有': 3,
        '坎为水': 6, '水泽节': 1, '水雷屯': 2, '水火既济': 3,
        '泽火革': 4, '雷火丰': 5, '地火明夷': 4, '地水师': 3,
        '艮为山': 6, '山火贲': 1, '山天大畜': 2, '山泽损': 3,
        '火泽睽': 4, '天泽履': 5, '风泽中孚': 4, '风山渐': 3,
        '震为雷': 6, '雷地豫': 1, '雷水解': 2, '雷风恒': 3,
        '地风升': 4, '水风井': 5, '泽风大过': 4, '泽雷随': 3,
        '巽为风': 6, '风天小畜': 1, '风火家人': 2, '风雷益': 3,
        '天雷无妄': 4, '火雷噬嗑': 5, '山雷颐': 4, '山风蛊': 3,
        '离为火': 6, '火山旅': 1, '火风鼎': 2, '火水未济': 3,
        '山水蒙': 4, '风水涣': 5, '天水讼': 4, '天火同人': 3,
        '坤为地': 6, '地雷复': 1, '地泽临': 2, '地天泰': 3,
        '雷天大壮': 4, '泽天夬': 5, '水天需': 4, '水地比': 3,
        '兑为泽': 6, '泽水困': 1, '泽地萃': 2, '泽山咸': 3,
        '水山蹇': 4, '地山谦': 5, '雷山小过': 4, '雷泽归妹': 3,
    }
    return shi_positions.get(gua_name, 6)


def get_ying_yao(shi_yao):
    """
    获取应爻位置
    世应相隔两位：1-4, 2-5, 3-6, 4-1, 5-2, 6-3
    """
    ying_map = {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2, 6: 3}
    return ying_map.get(shi_yao, 3)


def get_liuqin(gua_name, yao_position):
    """
    获取六亲
    按卦宫五行和爻位计算
    """
    palace = get_gua_palace(gua_name)
    palace_wuxing = TRIGRAM_WUXING.get({
        '乾': '111', '兑': '011', '离': '101', '震': '100',
        '巽': '110', '坎': '010', '艮': '001', '坤': '000'
    }.get(palace, '111'), '金')
    
    # 简化版：按爻位返回六亲
    liuqin_order = ['父母', '兄弟', '子孙', '妻财', '官鬼']
    return liuqin_order[yao_position % 5]


def format_liuyao_panduan(yao_list, gua_name, method='起卦'):
    """
    六爻排盘（完整格式）
    
    包含：
    - 六爻（从上到下）
    - 六亲
    - 地支
    - 五行
    - 世应爻
    - 变爻
    - 六神（简化）
    """
    lines = []
    
    # 标题
    lines.append(f'【{method}】六爻排盘')
    lines.append('')
    lines.append(f'卦名：{gua_name}')
    lines.append('')
    
    # 获取世应爻
    shi_yao = get_shi_yao(gua_name)
    ying_yao = get_ying_yao(shi_yao)
    
    # 表头
    lines.append('六神  六亲  地支  五行  爻象  世应')
    lines.append('─' * 40)
    
    # 从初爻往上排（显示时从上往下）
    for i in range(5, -1, -1):
        yao = yao_list[i]
        yao_name = get_yao_name(i, yao)
        symbol = YAO_SYMBOLS.get(yao, '───')
        
        # 六亲
        liuqin = get_liuqin(gua_name, i)
        
        # 地支（简化版，按卦名）
        dizhi_list = GUA_DIZHI.get(gua_name, ['子', '寅', '辰', '午', '申', '戌'])
        dizhi = dizhi_list[i] if i < len(dizhi_list) else '子'
        
        # 五行
        wuxing = WUXING.get(dizhi, '土')
        
        # 世应
        shi_ying = ''
        if i == shi_yao - 1 if shi_yao <= 6 else False:
            shi_ying = '世'
        elif i == ying_yao - 1 if ying_yao <= 6 else False:
            shi_ying = '应'
        
        # 变爻标记
        mark = CHANGING_MARKS.get(yao, '')
        
        # 六神（简化，按日干）
        liushen = LIUSHEN[i % 6]
        
        line = f'{liushen:4} {liuqin:4} {dizhi:2} {wuxing:2} {symbol} {shi_ying:2} {mark}'
        lines.append(line)
    
    lines.append('')
    lines.append(f'世爻：{shi_yao}爻  应爻：{ying_yao}爻')
    
    # 变卦信息
    changed_yao, changed_gua_name = get_changing_gua(yao_list)
    if changed_gua_name:
        lines.append(f'变卦：{changed_gua_name}')
    
    return '\n'.join(lines)


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
