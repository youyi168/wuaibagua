#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六爻排盘 UI 模块（v2 风格）
深色玄学风，信息密度高，颜色编码
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime
import ui_theme as T
from ui_components import apply_card_bg, create_gold_button, create_action_button
from gua_helpers import get_gua_palace


# ==================== 弹窗入口 ====================

def show_liuyao_popup(yao_list, gua_name, app=None):
    """六爻排盘弹窗（v2 风格）"""
    try:
        from liuyao_paipan import format_liuyao_full
        panduan_text = format_liuyao_full(yao_list, gua_name)

        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        title = Label(
            text='六 爻 排 盘',
            size_hint_y=None,
            height=dp(36),
            font_size=dp(16),
            color=T.COLOR_GOLD,
            bold=True,
            halign='center',
        )
        layout.add_widget(title)

        scroll = ScrollView(size_hint_y=1)
        content = Label(
            text=panduan_text,
            markup=True,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=dp(11),
            color=T.COLOR_TEXT,
            padding=(dp(8), dp(4)),
        )
        content.bind(size=content.setter('text_size'))
        content.bind(texture_size=lambda *a: setattr(content, 'height', content.texture_size[1]))
        scroll.add_widget(content)
        layout.add_widget(scroll)

        popup = Popup(
            title='',
            content=layout,
            size_hint=(0.95, 0.85),
            auto_dismiss=True,
            background_color=T.COLOR_BG,
        )

        close_btn = create_gold_button('关闭', font_size=dp(13), height=dp(42))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)

        popup.open()
    except Exception as e:
        import logging
        logging.getLogger('wuaibagua').error(f'[LiuyaoUI] Error: {e}')
        from android_jni import show_toast
        show_toast('排盘失败')


# ==================== 排盘信息卡片 ====================

def build_gua_info_card(gua_name, changing_gua_name=None):
    """本卦/变卦信息卡片"""
    card = BoxLayout(orientation='vertical', padding=(dp(14), dp(10)), spacing=dp(4), size_hint_y=None, height=dp(60))
    apply_card_bg(card)

    # 标题栏
    title = Label(
        text='本卦',
        font_size=dp(13),
        color=T.COLOR_GOLD,
        bold=True,
        halign='left',
        size_hint_y=None,
        height=dp(20),
    )
    card.add_widget(title)

    # 本卦 → 变卦
    row = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(28))
    
    main_gua = Label(
        text=gua_name,
        font_size=dp(15),
        color=T.COLOR_GOLD,
        bold=True,
        halign='center',
        size_hint_x=0.45,
    )
    row.add_widget(main_gua)

    arrow = Label(
        text='→',
        font_size=dp(16),
        color=T.COLOR_TEXT_DIM,
        halign='center',
        size_hint_x=0.1,
    )
    row.add_widget(arrow)

    change_text = changing_gua_name or '无变卦'
    change_color = T.COLOR_BLUE if changing_gua_name else T.COLOR_TEXT_DIM
    change_gua = Label(
        text=change_text,
        font_size=dp(15),
        color=change_color,
        bold=True,
        halign='center',
        size_hint_x=0.45,
    )
    row.add_widget(change_gua)

    card.add_widget(row)
    return card


def build_time_info_card():
    """起卦时间卡片"""
    card = BoxLayout(orientation='vertical', padding=(dp(14), dp(10)), spacing=dp(4), size_hint_y=None)
    card.bind(minimum_height=card.setter('height'))
    apply_card_bg(card)

    title = Label(
        text='起卦时间',
        font_size=dp(13),
        color=T.COLOR_GOLD,
        bold=True,
        halign='left',
        size_hint_y=None,
        height=dp(20),
    )
    card.add_widget(title)

    now = datetime.now()
    infos = [
        ('公历', now.strftime('%Y年%m月%d日 %H:%M'), T.COLOR_TEXT),
        ('干支', now.strftime('%Y年 %m月 %d日'), T.COLOR_GOLD),
        ('旬空', '寅卯（示例）', T.COLOR_RED),
    ]
    for label, value, color in infos:
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(22))
        row.add_widget(Label(text=label, font_size=dp(11), color=T.COLOR_TEXT_SECOND, size_hint_x=0.3, halign='left'))
        row.add_widget(Label(text=value, font_size=dp(11), color=color, size_hint_x=0.7, halign='right'))
        card.add_widget(row)

    return card


def build_yao_table_card(yao_list, gua_name):
    """六爻排盘表格卡片"""
    card = BoxLayout(orientation='vertical', padding=(dp(10), dp(8)), spacing=dp(4), size_hint_y=None)
    card.bind(minimum_height=card.setter('height'))
    apply_card_bg(card)

    title = Label(
        text='六爻排盘',
        font_size=dp(13),
        color=T.COLOR_GOLD,
        bold=True,
        halign='left',
        size_hint_y=None,
        height=dp(20),
    )
    card.add_widget(title)

    # 表头
    headers = ['爻位', '爻符', '六亲', '纳甲', '纳支', '神煞']
    header_row = BoxLayout(orientation='horizontal', spacing=dp(2), size_hint_y=None, height=dp(20))
    for h in headers:
        header_row.add_widget(Label(
            text=h, font_size=dp(10), color=T.COLOR_TEXT_DIM,
            size_hint_x=1.0 / len(headers), halign='center',
        ))
    card.add_widget(header_row)

    # 爻行
    yao_names = ['上九', '六五', '九四', '九三', '九二', '初九']
    liuqin_list = ['父母', '兄弟', '官鬼', '父母', '妻财', '子孙']
    najia_list = ['己巳', '己未', '己酉', '甲辰', '甲寅', '甲子']
    nazhi_list = ['巳火', '未土', '酉金', '辰土', '寅木', '子水']
    shensha_list = ['世', '螣蛇', '勾陈', '应', '空亡', '白虎']

    for i in range(6):
        yao = yao_list[5 - i] if i < len(yao_list) else 7
        is_yang = yao in [7, 9]
        row = BoxLayout(orientation='horizontal', spacing=dp(2), size_hint_y=None, height=dp(28))

        # 爻位
        row.add_widget(Label(text=yao_names[i], font_size=dp(10), color=T.COLOR_TEXT_SECOND, size_hint_x=1.0 / 6, halign='center'))

        # 爻符（Canvas 绘制）
        yao_widget = Widget(size_hint_x=1.0 / 6)
        yao_color = T.COLOR_GOLD_FAINT if yao in [6, 9] else T.COLOR_GOLD
        with yao_widget.canvas:
            Color(*yao_color)
            if is_yang:
                yao_widget._rect = RoundedRectangle(pos=(dp(4), dp(10)), size=(yao_widget.width - dp(8), dp(6)), radius=[dp(2)])
            else:
                half = (yao_widget.width - dp(12)) / 2
                yao_widget._rect1 = Rectangle(pos=(dp(4), dp(10)), size=(half, dp(6)))
                yao_widget._rect2 = Rectangle(pos=(dp(4) + half + dp(4), dp(10)), size=(half, dp(6)))
        row.add_widget(yao_widget)

        # 六亲
        lq = liuqin_list[i]
        lq_color = T.LIUQIN_COLORS.get(lq, T.COLOR_TEXT)
        row.add_widget(Label(text=lq, font_size=dp(10), color=lq_color, size_hint_x=1.0 / 6, halign='center', bold=True))

        # 纳甲
        row.add_widget(Label(text=najia_list[i], font_size=dp(10), color=T.COLOR_TEXT_SECOND, size_hint_x=1.0 / 6, halign='center'))

        # 纳支
        row.add_widget(Label(text=nazhi_list[i], font_size=dp(10), color=T.COLOR_TEXT, size_hint_x=1.0 / 6, halign='center'))

        # 神煞
        ss = shensha_list[i]
        ss_color = T.COLOR_GOLD if ss == '世' else (T.COLOR_BLUE if ss == '应' else (T.COLOR_RED if ss == '空亡' else T.COLOR_TEXT_DIM))
        row.add_widget(Label(text=ss, font_size=dp(10), color=ss_color, size_hint_x=1.0 / 6, halign='center'))

        card.add_widget(row)

    return card
