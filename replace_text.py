#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""搜索并替换 '我爱八卦' 为 '我爱八卦'"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

target = '我爱八卦'
replacement = '我爱八卦'

files_to_check = []

for root, dirs, files in os.walk('.'):
    if '.git' in root:
        continue
    for f in files:
        if f.endswith(('.py', '.spec', '.md', '.txt', '.yml', '.yaml')):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if target in content:
                        count = content.count(target)
                        files_to_check.append((filepath, count, content))
            except:
                pass

print(f'找到包含 "{target}" 的文件:')
for filepath, count, _ in files_to_check:
    print(f'  {filepath}: {count} 处')

# 执行替换
for filepath, count, content in files_to_check:
    new_content = content.replace(target, replacement)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(new_content)
    print(f'已替换: {filepath}')

print(f'\n总计替换了 {sum(c for _, c, _ in files_to_check)} 处')
