#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
64 卦完整计算（按《图解周易》标准逻辑）

排盘规则：
1. 从下往上画爻：初爻→二爻→三爻→四爻→五爻→上爻
2. 下卦（内卦）：初爻、二爻、三爻
3. 上卦（外卦）：四爻、五爻、上爻
4. 卦名 = 上卦名 + 下卦名

二进制（从下往上）：
乾☰=111, 坤☷=000, 震☳=100, 坎☵=010
艮☶=001, 巽☴=110, 离☲=101, 兑☱=011
"""

# 八卦定义
TRIGRAMS = {
    '111': '乾', '000': '坤', '100': '震', '010': '坎',
    '001': '艮', '110': '巽', '101': '离', '011': '兑',
}

# 64 卦完整映射（上卦 + 下卦 → 卦名）
# 二进制格式：下卦 (3 位) + 上卦 (3 位) = 6 位
HEXAGRAM_NAMES = {
    '000000': '坤为地', '000001': '山地剥', '000010': '水地比', '000011': '泽地萃',
    '000100': '雷地豫', '000101': '火地晋', '000110': '风地观', '000111': '天地否',
    '001000': '地山谦', '001001': '艮为山', '001010': '水山蹇', '001011': '泽山咸',
    '001100': '雷山小过', '001101': '火山旅', '001110': '山风蛊', '001111': '天山遁',
    '010000': '地水师', '010001': '山火贲', '010010': '坎为水', '010011': '泽水困',
    '010100': '雷水解', '010101': '火水未济', '010110': '风水涣', '010111': '天水讼',
    '011000': '地泽临', '011001': '山泽损', '011010': '水泽节', '011011': '兑为泽',
    '011100': '雷泽归妹', '011101': '火泽睽', '011110': '风泽中孚', '011111': '天泽履',
    '100000': '地雷复', '100001': '山雷颐', '100010': '水雷屯', '100011': '泽雷随',
    '100100': '震为雷', '100101': '火雷噬嗑', '100110': '风雷益', '100111': '天雷无妄',
    '101000': '地火明夷', '101001': '山水蒙', '101010': '水火既济', '101011': '泽火革',
    '101100': '雷火丰', '101101': '离为火', '101110': '风火家人', '101111': '天火同人',
    '110000': '地风升', '110001': '风山渐', '110010': '水风井', '110011': '泽风大过',
    '110100': '雷风恒', '110101': '火风鼎', '110110': '巽为风', '110111': '天风姤',
    '111000': '地天泰', '111001': '山天大畜', '111010': '水天需', '111011': '泽天夬',
    '111100': '雷天大壮', '111101': '火天大有', '111110': '风天小畜', '111111': '乾为天',
}

# 验证映射表
_values = list(HEXAGRAM_NAMES.values())
if len(set(_values)) < 64:
    from collections import Counter
    print("⚠️  警告：HEXAGRAM_NAMES 有重复卦名")
    for name, count in Counter(_values).items():
        if count > 1:
            print(f"  {name}: {count} 次")

# 爻符号（ASCII 确保显示）
YAO_SYMBOLS = {6: '- -', 7: '───', 8: '- -', 9: '───'}
CHANGING_MARKS = {6: '✕', 9: '○'}
YAO_POSITIONS = ['初', '二', '三', '四', '五', '上']


def get_gua_name(yao_list):
    """
    根据 6 爻获取卦名（符合《图解周易》）
    
    Args:
        yao_list: [初爻，二爻，三爻，四爻，五爻，上爻]
                  每个爻为 6/7/8/9
                  6=老阴，7=少阳，8=少阴，9=老阳
    
    Returns:
        str: 卦名
    """
    try:
        # 转换为二进制（从下往上）
        # 阳爻 (7,9) = 1, 阴爻 (6,8) = 0
        binary = ''
        for yao in yao_list:
            binary += '1' if yao in [7, 9] else '0'
        
        # 查表获取卦名
        gua_name = HEXAGRAM_NAMES.get(binary)
        
        if gua_name:
            return gua_name
        
        # 调试输出
        print(f'[DEBUG] 未找到卦名：binary={binary}, yao_list={yao_list}')
        return '未知卦'
    except Exception as e:
        print(f'[ERROR] get_gua_name: {e}')
        return '乾为天'


def get_binary(yao_list):
    """获取卦象二进制表示"""
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
        
        # Unicode 编码计算（U+4DC0 开始）
        index = int(binary, 2)
        return chr(0x4DC0 + index)
    except Exception as e:
        print(f'[ERROR] get_hexagram_unicode: {e}')
        return ''


def get_changing_gua(yao_list):
    """
    计算变卦（符合《图解周易》）
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


def get_yao_name(position, yao):
    """
    获取爻名（符合《周易》命名规则）
    阳爻称"九"，阴爻称"六"
    """
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
    """
    显示卦象（符合《图解周易》传统）
    从上爻→初爻显示
    """
    lines = [f'{method}', '']
    
    gua_name = get_gua_name(yao_list)
    hexagram_symbol = get_hexagram_unicode(gua_name)
    
    if hexagram_symbol:
        lines.append(f'{hexagram_symbol}  {gua_name}')
        lines.append('')
    
    changed_yao, changed_gua_name = get_changing_gua(yao_list)
    
    # 从上爻→初爻显示
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


def format_liuyao_simple(yao_list, gua_name, method='起卦'):
    """六爻排盘（简化版，避免 Vulkan）"""
    lines = []
    lines.append(f'【{method}】六爻排盘')
    lines.append('')
    lines.append(f'卦名：{gua_name}')
    lines.append('')
    lines.append('爻位  爻象  阴阳')
    lines.append('─' * 30)
    
    for i in range(5, -1, -1):
        yao = yao_list[i]
        yao_name = get_yao_name(i, yao)
        yinyang = '阳' if yao in [7, 9] else '阴'
        symbol = YAO_SYMBOLS.get(yao, '───')
        mark = CHANGING_MARKS.get(yao, '')
        line = f'{yao_name:4} {symbol} {yinyang:2} {mark}'
        lines.append(line)
    
    lines.append('')
    
    _, changed_gua_name = get_changing_gua(yao_list)
    if changed_gua_name:
        lines.append(f'变卦：{changed_gua_name}')
    
    return '\n'.join(lines)


if __name__ == '__main__':
    # 测试
    print("=" * 60)
    print("64 卦映射表验证")
    print("=" * 60)
    
    keys = list(HEXAGRAM_NAMES.keys())
    values = list(HEXAGRAM_NAMES.values())
    print(f"总卦数：{len(values)}")
    print(f"唯一卦数：{len(set(values))}")
    
    if len(set(values)) == 64:
        print("\n✅ 64 卦完整，无重复！")
    else:
        from collections import Counter
        repeats = [(n, c) for n, c in Counter(values).items() if c > 1]
        if repeats:
            print("\n❌ 有重复卦名:")
            for name, count in repeats:
                print(f"  {name}: {count} 次")
    
    # 测试几个卦
    print("\n" + "=" * 60)
    print("卦象计算测试")
    print("=" * 60)
    
    tests = [
        ([9, 9, 9, 9, 9, 9], '乾为天'),  # 111111
        ([6, 6, 6, 6, 6, 6], '坤为地'),  # 000000
        ([9, 9, 9, 8, 9, 8], '水天需'),  # 111010
    ]
    
    for yao_list, expected in tests:
        binary = get_binary(yao_list)
        name = get_gua_name(yao_list)
        status = '✓' if name == expected else '✗'
        print(f"{status} {expected}: {name} (binary={binary})")
