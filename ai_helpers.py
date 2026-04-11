#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 助手集成模块
支持豆包等 AI 平台
"""

import logging
import webbrowser
from android_jni import show_toast

logger = logging.getLogger('wuaibagua')

# 豆包快捷链接模板
DOUBAO_CHAT_URL = 'https://www.doubao.com/chat/url-action?action={"pluginId":"Send_Message","payload":{"text":"%s"}}'


def ask_doubao(question):
    """在浏览器中打开豆包，自动带入问题"""
    try:
        import urllib.parse
        encoded = urllib.parse.quote(question)
        url = DOUBAO_CHAT_URL % encoded
        logger.info(f'[Doubao] Opening: {url[:100]}...')
        webbrowser.open(url)
        show_toast('正在打开豆包...')
    except Exception as e:
        logger.error(f'[Doubao] Error: {e}')
        show_toast('打开豆包失败')


def build_doubao_question(gua_name, yao_list=None, changing_gua_name=None, detail_data=None):
    """构建询问豆包的问题文本"""
    parts = [f'我起了一卦：{gua_name}']

    if yao_list:
        yao_names = ['初', '二', '三', '四', '五', '上']
        yao_parts = []
        for i in range(6):
            yao = yao_list[i]
            yao_type = '阳' if yao in [7, 9] else '阴'
            mark = '（变）' if yao in [6, 9] else ''
            yao_parts.append(f'{yao_names[i]}{yao_type}{mark}')
        parts.append(f'爻象：{", ".join(yao_parts)}')

    if changing_gua_name:
        parts.append(f'变卦：{changing_gua_name}')

    if detail_data:
        if detail_data.get('gua_ci'):
            parts.append(f'卦辞：{detail_data["gua_ci"]}')
        if detail_data.get('bai_hua'):
            parts.append(f'解释：{detail_data["bai_hua"][:100]}')

    parts.append('\n请帮我详细解读这个卦象，分析吉凶运势。')

    return '\n'.join(parts)
