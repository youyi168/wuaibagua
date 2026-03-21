#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('main.py', 'r', encoding='utf-8').read()
print(f'main.py 中吾爱八卦: {content.count("吾爱八卦")} 处')
print(f'main.py 中我爱八卦: {content.count("我爱八卦")} 处')
