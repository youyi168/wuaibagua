#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 v2.0 - UI 主题配置
深色系东方玄学风格
"""

# ==================== 主配色 ====================
# 背景
COLOR_BG = (0.059, 0.059, 0.118, 1)          # #0f0f1e 深紫蓝
COLOR_BG_CARD = (0.137, 0.137, 0.235, 1)      # #23233c 卡片底
COLOR_BG_HEADER = (0.102, 0.102, 0.176, 1)    # #1a1a2e 头部

# 金色主题
COLOR_GOLD = (1.0, 0.843, 0.0, 1)             # #ffd700 亮金
COLOR_GOLD_DARK = (0.788, 0.627, 0.125, 1)    # #c9a020 暗金
COLOR_GOLD_FAINT = (0.6, 0.5, 0.1, 1)         # 微金

# 文字
COLOR_TEXT = (0.9, 0.9, 0.92, 1)              # 主文字
COLOR_TEXT_SECOND = (0.6, 0.6, 0.65, 1)       # 次要文字
COLOR_TEXT_DIM = (0.35, 0.35, 0.4, 1)         # 暗淡文字

# 功能色
COLOR_BLUE = (0.392, 0.706, 0.961, 1)         # #64b5f6 蓝
COLOR_GREEN = (0.3, 0.686, 0.314, 1)          # #4caf50 绿
COLOR_RED = (1.0, 0.42, 0.42, 1)              # #ff6b6b 红
COLOR_PURPLE = (0.808, 0.576, 0.847, 1)       # #ce93d8 紫

# ==================== 尺寸常量 ====================
CARD_RADIUS = [16, 16, 16, 16]
BUTTON_RADIUS = [12, 12, 12, 12]
TAB_HEIGHT = 44
HEADER_HEIGHT = 56

# ==================== 六亲颜色 ====================
LIUQIN_COLORS = {
    '父母': COLOR_GOLD,
    '官鬼': COLOR_RED,
    '兄弟': COLOR_BLUE,
    '妻财': COLOR_GREEN,
    '子孙': COLOR_PURPLE,
}

# ==================== Canvas 爻符参数 ====================
YAO_LINE_HEIGHT = 4
YAO_LINE_GAP = 2
YAO_WIDTH_RATIO = 0.7
YAO_LINE_RADIUS = 2
