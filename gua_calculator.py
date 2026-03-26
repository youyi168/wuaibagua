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
    """
    从 txt 文件读取卦象详细数据（符合《图解周易》）
    
    Args:
        gua_name: 卦名全称（如'乾为天'）
    
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
        # 获取简称
        short_name = FULL_TO_SHORT.get(gua_name)
        if not short_name:
            print(f'[WARN] 未找到卦名简称：{gua_name}')
            return None
        
        # 读取 txt 文件（尝试多个路径）
        import os
        
        # 路径 1: 打包后的 APK 路径
        txt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', f'{short_name}卦.txt')
        
        # 路径 2: 开发环境路径（上级目录）
        if not os.path.exists(txt_file):
            txt_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', f'{short_name}卦.txt')
        
        # 路径 3: 当前工作目录
        if not os.path.exists(txt_file):
            txt_file = f'data/{short_name}卦.txt'
        
        if not os.path.exists(txt_file):
            print(f'[WARN] txt 文件不存在：{txt_file} (卦名：{gua_name}, 简称：{short_name})')
            return None
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 txt 文件内容
        result = {
            'gua_ci': '',      # 卦辞
            'da_xiang': '',    # 大象
            'yao_ci': [],      # 爻辞列表
            'bai_hua': '',     # 白话解释
            'full_text': content,  # 完整原文
        }
        
        lines = content.strip().split('\n')
        
        # 提取卦辞（第三行，格式如"乾：元，亨，利，贞。"）
        for line in lines:
            line_stripped = line.strip()
            # 匹配"卦名：内容"格式，卦名为 1-2 个字（注意中文冒号：）
            if ('：' in line_stripped or ':' in line_stripped) and not line_stripped.startswith('【') and not line_stripped.startswith('《') and not line_stripped.startswith('第'):
                # 使用中文冒号分割
                if '：' in line_stripped:
                    parts = line_stripped.split('：', 1)
                else:
                    parts = line_stripped.split(':', 1)
                if len(parts[0]) <= 2:  # 卦名通常 1-2 个字（乾、坤、需等）
                    result['gua_ci'] = parts[1].strip().rstrip('.')
                    break
        
        # 提取大象（《象》曰：...）
        for line in lines:
            if '《象》曰' in line or '象曰' in line:
                if '君子' in line:  # 大象通常包含"君子"
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
                    
                    # 提取爻名和爻辞
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
                    
                    # 查找对应的象曰（往后找 3 行）
                    for j in range(i+1, min(i+4, len(lines))):
                        xiang_line = lines[j]
                        if '《象》曰' in xiang_line or '象曰' in xiang_line:
                            if '君子' not in xiang_line:  # 排除大象
                                yao_data['xiang'] = xiang_line.replace('《象》曰：', '').replace('象曰：', '').rstrip('。').strip()
                                break
                    
                    result['yao_ci'].append(yao_data)
                    break
            i += 1
        
        # 白话解释（使用完整 txt 内容）
        result['bai_hua'] = content
        
        return result
    
    except Exception as e:
        print(f'[ERROR] get_gua_detail failed: {e}')
        return None


def format_gua_display(yao_list, method='起卦'):
    """
    显示卦象（ASCII 版，兼容所有设备）
    从上爻→初爻显示
    """
    lines = [f'[ {method} ]', '']
    
    gua_name = get_gua_name(yao_list)
    lines.append(f'卦名：{gua_name}')
    lines.append('')
    
    changed_yao, changed_gua_name = get_changing_gua(yao_list)
    
    # ASCII 爻符号
    yao_ascii = {
        6: '-- -- X',  # 老阴
        7: '-----',    # 少阳
        8: '-- --',    # 少阴
        9: '----- O',  # 老阳
    }
    
    # 从上爻→初爻显示
    for i in range(5, -1, -1):
        yao = yao_list[i]
        yao_name = get_yao_name(i, yao)
        symbol = yao_ascii.get(yao, '-----')
        lines.append(f'{yao_name:4} {symbol}')
    
    lines.append('')
    
    if changed_gua_name:
        lines.append(f'变卦：{changed_gua_name}')
    
    return '\n'.join(lines), gua_name, changed_gua_name


# 别名，保持兼容
format_gua_display_ascii = format_gua_display


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
    """
    六爻排盘（ASCII 版，避免字体问题）
    使用纯 ASCII 字符，确保所有设备正常显示
    """
    lines = []
    lines.append(f'[ {method} ] 六爻排盘')
    lines.append('')
    lines.append(f'卦名：{gua_name}')
    lines.append('')
    lines.append('爻位   爻象   阴阳')
    lines.append('-' * 30)
    
    # ASCII 爻符号
    yao_ascii = {
        6: '-- -- X',  # 老阴
        7: '-----',    # 少阳
        8: '-- --',    # 少阴
        9: '----- O',  # 老阳
    }
    
    for i in range(5, -1, -1):
        yao = yao_list[i]
        yao_name = get_yao_name(i, yao)
        yinyang = 'Yang' if yao in [7, 9] else 'Yin'
        symbol = yao_ascii.get(yao, '-----')
        line = f'{yao_name:4} {symbol:8} {yinyang}'
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
