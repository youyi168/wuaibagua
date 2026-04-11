#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六十四卦 Tab 模块（v2 风格）
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
import ui_theme as T
from ui_components import apply_card_bg, create_gold_button, MiniGuaWidget
from gua_helpers import get_all_gua_with_palace, get_binary_from_name, gua_name_to_yao
from android_jni import show_toast


def build_gua64_tab(app):
    """构建六十四卦 Tab"""
    layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8), size_hint_y=None)
    layout.bind(minimum_height=layout.setter('height'))

    # 搜索框
    search_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
    app.gua64_search = TextInput(
        hint_text='搜索卦名...',
        font_size=dp(13),
        size_hint_x=1,
        multiline=False,
        background_color=T.COLOR_BG_CARD,
        foreground_color=T.COLOR_TEXT,
        hint_text_color=T.COLOR_TEXT_SECOND,
        cursor_color=T.COLOR_GOLD,
    )
    app.gua64_search.bind(on_text_validate=lambda x: app._refresh_gua64_grid())
    search_box.add_widget(app.gua64_search)

    search_btn = create_gold_button('搜索', font_size=dp(12), height=dp(40), size_hint_x=None, width=dp(56))
    search_btn.bind(on_press=lambda x: app._refresh_gua64_grid())
    search_box.add_widget(search_btn)
    layout.add_widget(search_box)

    # 宫位筛选
    palaces = ['全部', '乾宫', '坤宫', '震宫', '巽宫', '坎宫', '离宫', '艮宫', '兑宫']
    app.gua64_palace = ['全部']

    palace_scroll = ScrollView(size_hint_y=None, height=dp(34), do_scroll_x=True, do_scroll_y=False)
    palace_row = BoxLayout(orientation='horizontal', size_hint=(None, 1), spacing=dp(4),
                           width=dp(36) * len(palaces) + dp(16))
    app.gua64_palace_btns = []

    for p in palaces:
        btn = Button(
            text=p, size_hint=(None, 1), width=dp(56),
            font_size=dp(11), color=T.COLOR_TEXT_SECOND,
            background_color=(0, 0, 0, 0), background_normal='',
        )
        apply_card_bg(btn)

        def on_palace(instance, palace_name=p):
            app.gua64_palace[0] = palace_name
            for pb in app.gua64_palace_btns:
                pb.canvas.before.clear()
                if pb.text == palace_name:
                    apply_card_bg(pb)
                    from kivy.graphics import Color, RoundedRectangle
                    with pb.canvas.before:
                        Color(*T.COLOR_GOLD)
                        pb._bg_rect = RoundedRectangle(size=pb.size, pos=pb.pos, radius=T.BUTTON_RADIUS)
                    pb.color = T.COLOR_BG
                else:
                    apply_card_bg(pb)
                    pb.color = T.COLOR_TEXT_SECOND
            app._refresh_gua64_grid()

        btn.bind(on_press=on_palace)
        app.gua64_palace_btns.append(btn)
        palace_row.add_widget(btn)

    palace_scroll.add_widget(palace_row)
    layout.add_widget(palace_scroll)

    # 初始高亮"全部"
    app.gua64_palace_btns[0].canvas.before.clear()
    from kivy.graphics import Color, RoundedRectangle
    with app.gua64_palace_btns[0].canvas.before:
        Color(*T.COLOR_GOLD)
        app.gua64_palace_btns[0]._bg_rect = RoundedRectangle(
            size=app.gua64_palace_btns[0].size, pos=app.gua64_palace_btns[0].pos, radius=T.BUTTON_RADIUS)
    app.gua64_palace_btns[0].color = T.COLOR_BG

    # 卦象网格
    app.gua64_grid = GridLayout(
        cols=4, spacing=dp(4), size_hint_y=None,
        row_default_height=dp(60),
        row_force_default=True,
    )
    app.gua64_grid.bind(minimum_height=app.gua64_grid.setter('height'))
    layout.add_widget(app.gua64_grid)

    # 加载数据
    app._all_gua_data = get_all_gua_with_palace()
    app._refresh_gua64_grid()

    return layout


def refresh_gua64_grid(app):
    """刷新 64 卦网格"""
    app.gua64_grid.clear_widgets()

    query = app.gua64_search.text.strip().lower() if hasattr(app, 'gua64_search') else ''
    palace = app.gua64_palace[0] if hasattr(app, 'gua64_palace') else '全部'

    filtered = app._all_gua_data
    if palace != '全部':
        filtered = [g for g in filtered if g['palace'] == palace]
    if query:
        filtered = [g for g in filtered if query in g['name'].lower()]

    for gua in filtered:
        card = BoxLayout(orientation='vertical', spacing=dp(2), padding=dp(2))

        binary = get_binary_from_name(gua['name'])
        if binary:
            mini_gua = MiniGuaWidget(binary_str=binary, size_hint=(None, None), size=(dp(32), dp(28)))
            card.add_widget(mini_gua)

        name_label = Label(
            text=gua['name'], font_size=dp(9), color=T.COLOR_GOLD, halign='center',
        )
        card.add_widget(name_label)

        palace_label = Label(
            text=gua.get('palace', ''), font_size=dp(8), color=T.COLOR_TEXT_DIM, halign='center',
        )
        card.add_widget(palace_label)

        btn = Button(text='', background_color=(0, 0, 0, 0), background_normal='')
        apply_card_bg(btn)
        btn.add_widget(card)

        def on_detail(instance, g_name=gua['name']):
            _show_gua_detail_popup(app, g_name)

        btn.bind(on_press=on_detail)
        app.gua64_grid.add_widget(btn)


def _show_gua_detail_popup(app, gua_name):
    """卦象详情弹窗"""
    try:
        import gua_db
        db_data = gua_db.get_gua_by_name(gua_name)
        if not db_data:
            show_toast(f'未找到 {gua_name}')
            return

        popup_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        title = Label(
            text=f'☯ {gua_name}',
            size_hint_y=None, height=dp(32),
            font_size=dp(16), color=T.COLOR_GOLD, bold=True,
        )
        popup_layout.add_widget(title)

        from gua_helpers import get_gua_palace
        palace = get_gua_palace(gua_name)
        info = f'宫位：{palace}'
        if db_data.get('upper_gua') and db_data.get('lower_gua'):
            info += f'  上{db_data["upper_gua"]}下{db_data["lower_gua"]}'
        info_label = Label(
            text=info, size_hint_y=None, height=dp(20),
            font_size=dp(11), color=T.COLOR_TEXT_SECOND,
        )
        popup_layout.add_widget(info_label)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        content.bind(minimum_height=content.setter('height'))

        def add_sec(label_text, detail_text):
            sec = Label(text=label_text, size_hint_y=None, height=dp(22), font_size=dp(13), color=T.COLOR_GOLD, bold=True)
            content.add_widget(sec)
            txt = Label(text=detail_text, size_hint_y=None, halign='left', font_size=dp(12), color=T.COLOR_TEXT, padding=(6, 2))
            txt.bind(size=txt.setter('text_size'))
            content.add_widget(txt)

        if db_data.get('description'):
            add_sec('【卦辞】', db_data['description'])
        if db_data.get('bai_hua'):
            add_sec('【白话】', db_data['bai_hua'][:200])
        if db_data.get('guan_xiang'):
            add_sec('【卦象】', db_data['guan_xiang'][:200])

        scroll.add_widget(content)
        popup_layout.add_widget(scroll)

        # 快速起卦
        qi_btn = create_gold_button(f'以此卦起卦', font_size=dp(13), height=dp(40))
        qi_btn.bind(on_press=lambda x, gn=gua_name: _quick_divine(app, gn, popup))
        popup_layout.add_widget(qi_btn)

        close_btn = Button(
            text='关闭', size_hint_y=None, height=dp(38),
            font_size=dp(13), color=T.COLOR_TEXT_SECOND,
            background_color=(0, 0, 0, 0), background_normal='',
        )
        close_btn.bind(on_press=lambda x: popup.dismiss())
        popup_layout.add_widget(close_btn)

        popup = Popup(
            title='', content=popup_layout,
            size_hint=(0.92, 0.75),
            auto_dismiss=True, background_color=T.COLOR_BG,
        )
        popup.open()
    except Exception as e:
        print(f'[Error] gua_detail: {e}')


def _quick_divine(app, gua_name, popup):
    """从速查快速起卦"""
    popup.dismiss()
    yao_list = gua_name_to_yao(gua_name)
    if yao_list:
        app._switch_content('起卦')
        # 切换 Tab 按钮状态
        for n, b in app.tab_buttons.items():
            b.canvas.before.clear()
            if n == '起卦':
                from kivy.graphics import Color, RoundedRectangle
                with b.canvas.before:
                    Color(*T.COLOR_GOLD)
                    b._bg_rect = RoundedRectangle(size=b.size, pos=b.pos, radius=T.BUTTON_RADIUS)
                b.color = T.COLOR_BG
                b.bold = True
            else:
                apply_card_bg(b)
                b.color = T.COLOR_TEXT_SECOND
                b.bold = False
        app.display_gua(yao_list, '手动选卦')
    else:
        show_toast(f'无法解析 {gua_name}')
