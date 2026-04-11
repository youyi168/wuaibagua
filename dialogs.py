#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
弹窗模块
分享、卦象详解、设置等对话框
"""

import logging
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.metrics import dp
import ui_theme as T
from ui_components import apply_card_bg, create_gold_button
from android_jni import copy_to_clipboard, show_toast

logger = logging.getLogger('wuaibagua')


# ==================== 分享弹窗 ====================

def show_share_popup(text):
    """分享弹窗"""
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        title = Label(
            text='选择分享方式',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            color=T.COLOR_GOLD,
            bold=True,
        )
        layout.add_widget(title)

        popup = None  # 先声明

        options = [
            ('复制文本', lambda: _do_copy(text, popup)),
            ('分享到微信', lambda: _do_share('微信', text, popup)),
            ('分享到 QQ', lambda: _do_share('QQ', text, popup)),
        ]

        for name, callback in options:
            btn = create_gold_button(f' {name}', font_size=dp(14), height=dp(44))
            btn.bind(on_press=lambda x, cb=callback: cb())
            layout.add_widget(btn)

        cancel_btn = Button(
            text='取消',
            size_hint_y=None,
            height=dp(42),
            font_size=dp(14),
            color=T.COLOR_TEXT_SECOND,
            background_color=(0, 0, 0, 0),
            background_normal='',
        )
        cancel_btn.bind(on_press=lambda x: popup.dismiss() if popup else None)
        layout.add_widget(cancel_btn)

        popup = Popup(
            title='',
            content=layout,
            size_hint=(0.85, 0.55),
            auto_dismiss=False,
            background_color=T.COLOR_BG,
        )
        popup.open()
    except Exception as e:
        logger.error(f'[Dialog] share_popup error: {e}')


def _do_copy(text, popup):
    copy_to_clipboard(text)
    popup.dismiss()
    show_toast('已复制')

def _do_share(platform, text, popup):
    copy_to_clipboard(text)
    popup.dismiss()
    show_toast(f'已复制，请打开{platform}粘贴')


# ==================== 卦象详解弹窗 ====================

def show_gua_explanation(gua_name, detail_data, yao_list=None, changing_gua_name=None, duangua_result=None):
    """卦象详解弹窗"""
    try:
        import gua_db
        db_data = gua_db.get_gua_by_name(gua_name)
        if not db_data:
            show_toast(f'未找到 {gua_name}')
            return

        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        title = Label(
            text=f'【{gua_name}】详解',
            size_hint_y=None,
            height=dp(36),
            font_size=dp(16),
            color=T.COLOR_GOLD,
            bold=True,
        )
        layout.add_widget(title)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        content.bind(minimum_height=content.setter('height'))

        def add_section(label_text, detail_text, fs=dp(13)):
            sec = Label(
                text=label_text,
                size_hint_y=None, height=dp(24),
                font_size=dp(14), color=T.COLOR_GOLD, bold=True, halign='left',
            )
            content.add_widget(sec)
            txt = Label(
                text=detail_text,
                size_hint_y=None,
                halign='left', valign='top',
                font_size=fs, color=T.COLOR_TEXT, padding=(8, 3),
            )
            txt.bind(size=txt.setter('text_size'))
            content.add_widget(txt)

        if db_data.get('description'):
            add_section('【卦辞】', db_data['description'])
        if db_data.get('bai_hua'):
            add_section('【白话解释】', db_data['bai_hua'], dp(12))
        if db_data.get('guan_xiang'):
            add_section('【卦象分析】', db_data['guan_xiang'], dp(12))
        if db_data.get('ren_sheng'):
            add_section('【人生启示】', db_data['ren_sheng'], dp(12))

        if duangua_result:
            add_section('【断卦方法】', duangua_result['duan_gua_method'])

        # 爻辞
        yao_ci_list = gua_db.get_yao_ci(gua_name)
        if yao_ci_list:
            add_section('【爻辞详解】', '')
            for yao in yao_ci_list:
                yao_label = Label(
                    text=f"{yao['yao_name']}: {yao['yao_text']}",
                    size_hint_y=None,
                    halign='left', valign='top',
                    font_size=dp(13), color=T.COLOR_TEXT, padding=(8, 2),
                )
                yao_label.bind(size=yao_label.setter('text_size'))
                content.add_widget(yao_label)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        popup = Popup(
            title='',
            content=layout,
            size_hint=(0.95, 0.85),
            auto_dismiss=True,
            background_color=T.COLOR_BG,
        )

        close_btn = create_gold_button('关闭', font_size=dp(14), height=dp(44))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)

        popup.open()
    except Exception as e:
        logger.error(f'[Dialog] explanation error: {e}')
        show_toast('显示失败')


# ==================== 手动选卦弹窗 ====================

def show_manual_select_gua_popup(app):
    """手动选卦弹窗 —— 64卦列表 + 宫位筛选"""
    try:
        from gua_helpers import get_all_gua_with_palace, get_binary_from_name, gua_name_to_yao
        from ui_components import MiniGuaWidget

        all_gua = get_all_gua_with_palace()
        if not all_gua:
            show_toast('卦象数据加载失败')
            return

        popup_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        title = Label(
            text='选择卦象',
            size_hint_y=None,
            height=dp(36),
            font_size=dp(16),
            color=T.COLOR_GOLD,
            bold=True,
        )
        popup_layout.add_widget(title)

        # 宫位筛选
        palaces = ['全部', '乾宫', '坤宫', '震宫', '巽宫', '坎宫', '离宫', '艮宫', '兑宫']
        current_palace = ['全部']
        palace_scroll = ScrollView(size_hint_y=None, height=dp(34), do_scroll_x=True, do_scroll_y=False)
        palace_row = BoxLayout(orientation='horizontal', size_hint=(None, 1), spacing=dp(4),
                               width=dp(36) * len(palaces) + dp(16))
        palace_buttons = []

        for p in palaces:
            btn = Button(
                text=p,
                size_hint=(None, 1),
                width=dp(56),
                font_size=dp(11),
                color=T.COLOR_TEXT_SECOND,
                background_color=(0, 0, 0, 0),
                background_normal='',
            )
            apply_card_bg(btn)

            def on_palace(instance, palace_name=p):
                current_palace[0] = palace_name
                for pb in palace_buttons:
                    pb.canvas.before.clear()
                    if pb.text == palace_name:
                        apply_card_bg(pb)
                        # 高亮
                        with pb.canvas.before:
                            from kivy.graphics import Color, RoundedRectangle
                            Color(*T.COLOR_GOLD)
                            pb._bg_rect = RoundedRectangle(size=pb.size, pos=pb.pos, radius=T.BUTTON_RADIUS)
                            pb.bind(size=lambda *a: setattr(pb._bg_rect, 'size', pb.size))
                        pb.color = T.COLOR_BG
                    else:
                        apply_card_bg(pb)
                        pb.color = T.COLOR_TEXT_SECOND
                _update_gua_grid(grid, palace_name, all_gua, app, popup)

            btn.bind(on_press=on_palace)
            palace_buttons.append(btn)
            palace_row.add_widget(btn)

        palace_scroll.add_widget(palace_row)
        popup_layout.add_widget(palace_scroll)

        # 初始高亮"全部"
        palace_buttons[0].canvas.before.clear()
        with palace_buttons[0].canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*T.COLOR_GOLD)
            palace_buttons[0]._bg_rect = RoundedRectangle(
                size=palace_buttons[0].size, pos=palace_buttons[0].pos, radius=T.BUTTON_RADIUS)
        palace_buttons[0].color = T.COLOR_BG

        # 卦象网格
        grid_scroll = ScrollView()
        grid = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        grid_container = BoxLayout(orientation='vertical', spacing=dp(4))

        # 用 GridLayout 做 4 列
        grid_layout = GridLayout(cols=4, spacing=dp(4), size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        grid_container.add_widget(grid_layout)
        grid_scroll.add_widget(grid_container)
        popup_layout.add_widget(grid_scroll)

        popup = Popup(
            title='',
            content=popup_layout,
            size_hint=(0.95, 0.8),
            auto_dismiss=True,
            background_color=T.COLOR_BG,
        )

        # 初始填充
        _update_gua_grid(grid_layout, '全部', all_gua, app, popup)

        popup.open()
    except Exception as e:
        logger.error(f'[Dialog] manual_select error: {e}')
        show_toast('弹窗失败')


def _update_gua_grid(grid_layout, palace, all_gua, app, popup):
    """更新卦象网格"""
    grid_layout.clear_widgets()

    filtered = all_gua if palace == '全部' else [g for g in all_gua if g['palace'] == palace]

    from gua_helpers import get_binary_from_name, gua_name_to_yao
    from ui_components import MiniGuaWidget

    for gua in filtered:
        card = BoxLayout(orientation='vertical', spacing=dp(2), padding=dp(3))

        binary = get_binary_from_name(gua['name'])
        if binary:
            mini_gua = MiniGuaWidget(binary_str=binary, size_hint=(None, None), size=(dp(36), dp(32)))
            card.add_widget(mini_gua)

        name_label = Label(
            text=gua['name'],
            font_size=dp(9),
            color=T.COLOR_GOLD,
            halign='center',
        )
        card.add_widget(name_label)

        btn = Button(text='', background_color=(0, 0, 0, 0), background_normal='')
        apply_card_bg(btn)
        btn.add_widget(card)

        def on_gua(instance, g_name=gua['name']):
            try:
                if popup and hasattr(popup, 'dismiss'):
                    popup.dismiss()
            except Exception:
                pass
            yao_list = gua_name_to_yao(g_name)
            if yao_list:
                app.display_gua(yao_list, '手动选卦')
            else:
                show_toast(f'无法解析 {g_name}')

        btn.bind(on_press=on_gua)
        grid_layout.add_widget(btn)
