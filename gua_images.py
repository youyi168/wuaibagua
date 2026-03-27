#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卦象符号图片显示模块
统一尺寸：爻符号 120x40px, 64 卦 120x260px
"""

import os

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
SYMBOLS_DIR = os.path.join(RESOURCES_DIR, 'symbols')
HEXAGRAMS_DIR = os.path.join(RESOURCES_DIR, 'hexagrams')

# 图片尺寸
YAO_IMAGE_SIZE = (120, 40)      # 爻符号
HEXAGRAM_IMAGE_SIZE = (120, 260) # 64 卦

# 爻符号图片路径
YAO_IMAGES = {
    6: os.path.join(SYMBOLS_DIR, 'yin_old.png'),   # 老阴
    7: os.path.join(SYMBOLS_DIR, 'yang.png'),      # 少阳
    8: os.path.join(SYMBOLS_DIR, 'yin.png'),       # 少阴
    9: os.path.join(SYMBOLS_DIR, 'yang_old.png'),  # 老阳
}

# 64 卦图片路径（按二进制）
HEXAGRAM_IMAGES = {}
for i in range(64):
    binary = format(i, '06b')
    HEXAGRAM_IMAGES[binary] = os.path.join(HEXAGRAMS_DIR, f'hex_{binary}.png')

# 爻位名称
YAO_POSITIONS = ['初', '二', '三', '四', '五', '上']


def get_yao_image_path(yao_value):
    """获取爻符号图片路径"""
    return YAO_IMAGES.get(yao_value, YAO_IMAGES[7])


def get_hexagram_image_path(binary):
    """获取 64 卦图片路径"""
    return HEXAGRAM_IMAGES.get(binary, HEXAGRAM_IMAGES['111111'])


def get_yao_name(position, yao_value):
    """获取爻名"""
    yao_type = '九' if yao_value in [7, 9] else '六'
    return f'{YAO_POSITIONS[position]}{yao_type}'


def check_images_exist():
    """检查图片文件是否存在"""
    missing = []
    
    for path in YAO_IMAGES.values():
        if not os.path.exists(path):
            missing.append(path)
    
    for path in HEXAGRAM_IMAGES.values():
        if not os.path.exists(path):
            missing.append(path)
    
    if missing:
        print(f"⚠️  缺少 {len(missing)} 个图片文件")
        return False
    
    print(f"✅ 所有图片文件存在 ({len(YAO_IMAGES) + len(HEXAGRAM_IMAGES)} 个)")
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("卦象符号图片模块测试")
    print("=" * 60)
    
    check_images_exist()
    
    print("\n爻符号图片:")
    for yao_val, path in YAO_IMAGES.items():
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"  {yao_val}: {path.split('/')[-1]} {exists}")
    
    print("\n64 卦图片 (前 5 个):")
    for binary, path in list(HEXAGRAM_IMAGES.items())[:5]:
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"  {binary}: {path.split('/')[-1]} {exists}")
