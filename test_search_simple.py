#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试搜索功能核心逻辑
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 模拟测试
def test_search_urls():
    """测试搜索 URL 生成"""
    gua_name = "乾为天"
    dong_yao_positions = [1, 3]  # 初爻和三爻动
    yao_names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
    
    # 测试卦名搜索
    url1 = f"https://www.baidu.com/s?wd={gua_name}"
    print(f"卦名搜索: {url1}")
    
    # 测试动爻搜索
    if len(dong_yao_positions) == 1:
        yao_name = yao_names[dong_yao_positions[0] - 1]
        query = f"{gua_name} {yao_name}"
    else:
        query = f"{gua_name} 动爻"
    
    url2 = f"https://www.baidu.com/s?wd={query}"
    print(f"动爻搜索: {url2}")
    
    print("\n测试通过！")


if __name__ == '__main__':
    test_search_urls()
