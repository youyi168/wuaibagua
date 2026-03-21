# -*- coding: utf-8 -*-
"""测试卦象映射逻辑"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

BAGUA_NAMES = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']

LIUSHI_GUA = [
    ['乾为天', '天泽履', '天火同人', '天雷无妄', '天风姤', '天水讼', '天山遁', '天地否'],
    ['泽天夬', '兑为泽', '泽火革', '泽雷随', '泽风大过', '泽水困', '泽山咸', '泽地萃'],
    ['火天大有', '火泽睽', '离为火', '火雷噬嗑', '火风鼎', '火水未济', '火山旅', '火地晋'],
    ['雷天大壮', '雷泽归妹', '雷火丰', '震为雷', '雷风恒', '雷水解', '雷山小过', '雷地豫'],
    ['风天小畜', '风泽中孚', '风火家人', '风雷益', '巽为风', '风水涣', '风山渐', '风地观'],
    ['水天需', '水泽节', '水火既济', '水雷屯', '水风井', '坎为水', '水山蹇', '水地比'],
    ['山天大畜', '山泽损', '山火贲', '山雷颐', '山风蛊', '山水蒙', '艮为山', '山地剥'],
    ['地天泰', '地泽临', '地火明夷', '地雷复', '地风升', '地水师', '地山谦', '坤为地']
]

def _get_trigram(yao1, yao2, yao3):
    bit1 = 1 if '阳' in yao1['yin_yang'] else 0
    bit2 = 1 if '阳' in yao2['yin_yang'] else 0
    bit3 = 1 if '阳' in yao3['yin_yang'] else 0
    index = bit3 * 4 + bit2 * 2 + bit1
    trigram_map = {7: 0, 6: 1, 5: 2, 4: 3, 3: 4, 2: 5, 1: 6, 0: 7}
    return trigram_map.get(index, 7)

def test_gua(name, yao_list, expected_gua_name, expected_upper, expected_lower):
    print(f'Test: {name}')
    
    lower = _get_trigram(yao_list[0], yao_list[1], yao_list[2])
    upper = _get_trigram(yao_list[3], yao_list[4], yao_list[5])
    
    gua_name = LIUSHI_GUA[upper][lower]
    
    yao_display = [y['yin_yang'] for y in yao_list]
    print(f'  Yao (初->上): {yao_display}')
    print(f'  Lower (初二三): {BAGUA_NAMES[lower]}, Upper (四五上): {BAGUA_NAMES[upper]}')
    print(f'  Gua Name: {gua_name}')
    print(f'  Expected: {expected_gua_name}, Upper={expected_upper}, Lower={expected_lower}')
    
    ok = (gua_name == expected_gua_name and 
          BAGUA_NAMES[upper] == expected_upper and 
          BAGUA_NAMES[lower] == expected_lower)
    print(f'  Result: {"PASS" if ok else "FAIL"}')
    print()
    return ok

yang = {'yin_yang': '阳'}
yin = {'yin_yang': '阴'}

all_pass = True

# 乾为天：六爻皆阳
all_pass &= test_gua('Qian Wei Tian', [yang, yang, yang, yang, yang, yang], 
                     '乾为天', '乾', '乾')

# 坤为地：六爻皆阴
all_pass &= test_gua('Kun Wei Di', [yin, yin, yin, yin, yin, yin], 
                     '坤为地', '坤', '坤')

# 天地否：上乾下坤
all_pass &= test_gua('Tian Di Pi', [yin, yin, yin, yang, yang, yang], 
                     '天地否', '乾', '坤')

# 地天泰：上坤下乾
all_pass &= test_gua('Di Tian Tai', [yang, yang, yang, yin, yin, yin], 
                     '地天泰', '坤', '乾')

# 离为火
all_pass &= test_gua('Li Wei Huo', [yang, yin, yang, yang, yin, yang], 
                     '离为火', '离', '离')

# 坎为水
all_pass &= test_gua('Kan Wei Shui', [yin, yang, yin, yin, yang, yin], 
                     '坎为水', '坎', '坎')

print('=' * 40)
print(f'All tests: {"PASS" if all_pass else "FAIL"}')
