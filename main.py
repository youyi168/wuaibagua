#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 v2.0 - 模块化重构
深色玄学风 UI · 全新架构
"""

__version__ = '2.0.0'

# ==================== 全局异常处理 ====================
import sys
import traceback
import logging

def setup_global_exception_handler():
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.error(f"============= 全局异常 =============")
        logging.error(f"类型：{exc_type.__name__}")
        logging.error(f"信息：{exc_value}")
        logging.error(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    sys.excepthook = handle_exception
    try:
        import threading
        threading.excepthook = lambda args: handle_exception(args.exc_type, args.exc_value, args.exc_traceback)
    except Exception:
        pass

setup_global_exception_handler()
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger('wuaibagua')

# ==================== Vulkan 禁用（必须在 Kivy 导入前） ====================
import os
os.environ['KIVY_GL_BACKEND'] = 'gl'
os.environ['KIVY_NO_VULKAN'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy.config import Config
Config.set('graphics', 'backend', 'gl')
Config.set('graphics', 'vsync', '0')
Config.set('input', 'mouse', 'mouse,disable_multitouch,multitouch_on_demand')
Config.set('kivy', 'log_level', 'error')
Config.set('kivy', 'default_font',
    ['NotoSansSC', 'fonts/NotoSansSC-Regular.ttf', 'fonts/NotoSansSC-Regular.ttf',
     'fonts/NotoSansSC-Regular.ttf', 'fonts/NotoSansSC-Regular.ttf'])

# ==================== 标准导入 ====================
import random
import hashlib
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

# ==================== 导入新模块 ====================
import ui_theme as T
from ui_components import apply_card_bg, apply_gold_bg, create_gold_button, create_action_button, GuaSymbolWidget, MiniGuaWidget
from android_jni import init_android_clipboard, copy_to_clipboard, show_toast, get_device_id
from gua_helpers import get_gua_palace, get_all_gua_with_palace, get_binary_from_name, gua_name_to_yao, get_daily_gua

try:
    import gua_calculator
    GUA_CALC_AVAILABLE = True
except ImportError:
    GUA_CALC_AVAILABLE = False

# ==================== 主应用 ====================

class WuaibaguaApp(App):
    """我爱八卦 v2.0 主类"""

    def build(self):
        self.title = '我爱八卦'
        Window.clearcolor = T.COLOR_BG[:3]
        Clock.schedule_once(lambda dt: init_android_clipboard(), 0.5)

        # 注册字体
        from pathlib import Path
        font_path = Path(__file__).parent / 'fonts' / 'NotoSansSC-Regular.ttf'
        if font_path.exists():
            try:
                LabelBase.register(name='NotoSansSC', fn_regular=str(font_path))
            except Exception as e:
                logger.warning(f'[Font] 注册失败: {e}')

        # ========== 主布局 ==========
        main_layout = BoxLayout(orientation='vertical', padding=0, spacing=0)

        # 顶部标题栏
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(52), padding=(dp(16), dp(8)))
        with header.canvas.before:
            Color(*T.COLOR_BG_HEADER)
            header._bg_rect = RoundedRectangle(size=header.size, pos=header.pos)
            header.bind(size=lambda *a: setattr(header._bg_rect, 'size', header.size))
            header.bind(pos=lambda *a: setattr(header._bg_rect, 'pos', header.pos))

        header.add_widget(Label(text='我 爱 八 卦', font_size=dp(18), color=T.COLOR_GOLD, bold=True, letter_spacing=4))
        self.header_subtitle = Label(text='周易六十四卦 · 卜卦解惑', font_size=dp(10), color=T.COLOR_TEXT_SECOND, halign='right')
        header.add_widget(self.header_subtitle)
        main_layout.add_widget(header)

        # Tab 导航栏
        tab_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(42), padding=(dp(4), dp(4)), spacing=dp(4))
        with tab_bar.canvas.before:
            Color(*T.COLOR_BG_HEADER)
            tab_bar._bg_rect = RoundedRectangle(size=tab_bar.size, pos=tab_bar.pos)
            tab_bar.bind(size=lambda *a: setattr(tab_bar._bg_rect, 'size', tab_bar.size))
            tab_bar.bind(pos=lambda *a: setattr(tab_bar._bg_rect, 'pos', tab_bar.pos))

        self.tab_buttons = {}
        tab_defs = ['起卦', '64卦', '运势', '设置']

        for name in tab_defs:
            btn = Button(text=name, font_size=dp(12), color=T.COLOR_TEXT_SECOND,
                         background_color=(0, 0, 0, 0), background_normal='')
            with btn.canvas.before:
                Color(0, 0, 0, 0)
                btn._bg_rect = RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(8)] * 4)
                btn.bind(size=lambda *a, b=btn: setattr(b._bg_rect, 'size', b.size))
                btn.bind(pos=lambda *a, b=btn: setattr(b._bg_rect, 'pos', b.pos))
            self.tab_buttons[name] = btn
        main_layout.add_widget(tab_bar)

        # 内容容器
        self.content_container = BoxLayout(orientation='vertical')
        main_layout.add_widget(self.content_container)

        # 构建各 Tab
        self._tab_divination = self._build_divination_tab()
        self._tab_gua64 = self._build_gua64_tab()
        self._tab_fortune = self._build_fortune_tab()
        self._tab_settings = self._build_settings_tab()

        self._current_tab = '起卦'
        self.content_container.add_widget(self._tab_divination)

        # Tab 切换逻辑
        def switch_tab(name):
            for n, b in self.tab_buttons.items():
                b.canvas.before.clear()
                if n == name:
                    with b.canvas.before:
                        Color(*T.COLOR_GOLD)
                        b._bg_rect = RoundedRectangle(size=b.size, pos=b.pos, radius=[dp(8)] * 4)
                        b.bind(size=lambda *a, bb=b: setattr(bb._bg_rect, 'size', bb.size))
                        b.bind(pos=lambda *a, bb=b: setattr(bb._bg_rect, 'pos', bb.pos))
                    b.color = T.COLOR_BG
                    b.bold = True
                else:
                    with b.canvas.before:
                        Color(0, 0, 0, 0)
                        b._bg_rect = RoundedRectangle(size=b.size, pos=b.pos, radius=[dp(8)] * 4)
                        b.bind(size=lambda *a, bb=b: setattr(bb._bg_rect, 'size', bb.size))
                        b.bind(pos=lambda *a, bb=b: setattr(bb._bg_rect, 'pos', bb.pos))
                    b.color = T.COLOR_TEXT_SECOND
                    b.bold = False
            self._switch_content(name)

        for name in tab_defs:
            self.tab_buttons[name].bind(on_press=lambda x, n=name: switch_tab(n))

        # 激活起卦
        self.tab_buttons['起卦'].canvas.before.clear()
        with self.tab_buttons['起卦'].canvas.before:
            Color(*T.COLOR_GOLD)
            self.tab_buttons['起卦']._bg_rect = RoundedRectangle(
                size=self.tab_buttons['起卦'].size, pos=self.tab_buttons['起卦'].pos, radius=[dp(8)] * 4)
        self.tab_buttons['起卦'].color = T.COLOR_BG
        self.tab_buttons['起卦'].bold = True

        # 状态
        self.current_gua = None
        self.current_yao_list = None
        self.current_gua_detail = None
        self.current_changing_gua = None
        self.current_duangua_result = None

        return main_layout

    def _switch_content(self, name):
        tab_map = {'起卦': self._tab_divination, '64卦': self._tab_gua64, '运势': self._tab_fortune, '设置': self._tab_settings}
        sub_map = {'起卦': '周易六十四卦 · 卜卦解惑', '64卦': '快速查找 · 点击查看', '运势': '每日专属 · 趋吉避凶', '设置': '个性化 · 数据管理'}
        self.header_subtitle.text = sub_map.get(name, '')
        self.content_container.clear_widgets()
        w = tab_map.get(name)
        if w:
            self.content_container.add_widget(w)
        self._current_tab = name

    # ==================== 起卦 Tab ====================
    def _build_divination_tab(self):
        layout = BoxLayout(orientation='vertical', padding=(dp(10), dp(4), dp(10), dp(10)), spacing=dp(6), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # 卦象显示区
        self.gua_display_area = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(4))
        apply_card_bg(self.gua_display_area)

        self.empty_state = Label(text='☯', font_size=dp(48), color=T.COLOR_GOLD, halign='center', valign='middle',
                                  size_hint_y=None, height=dp(88))
        self.empty_hint = Label(text='选择起卦方式', font_size=dp(14), color=T.COLOR_TEXT_SECOND, halign='center',
                                 size_hint_y=None, height=dp(22))
        self.gua_display_area.add_widget(self.empty_state)
        self.gua_display_area.add_widget(self.empty_hint)

        # 结果状态
        self.result_state = BoxLayout(orientation='vertical', spacing=dp(3), padding=(dp(8), dp(4)))
        self.result_state.size_hint_y = None
        self.result_state.bind(minimum_height=self.result_state.setter('height'))

        self.gua_name_label = Label(text='', font_size=dp(24), color=T.COLOR_GOLD, bold=True, halign='center',
                                     size_hint_y=None, height=dp(32))
        self.result_state.add_widget(self.gua_name_label)

        self.gua_palace_label = Label(text='', font_size=dp(11), color=T.COLOR_TEXT_SECOND, halign='center',
                                       size_hint_y=None, height=dp(18))
        self.result_state.add_widget(self.gua_palace_label)

        self.yao_draw_area = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(110), spacing=dp(3), padding=(dp(30), dp(4)))
        self.result_state.add_widget(self.yao_draw_area)

        self.gua_ci_label = Label(text='', font_size=dp(12), color=T.COLOR_TEXT, halign='center',
                                   size_hint_y=None, height=dp(36))
        self.gua_ci_label.bind(size=self.gua_ci_label.setter('text_size'))
        self.result_state.add_widget(self.gua_ci_label)

        self.changing_label = Label(text='', font_size=dp(11), color=T.COLOR_GOLD, halign='center',
                                     size_hint_y=None, height=dp(20))
        self.result_state.add_widget(self.changing_label)
        layout.add_widget(self.gua_display_area)

        # 起卦方式 2x2
        method_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(150))
        for text, sub, method in [('随机起卦', '心诚则灵', 'auto'), ('手动选卦', '64卦列表', 'manual'),
                                   ('金钱起卦', '模拟摇卦', 'jinqian'), ('时间起卦', '以时起卦', 'time')]:
            card = self._create_method_card(text, sub)
            btn = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='')
            if method == 'auto': btn.bind(on_press=self.auto_gua)
            elif method == 'manual': btn.bind(on_press=self.manual_gua)
            elif method == 'jinqian': btn.bind(on_press=self.jinqian_gua)
            else: btn.bind(on_press=self.time_gua)
            card.add_widget(btn)
            method_grid.add_widget(card)
        layout.add_widget(method_grid)

        # 功能按钮（4个）
        quick_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
        for text, action in [('详解', self.show_explanation), ('六爻', self.show_liuyao),
                              ('问豆包', self.ask_doubao), ('分享', self.share_gua)]:
            btn = create_action_button(f' {text}', font_size=dp(11), height=dp(40))
            btn.bind(on_press=action)
            quick_row.add_widget(btn)
        layout.add_widget(quick_row)

        # 第二行按钮
        quick_row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
        for text, action in [('复制', self.copy_result), ('重新起卦', self.auto_gua)]:
            btn = create_action_button(f' {text}', font_size=dp(11), height=dp(40))
            btn.bind(on_press=action)
            quick_row2.add_widget(btn)
        layout.add_widget(quick_row2)

        return layout

    def _create_method_card(self, text, subtitle=None):
        """起卦方式卡片"""
        layout = BoxLayout(orientation='vertical', padding=(dp(12), dp(10)), spacing=dp(2),
                           size_hint_y=None, height=dp(70))
        apply_card_bg(layout)
        layout.add_widget(Label(text=text, font_size=dp(15), bold=True, color=T.COLOR_GOLD, size_hint_y=0.6))
        if subtitle:
            layout.add_widget(Label(text=subtitle, font_size=dp(11), color=T.COLOR_TEXT_SECOND, size_hint_y=0.4))
        else:
            layout.add_widget(Label(text='', size_hint_y=0.4))
        return layout

    # ==================== 64卦 Tab ====================
    def _build_gua64_tab(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # 搜索
        search_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
        self.gua64_search = TextInput(hint_text='搜索卦名...', font_size=dp(13), size_hint_x=1, multiline=False,
                                       background_color=T.COLOR_BG_CARD, foreground_color=T.COLOR_TEXT,
                                       hint_text_color=T.COLOR_TEXT_SECOND, cursor_color=T.COLOR_GOLD)
        self.gua64_search.bind(on_text_validate=lambda x: self._refresh_gua64_grid())
        search_box.add_widget(self.gua64_search)
        sbtn = create_gold_button('搜索', font_size=dp(12), height=dp(40), size_hint_x=None, width=dp(56))
        sbtn.bind(on_press=lambda x: self._refresh_gua64_grid())
        search_box.add_widget(sbtn)
        layout.add_widget(search_box)

        # 宫位筛选
        palaces = ['全部', '乾宫', '坤宫', '震宫', '巽宫', '坎宫', '离宫', '艮宫', '兑宫']
        self.gua64_palace = ['全部']
        palace_scroll = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(34), spacing=dp(4))
        self.gua64_palace_btns = []
        for p in palaces:
            btn = Button(text=p, size_hint_x=1, font_size=dp(11), color=T.COLOR_TEXT_SECOND,
                         background_color=(0, 0, 0, 0), background_normal='')
            apply_card_bg(btn)
            def on_palace(inst, pname=p):
                self.gua64_palace[0] = pname
                for pb in self.gua64_palace_btns:
                    pb.canvas.before.clear()
                    if pb.text == pname:
                        apply_card_bg(pb)
                        with pb.canvas.before:
                            Color(*T.COLOR_GOLD)
                            pb._bg_rect = RoundedRectangle(size=pb.size, pos=pb.pos, radius=[dp(8)] * 4)
                        pb.color = T.COLOR_BG
                    else:
                        apply_card_bg(pb)
                        pb.color = T.COLOR_TEXT_SECOND
                self._refresh_gua64_grid()
            btn.bind(on_press=on_palace)
            self.gua64_palace_btns.append(btn)
            palace_scroll.add_widget(btn)
        layout.add_widget(palace_scroll)

        # 初始高亮
        self.gua64_palace_btns[0].canvas.before.clear()
        apply_card_bg(self.gua64_palace_btns[0])
        with self.gua64_palace_btns[0].canvas.before:
            Color(*T.COLOR_GOLD)
            self.gua64_palace_btns[0]._bg_rect = RoundedRectangle(
                size=self.gua64_palace_btns[0].size, pos=self.gua64_palace_btns[0].pos, radius=[dp(8)] * 4)
        self.gua64_palace_btns[0].color = T.COLOR_BG

        # 网格
        self.gua64_grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=None, row_default_height=dp(60), row_force_default=True)
        self.gua64_grid.bind(minimum_height=self.gua64_grid.setter('height'))
        layout.add_widget(self.gua64_grid)

        self._all_gua_data = get_all_gua_with_palace()
        self._refresh_gua64_grid()
        return layout

    def _refresh_gua64_grid(self):
        self.gua64_grid.clear_widgets()
        query = self.gua64_search.text.strip().lower() if hasattr(self, 'gua64_search') else ''
        palace = self.gua64_palace[0] if hasattr(self, 'gua64_palace') else '全部'
        filtered = self._all_gua_data
        if palace != '全部': filtered = [g for g in filtered if g['palace'] == palace]
        if query: filtered = [g for g in filtered if query in g['name'].lower()]

        for gua in filtered:
            card = BoxLayout(orientation='vertical', spacing=dp(2), padding=dp(2))
            binary = get_binary_from_name(gua['name'])
            if binary:
                card.add_widget(MiniGuaWidget(binary_str=binary, size_hint=(None, None), size=(dp(32), dp(28))))
            card.add_widget(Label(text=gua['name'], font_size=dp(9), color=T.COLOR_GOLD, halign='center'))
            card.add_widget(Label(text=gua.get('palace', ''), font_size=dp(8), color=T.COLOR_TEXT_DIM, halign='center'))
            btn = Button(text='', background_color=(0, 0, 0, 0), background_normal='')
            apply_card_bg(btn)
            btn.add_widget(card)
            def on_detail(inst, gn=gua['name']): self._show_gua_detail_popup(gn)
            btn.bind(on_press=on_detail)
            self.gua64_grid.add_widget(btn)

    def _show_gua_detail_popup(self, gua_name):
        try:
            import gua_db
            db = gua_db.get_gua_by_name(gua_name)
            if not db:
                show_toast(f'未找到 {gua_name}')
                return
            popup_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
            popup_layout.add_widget(Label(text=f'☯ {gua_name}', size_hint_y=None, height=dp(32),
                                           font_size=dp(16), color=T.COLOR_GOLD, bold=True))
            info = f'宫位：{get_gua_palace(gua_name)}'
            if db.get('upper_gua') and db.get('lower_gua'): info += f'  上{db["upper_gua"]}下{db["lower_gua"]}'
            popup_layout.add_widget(Label(text=info, size_hint_y=None, height=dp(18), font_size=dp(11), color=T.COLOR_TEXT_SECOND))

            scroll = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
            scroll.bind(minimum_height=scroll.setter('height'))
            def add_sec(lt, dt):
                scroll.add_widget(Label(text=lt, size_hint_y=None, height=dp(22), font_size=dp(13), color=T.COLOR_GOLD, bold=True))
                txt = Label(text=dt, size_hint_y=None, halign='left', font_size=dp(12), color=T.COLOR_TEXT, padding=(6, 2))
                txt.bind(size=txt.setter('text_size'))
                scroll.add_widget(txt)
            if db.get('description'): add_sec('【卦辞】', db['description'])
            if db.get('bai_hua'): add_sec('【白话】', db['bai_hua'][:200])

            popup_layout.add_widget(scroll)

            qi_btn = create_gold_button('以此卦起卦', font_size=dp(13), height=dp(40))
            qi_btn.bind(on_press=lambda x, gn=gua_name: self._quick_divine(gn, popup))
            popup_layout.add_widget(qi_btn)

            close = Button(text='关闭', size_hint_y=None, height=dp(38), font_size=dp(13),
                           color=T.COLOR_TEXT_SECOND, background_color=(0, 0, 0, 0), background_normal='')
            close.bind(on_press=lambda x: popup.dismiss())
            popup_layout.add_widget(close)

            popup = Popup(title='', content=popup_layout, size_hint=(0.92, 0.75), auto_dismiss=True, background_color=T.COLOR_BG)
            popup.open()
        except Exception as e:
            logger.error(f'[Error] gua_detail: {e}')

    def _quick_divine(self, gua_name, popup):
        popup.dismiss()
        yl = gua_name_to_yao(gua_name)
        if yl:
            self._switch_content('起卦')
            for n, b in self.tab_buttons.items():
                b.canvas.before.clear()
                if n == '起卦':
                    apply_card_bg(b)
                    with b.canvas.before:
                        Color(*T.COLOR_GOLD)
                        b._bg_rect = RoundedRectangle(size=b.size, pos=b.pos, radius=[dp(8)] * 4)
                    b.color = T.COLOR_BG; b.bold = True
                else:
                    apply_card_bg(b); b.color = T.COLOR_TEXT_SECOND; b.bold = False
            self.display_gua(yl, '手动选卦')
        else:
            show_toast(f'无法解析 {gua_name}')

    # ==================== 运势 Tab（修复空白问题） ====================
    def _build_fortune_tab(self):
        layout = BoxLayout(orientation='vertical', padding=(dp(8), dp(4), dp(8), dp(8)), spacing=dp(6), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        today = datetime.now()
        layout.add_widget(Label(text=f'{today.year}年{today.month}月{today.day}日', font_size=dp(12),
                                 color=T.COLOR_TEXT_DIM, size_hint_y=None, height=dp(20), halign='center'))

        # 运势卡片 —— 关键修复：不设固定height，用minimum_height自适应
        self.fortune_card = BoxLayout(orientation='vertical', size_hint_y=None,
                                       padding=(dp(12), dp(8)), spacing=dp(4))
        self.fortune_card.bind(minimum_height=self.fortune_card.setter('height'))
        apply_card_bg(self.fortune_card)

        self.fortune_gua_name = Label(text='点击下方按钮查看今日运势', font_size=dp(18),
                                       color=T.COLOR_GOLD, bold=True, halign='center',
                                       size_hint_y=None, height=dp(28))
        self.fortune_card.add_widget(self.fortune_gua_name)

        self.fortune_yao_area = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(3), padding=(dp(15), dp(2)))
        self.fortune_yao_area.bind(minimum_height=self.fortune_yao_area.setter('height'))
        self.fortune_card.add_widget(self.fortune_yao_area)

        self.fortune_desc = Label(text='', font_size=dp(12), color=T.COLOR_TEXT_SECOND, halign='center', size_hint_y=None)
        self.fortune_desc.bind(size=self.fortune_desc.setter('text_size'))
        self.fortune_card.add_widget(self.fortune_desc)

        layout.add_widget(self.fortune_card)

        fbtn = create_gold_button('查看今日运势', font_size=dp(14), height=dp(46))
        fbtn.bind(on_press=self.daily_gua)
        layout.add_widget(fbtn)

        actions = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(38), spacing=dp(6))
        for text, action in [('详解', self.show_explanation), ('六爻', self.show_liuyao), ('分享', self.share_gua)]:
            btn = create_action_button(f' {text}', font_size=dp(11), height=dp(38))
            btn.bind(on_press=action)
            actions.add_widget(btn)
        layout.add_widget(actions)
        return layout

    def _update_fortune_display(self, gua_name, yao_list, changing_gua_name):
        if not hasattr(self, 'fortune_gua_name'): return
        self.fortune_gua_name.text = gua_name
        self.fortune_yao_area.clear_widgets()
        yao_names = ['上', '五', '四', '三', '二', '初']
        for i in range(6):
            yao = yao_list[5 - i]
            is_yang = yao in [7, 9]
            is_changing = yao in [6, 9]
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(14), spacing=dp(4))
            row.add_widget(Label(text=f'{yao_names[i]}', font_size=dp(9), color=T.COLOR_TEXT_DIM, size_hint_x=0.2))
            yw = Widget(size_hint_x=0.6)
            yc = T.COLOR_GOLD
            with yw.canvas:
                Color(*yc)
                if is_yang:
                    yw._rect = RoundedRectangle(pos=(0, dp(3)), size=(yw.width, dp(7)), radius=[dp(2)] * 4)
                else:
                    half = (yw.width - dp(6)) / 2
                    yw._rect1 = Rectangle(pos=(0, dp(3)), size=(half, dp(7)))
                    yw._rect2 = Rectangle(pos=(half + dp(6), dp(3)), size=(half, dp(7)))
            row.add_widget(yw)
            row.add_widget(Label(text='', size_hint_x=0.2))
            self.fortune_yao_area.add_widget(row)
        if self.current_gua_detail and self.current_gua_detail.get('bai_hua'):
            self.fortune_desc.text = self.current_gua_detail['bai_hua'][:80] + '...'
        else:
            self.fortune_desc.text = ''
        if changing_gua_name:
            self.fortune_desc.text += f'\n变卦：{changing_gua_name}'

    # ==================== 设置 Tab ====================
    def _build_settings_tab(self):
        layout = BoxLayout(orientation='vertical', padding=(dp(10), dp(4), dp(10), dp(10)), spacing=dp(8), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        vc = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), padding=(dp(20), dp(12)), spacing=dp(6))
        apply_card_bg(vc)
        vc.add_widget(Label(text='我 爱 八 卦', font_size=dp(20), color=T.COLOR_GOLD, bold=True, halign='center', size_hint_y=None, height=dp(26)))
        vc.add_widget(Label(text=f'v{__version__}  ·  周易六十四卦  ·  卜卦解惑', font_size=dp(11), color=T.COLOR_TEXT_SECOND, halign='center', size_hint_y=None, height=dp(18)))
        layout.add_widget(vc)

        sc = BoxLayout(orientation='vertical', size_hint_y=None, padding=(dp(15), dp(10)), spacing=dp(8))
        sc.bind(minimum_height=sc.setter('height'))
        apply_card_bg(sc)
        sc.add_widget(Label(text='功能选项', font_size=dp(14), color=T.COLOR_GOLD, bold=True, size_hint_y=None, height=dp(24)))

        from kivy.uix.switch import Switch
        for label_text in ['音效', '震动', '自动起卦']:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36), spacing=dp(10))
            row.add_widget(Label(text=label_text, font_size=dp(13), color=T.COLOR_TEXT))
            row.add_widget(Widget())
            row.add_widget(Switch(active=True, size_hint_x=None, width=dp(46)))
            sc.add_widget(row)

        for text, msg in [('问豆包 AI', '打开豆包对话'), ('检查更新', '当前已是最新版本')]:
            btn = create_gold_button(f' {text}', font_size=dp(13), height=dp(40))
            if text == '问豆包 AI':
                btn.bind(on_press=self.ask_doubao)
            else:
                btn.bind(on_press=lambda x: show_toast(f' {msg}'))
            sc.add_widget(btn)
        layout.add_widget(sc)

        fc = BoxLayout(orientation='vertical', size_hint_y=None, padding=(dp(15), dp(10)), spacing=dp(4))
        fc.bind(minimum_height=fc.setter('height'))
        apply_card_bg(fc)
        fc.add_widget(Label(text='功能列表', font_size=dp(14), color=T.COLOR_GOLD, bold=True, size_hint_y=None, height=dp(24)))
        for feat in ['随机起卦', '手动选卦', '金钱起卦', '时间起卦', '今日运势', '卦象详解', '六爻排盘', 'AI 问豆包']:
            fc.add_widget(Label(text=f' ☯ {feat}', font_size=dp(11), color=T.COLOR_TEXT, size_hint_y=None, height=dp(20)))
        layout.add_widget(fc)
        return layout

    # ==================== 起卦逻辑 ====================
    def auto_gua(self, inst): self.display_gua([random.randint(6, 9) for _ in range(6)], '电脑起卦')
    def manual_gua(self, inst): self._show_manual_select()
    def daily_gua(self, inst): self.display_gua(get_daily_gua(), '今日运势')
    def jinqian_gua(self, inst):
        try:
            self.display_gua(gua_calculator.jinqian_qigua(), '金钱起卦')
        except Exception as e:
            logger.error(f'[Error] jinqian: {e}'); show_toast('金钱起卦失败')
    def time_gua(self, inst):
        try:
            now = datetime.now()
            self.display_gua(gua_calculator.time_qigua(now.year, now.month, now.day, now.hour, now.minute), '时间起卦')
        except Exception as e:
            logger.error(f'[Error] time: {e}'); show_toast('时间起卦失败')

    # ==================== 手动选卦弹窗 ====================
    def _show_manual_select(self):
        try:
            all_gua = get_all_gua_with_palace()
            if not all_gua: show_toast('卦象数据加载失败'); return

            popup_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
            popup_layout.add_widget(Label(text='选择卦象', size_hint_y=None, height=dp(36), font_size=dp(16), color=T.COLOR_GOLD, bold=True))

            palaces = ['全部', '乾宫', '坤宫', '震宫', '巽宫', '坎宫', '离宫', '艮宫', '兑宫']
            current = ['全部']
            palace_scroll = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(34), spacing=dp(4))
            palace_btns = []
            for p in palaces:
                btn = Button(text=p, size_hint_x=1, font_size=dp(11), color=T.COLOR_TEXT_SECOND,
                             background_color=(0, 0, 0, 0), background_normal='')
                apply_card_bg(btn)
                def on_p(inst, pn=p):
                    current[0] = pn
                    for pb in palace_btns:
                        pb.canvas.before.clear()
                        if pb.text == pn:
                            apply_card_bg(pb)
                            with pb.canvas.before:
                                Color(*T.COLOR_GOLD)
                                pb._bg_rect = RoundedRectangle(size=pb.size, pos=pb.pos, radius=[dp(8)] * 4)
                            pb.color = T.COLOR_BG
                        else:
                            apply_card_bg(pb); pb.color = T.COLOR_TEXT_SECOND
                    _refresh_grid(pn)
                btn.bind(on_press=on_p)
                palace_btns.append(btn)
                palace_scroll.add_widget(btn)
            popup_layout.add_widget(palace_scroll)
            palace_btns[0].canvas.before.clear(); apply_card_bg(palace_btns[0])
            with palace_btns[0].canvas.before:
                Color(*T.COLOR_GOLD)
                palace_btns[0]._bg_rect = RoundedRectangle(size=palace_btns[0].size, pos=palace_btns[0].pos, radius=[dp(8)] * 4)
            palace_btns[0].color = T.COLOR_BG

            grid_layout = GridLayout(cols=4, spacing=dp(4), size_hint_y=None)
            grid_layout.bind(minimum_height=grid_layout.setter('height'))

            def _refresh_grid(palace):
                grid_layout.clear_widgets()
                fl = all_gua if palace == '全部' else [g for g in all_gua if g['palace'] == palace]
                for gua in fl:
                    card = BoxLayout(orientation='vertical', spacing=dp(2), padding=dp(2))
                    binary = get_binary_from_name(gua['name'])
                    if binary: card.add_widget(MiniGuaWidget(binary_str=binary, size_hint=(None, None), size=(dp(36), dp(32))))
                    card.add_widget(Label(text=gua['name'], font_size=dp(9), color=T.COLOR_GOLD, halign='center'))
                    btn = Button(text='', background_color=(0, 0, 0, 0), background_normal='')
                    apply_card_bg(btn); btn.add_widget(card)
                    def on_g(inst, gn=gua['name']):
                        popup.dismiss()
                        yl = gua_name_to_yao(gn)
                        if yl: self.display_gua(yl, '手动选卦')
                        else: show_toast(f'无法解析 {gn}')
                    btn.bind(on_press=on_g)
                    grid_layout.add_widget(btn)

            _refresh_grid('全部')
            popup_layout.add_widget(grid_layout)

            popup = Popup(title='', content=popup_layout, size_hint=(0.95, 0.8), auto_dismiss=True, background_color=T.COLOR_BG)
            popup.open()
        except Exception as e:
            logger.error(f'[Error] manual_select: {e}'); show_toast('弹窗失败')

    # ==================== 卦象显示 ====================
    def display_gua(self, yao_list, method):
        try:
            if GUA_CALC_AVAILABLE:
                text, gua_name, changing_gua_name, image_info = gua_calculator.format_gua_display(yao_list, method)
                self.current_changing_gua = changing_gua_name
            else:
                gua_name = '未知卦'; self.current_changing_gua = None

            self.current_gua = gua_name
            self.current_yao_list = yao_list
            self.current_gua_detail = None
            self.current_duangua_result = None
            if GUA_CALC_AVAILABLE:
                self.current_gua_detail = gua_calculator.get_gua_detail(gua_name)
                self.current_duangua_result = gua_calculator.duangua_logic(yao_list)

            self._show_gua_result(gua_name, yao_list, changing_gua_name if GUA_CALC_AVAILABLE else None)
            self._update_fortune_display(gua_name, yao_list, changing_gua_name if GUA_CALC_AVAILABLE else None)
            show_toast(f' {gua_name}')
        except Exception as e:
            logger.error(f'[Error] display_gua: {e}'); show_toast('显示失败')

    def _show_gua_result(self, gua_name, yao_list, changing_gua_name):
        if not hasattr(self, 'empty_state'): return
        if self.empty_state.parent: self.gua_display_area.remove_widget(self.empty_state)
        if self.empty_hint.parent: self.gua_display_area.remove_widget(self.empty_hint)
        if not self.result_state.parent:
            self.gua_display_area.add_widget(self.result_state, index=0)
            Clock.schedule_once(lambda dt: setattr(self.gua_display_area, 'height', self.result_state.minimum_height + dp(4)), 0)

        self.gua_name_label.text = gua_name
        self.gua_palace_label.text = get_gua_palace(gua_name) or ''

        self.yao_draw_area.clear_widgets()
        yao_names = ['上', '五', '四', '三', '二', '初']
        for i in range(6):
            yao = yao_list[5 - i]
            is_yang = yao in [7, 9]
            is_changing = yao in [6, 9]
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(16), spacing=dp(4))
            row.add_widget(Label(text=f'{yao_names[i]}', font_size=dp(10), color=T.COLOR_TEXT_SECOND, size_hint_x=0.15))
            yw = Widget(size_hint_x=0.7)
            yc = T.COLOR_GOLD if not is_changing else T.COLOR_GOLD
            with yw.canvas:
                Color(*yc)
                if is_yang:
                    yw._rect = RoundedRectangle(pos=(0, dp(4)), size=(yw.width, dp(7)), radius=[dp(2)] * 4)
                else:
                    half = (yw.width - dp(6)) / 2
                    yw._rect1 = Rectangle(pos=(0, dp(4)), size=(half, dp(7)))
                    yw._rect2 = Rectangle(pos=(half + dp(6), dp(4)), size=(half, dp(7)))
            row.add_widget(yw)
            row.add_widget(Label(text='', size_hint_x=0.15))
            self.yao_draw_area.add_widget(row)

        if self.current_gua_detail and self.current_gua_detail.get('gua_ci'):
            self.gua_ci_label.text = self.current_gua_detail['gua_ci'][:60]
        else:
            self.gua_ci_label.text = ''
        self.changing_label.text = f'变卦：{changing_gua_name}' if changing_gua_name else ''

    # ==================== 功能按钮 ====================
    def show_explanation(self, inst):
        if not self.current_gua: show_toast('请先起卦'); return
        try:
            import gua_db
            show_gua_explanation_popup(self.current_gua, self.current_gua_detail, self.current_yao_list,
                                        self.current_changing_gua, self.current_duangua_result)
        except Exception as e:
            logger.error(f'[Error] explanation: {e}'); show_toast('显示失败')

    def show_liuyao(self, inst):
        if not self.current_gua: show_toast('请先起卦'); return
        try:
            from liuyao_paipan import format_liuyao_full
            text = format_liuyao_full(self.current_yao_list, self.current_gua)
            show_liuyao_popup_v2(text)
        except Exception as e:
            logger.error(f'[Error] liuyao: {e}'); show_toast('排盘失败')

    def share_gua(self, inst):
        if not self.current_gua: show_toast('请先起卦'); return
        text = f'【{self.current_gua}】\n\n'
        if self.current_yao_list:
            yn = ['初', '二', '三', '四', '五', '上']
            for i in range(5, -1, -1):
                y = self.current_yao_list[i]
                text += f'{yn[i]}{"阳" if y in [7,9] else "阴"}{" " if y==9 else " " if y==6 else ""}\n'
        if self.current_changing_gua: text += f'\n变卦：{self.current_changing_gua}'
        show_share_popup_v2(text)

    def copy_result(self, inst):
        if not self.current_gua: show_toast('请先起卦'); return
        text = f'【{self.current_gua}】\n'
        if self.current_yao_list:
            yn = ['初', '二', '三', '四', '五', '上']
            for i in range(5, -1, -1):
                y = self.current_yao_list[i]
                text += f'{yn[i]}{"阳" if y in [7,9] else "阴"}{" " if y==9 else " " if y==6 else ""}\n'
        if self.current_changing_gua: text += f'\n变卦：{self.current_changing_gua}'
        copy_to_clipboard(text); show_toast('已复制')

    def ask_doubao(self, inst):
        """询问豆包 AI"""
        if not self.current_gua: show_toast('请先起卦'); return
        try:
            import webbrowser
            import urllib.parse
            q = f'我起了一卦：{self.current_gua}\n'
            if self.current_yao_list:
                yn = ['初', '二', '三', '四', '五', '上']
                parts = []
                for i in range(6):
                    y = self.current_yao_list[i]
                    parts.append(f'{yn[i]}{"阳" if y in [7,9] else "阴"}{"（变）" if y in [6,9] else ""}')
                q += f'爻象：{", ".join(parts)}\n'
            if self.current_changing_gua: q += f'变卦：{self.current_changing_gua}\n'
            if self.current_gua_detail and self.current_gua_detail.get('bai_hua'):
                q += f'解释：{self.current_gua_detail["bai_hua"][:80]}\n'
            q += '\n请帮我详细解读这个卦象，分析吉凶运势。'
            encoded = urllib.parse.quote(q)
            url = f'https://www.doubao.com/chat/url-action?action={{"pluginId":"Send_Message","payload":{{"text":"{encoded}"}}}}'
            webbrowser.open(url); show_toast('正在打开豆包...')
        except Exception as e:
            logger.error(f'[Error] ask_doubao: {e}'); show_toast('打开豆包失败')


# ==================== 弹窗函数（内联） ====================

def show_gua_explanation_popup(gua_name, detail_data, yao_list=None, changing_gua_name=None, duangua_result=None):
    try:
        import gua_db
        db = gua_db.get_gua_by_name(gua_name)
        if not db: show_toast(f'未找到 {gua_name}'); return
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        layout.add_widget(Label(text=f'【{gua_name}】详解', size_hint_y=None, height=dp(32), font_size=dp(15), color=T.COLOR_GOLD, bold=True))
        scroll = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        scroll.bind(minimum_height=scroll.setter('height'))
        def add_sec(lt, dt):
            scroll.add_widget(Label(text=lt, size_hint_y=None, height=dp(22), font_size=dp(13), color=T.COLOR_GOLD, bold=True))
            txt = Label(text=dt, size_hint_y=None, halign='left', font_size=dp(12), color=T.COLOR_TEXT, padding=(6, 2))
            txt.bind(size=txt.setter('text_size')); scroll.add_widget(txt)
        if db.get('description'): add_sec('【卦辞】', db['description'])
        if db.get('bai_hua'): add_sec('【白话】', db['bai_hua'])
        if db.get('guan_xiang'): add_sec('【卦象】', db['guan_xiang'])
        if duangua_result: add_sec('【断卦】', duangua_result.get('duan_gua_method', ''))
        layout.add_widget(scroll)
        popup = Popup(title='', content=layout, size_hint=(0.95, 0.85), auto_dismiss=True, background_color=T.COLOR_BG)
        cb = Button(text='关闭', size_hint_y=None, height=dp(40), font_size=dp(14), color=T.COLOR_TEXT_SECOND, background_color=(0,0,0,0), background_normal='')
        cb.bind(on_press=lambda x: popup.dismiss()); layout.add_widget(cb)
        popup.open()
    except Exception as e:
        logger.error(f'[Error] explanation popup: {e}'); show_toast('显示失败')


def show_liuyao_popup_v2(text):
    layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
    layout.add_widget(Label(text='六 爻 排 盘', size_hint_y=None, height=dp(32), font_size=dp(15), color=T.COLOR_GOLD, bold=True))
    content = Label(text=text, markup=True, size_hint_y=None, halign='left', valign='top', font_size=dp(11), color=T.COLOR_TEXT, padding=(dp(6), dp(4)))
    content.bind(size=content.setter('text_size')); content.bind(texture_size=lambda *a: setattr(content, 'height', content.texture_size[1]))
    layout.add_widget(content)
    popup = Popup(title='', content=layout, size_hint=(0.95, 0.85), auto_dismiss=True, background_color=T.COLOR_BG)
    cb = create_gold_button('关闭', font_size=dp(13), height=dp(40))
    cb.bind(on_press=lambda x: popup.dismiss()); layout.add_widget(cb)
    popup.open()


def show_share_popup_v2(text):
    layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
    layout.add_widget(Label(text='选择分享方式', size_hint_y=None, height=dp(36), font_size=dp(15), color=T.COLOR_GOLD, bold=True))
    popup = None
    def do_copy(): copy_to_clipboard(text); popup.dismiss(); show_toast('已复制')
    def do_share(platform): copy_to_clipboard(text); popup.dismiss(); show_toast(f'已复制，请打开{platform}粘贴')
    for name, cb in [('复制文本', do_copy), ('分享到微信', lambda: do_share('微信')), ('分享到 QQ', lambda: do_share('QQ'))]:
        btn = create_gold_button(f' {name}', font_size=dp(14), height=dp(42))
        btn.bind(on_press=lambda x, c=cb: c()); layout.add_widget(btn)
    cancel = Button(text='取消', size_hint_y=None, height=dp(40), font_size=dp(14), color=T.COLOR_TEXT_SECOND, background_color=(0,0,0,0), background_normal='')
    cancel.bind(on_press=lambda x: popup.dismiss()); layout.add_widget(cancel)
    popup = Popup(title='', content=layout, size_hint=(0.85, 0.5), auto_dismiss=False, background_color=T.COLOR_BG)
    popup.open()


if __name__ == '__main__':
    WuaibaguaApp().run()
