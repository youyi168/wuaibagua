#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
起卦 Tab 模块（v2 风格）
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
import ui_theme as T
from ui_components import apply_card_bg, create_gold_button, create_action_button, create_method_card
from android_jni import show_toast


def build_divination_tab(app):
    """构建起卦 Tab"""
    layout = BoxLayout(
        orientation='vertical',
        padding=(dp(10), dp(4), dp(10), dp(10)),
        spacing=dp(6),
        size_hint_y=None,
    )
    layout.bind(minimum_height=layout.setter('height'))

    # 卦象显示区
    app.gua_display_area = BoxLayout(
        orientation='vertical',
        size_hint_y=None,
        height=dp(120),
        spacing=dp(4),
    )
    apply_card_bg(app.gua_display_area)

    # 空状态
    app.empty_state = Label(
        text='☯',
        font_size=dp(48),
        color=T.COLOR_GOLD,
        halign='center',
        valign='middle',
        size_hint_y=None,
        height=dp(88),
    )
    app.empty_hint = Label(
        text='选择起卦方式',
        font_size=dp(14),
        color=T.COLOR_TEXT_SECOND,
        halign='center',
        size_hint_y=None,
        height=dp(22),
    )
    app.gua_display_area.add_widget(app.empty_state)
    app.gua_display_area.add_widget(app.empty_hint)

    # 结果状态
    app.result_state = BoxLayout(orientation='vertical', spacing=dp(3), padding=(dp(8), dp(4)))
    app.result_state.size_hint_y = None
    app.result_state.bind(minimum_height=app.result_state.setter('height'))

    app.gua_name_label = Label(
        text='', font_size=dp(24), color=T.COLOR_GOLD,
        bold=True, halign='center', size_hint_y=None, height=dp(32),
    )
    app.result_state.add_widget(app.gua_name_label)

    app.gua_palace_label = Label(
        text='', font_size=dp(11), color=T.COLOR_TEXT_SECOND,
        halign='center', size_hint_y=None, height=dp(18),
    )
    app.result_state.add_widget(app.gua_palace_label)

    app.yao_draw_area = BoxLayout(
        orientation='vertical', size_hint_y=None, height=dp(110),
        spacing=dp(3), padding=(dp(30), dp(4)),
    )
    app.result_state.add_widget(app.yao_draw_area)

    app.gua_ci_label = Label(
        text='', font_size=dp(12), color=T.COLOR_TEXT,
        halign='center', size_hint_y=None, height=dp(36),
    )
    app.gua_ci_label.bind(size=app.gua_ci_label.setter('text_size'))
    app.result_state.add_widget(app.gua_ci_label)

    app.changing_label = Label(
        text='', font_size=dp(11), color=T.COLOR_GOLD,
        halign='center', size_hint_y=None, height=dp(20),
    )
    app.result_state.add_widget(app.changing_label)

    layout.add_widget(app.gua_display_area)

    # 起卦方式 2x2
    method_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(150))

    for text, sub, method in [
        ('随机起卦', '心诚则灵', 'auto'),
        ('手动选卦', '64卦列表', 'manual'),
        ('金钱起卦', '模拟摇卦', 'jinqian'),
        ('时间起卦', '以时起卦', 'time'),
    ]:
        card = create_method_card(text, subtitle=sub, height=dp(70))
        card_btn = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='')

        if method == 'auto':
            card_btn.bind(on_press=app.auto_gua)
        elif method == 'manual':
            from dialogs import show_manual_select_gua_popup
            card_btn.bind(on_press=lambda x: show_manual_select_gua_popup(app))
        elif method == 'jinqian':
            card_btn.bind(on_press=app.jinqian_gua)
        else:
            card_btn.bind(on_press=app.time_gua)

        card.add_widget(card_btn)
        method_grid.add_widget(card)

    layout.add_widget(method_grid)

    # 功能按钮
    quick_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
    for text, action in [
        ('详解', app.show_explanation),
        ('六爻', app.show_liuyao),
        ('分享', app.share_gua),
        ('复制', app.copy_result),
    ]:
        btn = create_action_button(f' {text}', font_size=dp(12), height=dp(40))
        btn.bind(on_press=action)
        quick_row.add_widget(btn)
    layout.add_widget(quick_row)

    # 重新起卦
    app.redivide_btn = create_gold_button(' 重新起卦', font_size=dp(14), height=dp(42))
    app.redivide_btn.bind(on_press=app.auto_gua)
    app.redivide_btn.opacity = 0
    layout.add_widget(app.redivide_btn)

    return layout
