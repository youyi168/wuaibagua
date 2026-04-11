#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 组件模块
可复用的卡片、按钮、Canvas 爻符组件
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle
import ui_theme as T


# ==================== 背景辅助 ====================

def apply_card_bg(widget, radius=None):
    """卡片背景"""
    if radius is None:
        radius = T.CARD_RADIUS
    with widget.canvas.before:
        Color(*T.COLOR_BG_CARD)
        widget._bg_rect = RoundedRectangle(size=widget.size, pos=widget.pos, radius=radius)
        widget.bind(size=lambda *a: setattr(widget._bg_rect, 'size', widget.size))
        widget.bind(pos=lambda *a: setattr(widget._bg_rect, 'pos', widget.pos))
    return widget


def apply_gold_bg(widget, radius=None):
    """金色背景（按钮用）"""
    if radius is None:
        radius = T.BUTTON_RADIUS
    with widget.canvas.before:
        Color(*T.COLOR_GOLD)
        widget._bg_rect = RoundedRectangle(size=widget.size, pos=widget.pos, radius=radius)
        widget.bind(size=lambda *a: setattr(widget._bg_rect, 'size', widget.size))
        widget.bind(pos=lambda *a: setattr(widget._bg_rect, 'pos', widget.pos))
    return widget


def create_gold_button(text, font_size=None, height=None, **kwargs):
    """金色渐变按钮"""
    btn = Button(
        text=text,
        font_size=font_size or dp(15),
        size_hint_y=None,
        height=height or dp(48),
        color=T.COLOR_BG,
        bold=True,
        background_color=(0, 0, 0, 0),
        background_normal='',
        **kwargs
    )
    apply_gold_bg(btn)
    return btn


def create_outline_button(text, font_size=None, height=None, **kwargs):
    """描边按钮（副操作）"""
    btn = Button(
        text=text,
        font_size=font_size or dp(13),
        size_hint_y=None,
        height=height or dp(42),
        color=T.COLOR_GOLD,
        background_color=(0, 0, 0, 0),
        background_normal='',
        **kwargs
    )
    with btn.canvas.before:
        Color(0, 0, 0, 0)
        btn._bg_rect = RoundedRectangle(size=btn.size, pos=btn.pos, radius=T.BUTTON_RADIUS, border=(1, 1, 1, 1))
        btn.bind(size=lambda *a: setattr(btn._bg_rect, 'size', btn.size))
        btn.bind(pos=lambda *a: setattr(btn._bg_rect, 'pos', btn.pos))
    return btn


def create_action_button(text, font_size=None, height=None, **kwargs):
    """副按钮（半透明金边）"""
    btn = Button(
        text=text,
        font_size=font_size or dp(12),
        size_hint_y=None,
        height=height or dp(42),
        color=T.COLOR_GOLD,
        background_color=(0, 0, 0, 0),
        background_normal='',
        **kwargs
    )
    with btn.canvas.before:
        Color(0.15, 0.15, 0.25, 0.8)
        btn._bg_rect = RoundedRectangle(size=btn.size, pos=btn.pos, radius=T.BUTTON_RADIUS)
        btn.bind(size=lambda *a: setattr(btn._bg_rect, 'size', btn.size))
        btn.bind(pos=lambda *a: setattr(btn._bg_rect, 'pos', btn.pos))
    return btn


# ==================== 卡片式按钮 ====================

def create_method_card(text, subtitle=None, height=None):
    """起卦方式卡片"""
    layout = BoxLayout(
        orientation='vertical',
        padding=(dp(12), dp(10)),
        spacing=dp(2),
        size_hint_y=None,
        height=height or dp(72),
    )
    apply_card_bg(layout)

    main_label = Label(
        text=text,
        font_size=font_size or dp(16),
        bold=True,
        color=T.COLOR_GOLD,
        size_hint_y=0.6,
    )
    layout.add_widget(main_label)

    if subtitle:
        sub_label = Label(
            text=subtitle,
            font_size=dp(11),
            color=T.COLOR_TEXT_SECOND,
            size_hint_y=0.4,
        )
        layout.add_widget(sub_label)
    else:
        layout.add_widget(Label(text='', size_hint_y=0.4))

    return layout


# ==================== Canvas 爻符 ====================

def draw_yao_in_canvas(canvas_obj, is_yang, is_changing=False, width=None, x_offset=0):
    """在 canvas 上绘制单条爻符
    
    Args:
        canvas_obj: Kivy canvas 对象
        is_yang: True=阳爻（实线）, False=阴爻（两段）
        is_changing: 是否为变爻
        width: 线条宽度（不传则用 canvas_obj.width）
        x_offset: X 偏移
    """
    w = width if width is not None else getattr(canvas_obj, 'width', dp(100))
    margin = w * 0.15
    line_w = w - 2 * margin
    color = T.COLOR_GOLD_FAINT if is_changing else T.COLOR_GOLD
    h = T.YAO_LINE_HEIGHT

    with canvas_obj:
        Color(*color)
        if is_yang:
            RoundedRectangle(
                pos=(x_offset + margin, 0),
                size=(line_w, h),
                radius=[T.YAO_LINE_RADIUS] * 4
            )
        else:
            gap = line_w * 0.08
            half = (line_w - gap) / 2
            RoundedRectangle(
                pos=(x_offset + margin, 0),
                size=(half, h),
                radius=[T.YAO_LINE_RADIUS] * 4
            )
            RoundedRectangle(
                pos=(x_offset + margin + half + gap, 0),
                size=(half, h),
                radius=[T.YAO_LINE_RADIUS] * 4
            )


# ==================== GuaSymbolWidget ====================

class GuaSymbolWidget(BoxLayout):
    """卦象符号组件：Canvas 绘制 6 爻"""
    def __init__(self, yao_list=None, binary_str=None, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(2), **kwargs)
        self.size_hint_y = None

        if binary_str:
            from gua_helpers import yao_lines_from_binary
            self.yao_list = yao_lines_from_binary(binary_str)
        elif yao_list:
            self.yao_list = yao_list
        else:
            self.yao_list = [7, 7, 7, 7, 7, 7]

        self._draw_yao()

    def _draw_yao(self):
        self.clear_widgets()
        yao_h = dp(5)
        total_h = 6 * (yao_h + dp(2))
        self.height = total_h

        for i in range(5, -1, -1):
            yao_type = self.yao_list[i] if i < len(self.yao_list) else 7
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=yao_h)
            is_yang = yao_type in [7, 9]
            is_changing = yao_type in [6, 9]
            line_w = dp(40)

            if is_yang:
                line = BoxLayout(size_hint_x=None, width=line_w)
                with line.canvas:
                    Color(* (T.COLOR_GOLD_FAINT if is_changing else T.COLOR_GOLD))
                    line._rect = RoundedRectangle(size=(line_w, yao_h), radius=[dp(2)])
                    line.bind(size=lambda *a: setattr(line._rect, 'size', (line_w, yao_h)))
                row.add_widget(Widget())
                row.add_widget(line)
                row.add_widget(Widget())
            else:
                gap = dp(6)
                half_w = (line_w - gap) / 2
                left = BoxLayout(size_hint_x=None, width=line_w)
                with left.canvas:
                    Color(*T.COLOR_GOLD)
                    left._rect1 = RoundedRectangle(pos=(dp(2), 0), size=(half_w, yao_h), radius=[dp(2)])
                    left._rect2 = RoundedRectangle(pos=(dp(2) + half_w + gap, 0), size=(half_w, yao_h), radius=[dp(2)])
                row.add_widget(Widget())
                row.add_widget(left)
                row.add_widget(Widget())

            self.add_widget(row)


class MiniGuaWidget(Widget):
    """迷你卦象符号（64卦卡片用）"""
    def __init__(self, yao_list=None, binary_str=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.width = dp(40)
        self.height = dp(40)

        if binary_str:
            from gua_helpers import yao_lines_from_binary
            self.yao_list = yao_lines_from_binary(binary_str)
        elif yao_list:
            self.yao_list = yao_list
        else:
            self.yao_list = [7, 7, 7, 7, 7, 7]

        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *args):
        self.canvas.clear()
        yao_h = dp(3)
        gap = dp(2)
        total_h = 6 * (yao_h + gap)
        y_start = self.y + (self.height - total_h) / 2
        line_w = self.width - dp(6)

        with self.canvas:
            for i in range(6):
                y = y_start + i * (yao_h + gap)
                yao_type = self.yao_list[i] if i < len(self.yao_list) else 7
                is_yang = yao_type in [7, 9]

                if is_yang:
                    Color(*T.COLOR_GOLD)
                    RoundedRectangle(pos=(self.x + dp(3), y), size=(line_w, yao_h), radius=[dp(1)])
                else:
                    half = (line_w - dp(4)) / 2
                    Color(*T.COLOR_GOLD)
                    RoundedRectangle(pos=(self.x + dp(3), y), size=(half, yao_h), radius=[dp(1)])
                    RoundedRectangle(pos=(self.x + dp(3) + half + dp(4), y), size=(half, yao_h), radius=[dp(1)])
