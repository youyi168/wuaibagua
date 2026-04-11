#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运势 Tab 模块（v2 风格）
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime
import ui_theme as T
from ui_components import apply_card_bg, create_gold_button, create_action_button
from android_jni import show_toast


def build_fortune_tab(app):
    """构建运势 Tab"""
    layout = BoxLayout(
        orientation='vertical',
        padding=(dp(8), dp(4), dp(8), dp(8)),
        spacing=dp(6),
        size_hint_y=None,
    )
    layout.bind(minimum_height=layout.setter('height'))

    # 今日日期（农历风格）
    today = datetime.now()
    date_label = Label(
        text=f'{today.year}年{today.month}月{today.day}日',
        font_size=dp(12),
        color=T.COLOR_TEXT_DIM,
        size_hint_y=None,
        height=dp(20),
        halign='center',
        letter_spacing=1,
    )
    layout.add_widget(date_label)

    # 运势卡片
    app.fortune_card = BoxLayout(
        orientation='vertical',
        size_hint_y=None,
        padding=(dp(12), dp(8)),
        spacing=dp(4),
    )
    app.fortune_card.bind(minimum_height=app.fortune_card.setter('height'))
    apply_card_bg(app.fortune_card)

    app.fortune_gua_name = Label(
        text='点击下方按钮查看今日运势',
        font_size=dp(18),
        color=T.COLOR_GOLD,
        bold=True,
        halign='center',
        size_hint_y=None,
        height=dp(28),
    )
    app.fortune_card.add_widget(app.fortune_gua_name)

    app.fortune_yao_area = BoxLayout(
        orientation='vertical',
        size_hint_y=None,
        spacing=dp(3),
        padding=(dp(15), dp(2)),
    )
    app.fortune_yao_area.bind(minimum_height=app.fortune_yao_area.setter('height'))
    app.fortune_card.add_widget(app.fortune_yao_area)

    app.fortune_desc = Label(
        text='',
        font_size=dp(12),
        color=T.COLOR_TEXT_SECOND,
        halign='center',
        size_hint_y=None,
    )
    app.fortune_desc.bind(size=app.fortune_desc.setter('text_size'))
    app.fortune_card.add_widget(app.fortune_desc)

    layout.add_widget(app.fortune_card)

    # 主按钮
    fortune_btn = create_gold_button('查看今日运势', font_size=dp(14), height=dp(46))
    fortune_btn.bind(on_press=app.daily_gua)
    layout.add_widget(fortune_btn)

    # 操作按钮
    fortune_actions = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(38), spacing=dp(6))
    for text, action in [
        ('详解', app.show_explanation),
        ('六爻', app.show_liuyao),
        ('分享', app.share_gua),
    ]:
        btn = create_action_button(f' {text}', font_size=dp(11), height=dp(38))
        btn.bind(on_press=action)
        fortune_actions.add_widget(btn)
    layout.add_widget(fortune_actions)

    return layout


def update_fortune_display(app, gua_name, yao_list, changing_gua_name):
    """更新运势 Tab 显示"""
    if not hasattr(app, 'fortune_gua_name'):
        return

    app.fortune_gua_name.text = gua_name

    # Canvas 绘制爻符
    app.fortune_yao_area.clear_widgets()
    yao_names = ['上', '五', '四', '三', '二', '初']
    for i in range(6):
        yao = yao_list[5 - i]
        is_yang = yao in [7, 9]
        is_changing = yao in [6, 9]

        row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(14),
            spacing=dp(4),
        )
        row.add_widget(Label(
            text=f'{yao_names[i]}',
            font_size=dp(9),
            color=T.COLOR_TEXT_DIM,
            size_hint_x=0.2,
        ))

        yao_widget = Widget(size_hint_x=0.6)
        yao_color = T.COLOR_GOLD if not is_changing else T.COLOR_GOLD
        yao_widget.bind(size=lambda *a: _redraw_yao(yao_widget, is_yang, is_changing))
        _redraw_yao(yao_widget, is_yang, is_changing)
        row.add_widget(yao_widget)

        row.add_widget(Label(text='', size_hint_x=0.2))
        app.fortune_yao_area.add_widget(row)

    # 描述
    if app.current_gua_detail and app.current_gua_detail.get('bai_hua'):
        app.fortune_desc.text = app.current_gua_detail['bai_hua'][:80] + '...'
    else:
        app.fortune_desc.text = ''
    if changing_gua_name:
        app.fortune_desc.text += f'\n变卦：{changing_gua_name}'


def _redraw_yao(widget, is_yang, is_changing):
    """重绘爻符"""
    widget.canvas.clear()
    color = T.COLOR_GOLD
    with widget.canvas:
        Color(*color)
        if is_yang:
            widget._rect = RoundedRectangle(
                pos=(0, dp(3)),
                size=(widget.width, dp(7)),
                radius=[dp(2)] * 4
            )
        else:
            half = (widget.width - dp(6)) / 2
            widget._rect1 = Rectangle(pos=(0, dp(3)), size=(half, dp(7)))
            widget._rect2 = Rectangle(pos=(half + dp(6), dp(3)), size=(half, dp(7)))
