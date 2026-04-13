#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 v2.0.1 - 功能修复版
深色玄学风 UI · 模块化重构
修复：爻符可见/按钮可见/Tab滚动/弹窗闭包/宫位映射
"""

__version__ = '2.0.1'

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
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle

# ==================== 导入模块 ====================
import ui_theme as T
from ui_components import apply_card_bg, apply_gold_bg, create_gold_button, GuaSymbolWidget, MiniGuaWidget
from android_jni import init_android_clipboard, copy_to_clipboard, show_toast, get_device_id
from gua_helpers import get_gua_palace, get_all_gua_with_palace, get_binary_from_name, gua_name_to_yao, get_daily_gua

try:
    import gua_calculator
    GUA_CALC_AVAILABLE = True
except ImportError:
    GUA_CALC_AVAILABLE = False


# ==================== UI 辅助函数 ====================

def create_action_btn(text, fs=None, h=None, on_press=None, **kw):
    """功能按钮——浅色半透明背景，深色背景下可见"""
    btn = Button(text=text, font_size=fs or dp(12), size_hint_y=None, height=h or dp(40),
                 color=T.COLOR_GOLD, background_color=(0, 0, 0, 0), background_normal='', **kw)
    with btn.canvas.before:
        Color(0.22, 0.22, 0.36, 0.9)
        btn._bg = RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(10)] * 4)
        btn.bind(size=lambda *a: setattr(btn._bg, 'size', btn.size))
        btn.bind(pos=lambda *a: setattr(btn._bg, 'pos', btn.pos))
    if on_press:
        btn.bind(on_press=on_press)
    return btn


def make_yao_row(yao_type, label_text, label_color=None):
    """创建单行爻符（Canvas绘制，绑定size变化自动重绘）"""
    row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(16), spacing=dp(4))
    row.add_widget(Label(text=label_text, font_size=dp(10),
                          color=label_color or T.COLOR_TEXT_SECOND, size_hint_x=0.15))

    is_yang = yao_type in [7, 9]
    is_changing = yao_type in [6, 9]

    # 修复：Widget 必须设置 size_hint_y=None 和 height，否则 canvas 绘制区域为 0
    yw = Widget(size_hint=(0.7, None), height=dp(16))
    yc = T.COLOR_GOLD_FAINT if is_changing else T.COLOR_GOLD

    def redraw_wy(*args):
        yw.canvas.clear()
        w = yw.width
        h = yw.height
        if w < 1 or h < 1:
            return
        # 修复：爻符居中绘制
        cy = (h - dp(7)) / 2
        with yw.canvas:
            Color(*yc)
            if is_yang:
                RoundedRectangle(pos=(0, cy), size=(w, dp(7)), radius=[dp(2)] * 4)
            else:
                half = (w - dp(6)) / 2
                Rectangle(pos=(0, cy), size=(half, dp(7)))
                Rectangle(pos=(half + dp(6), cy), size=(half, dp(7)))

    yw.bind(size=redraw_wy)
    row.add_widget(yw)
    row.add_widget(Label(text='', size_hint_x=0.15))
    return row


def make_yao_row_fortune(yao_type, label_text):
    """运势Tab用的爻符行"""
    row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(14), spacing=dp(4))
    row.add_widget(Label(text=label_text, font_size=dp(9), color=T.COLOR_TEXT_DIM, size_hint_x=0.2))

    is_yang = yao_type in [7, 9]
    is_changing = yao_type in [6, 9]
    yc = T.COLOR_GOLD_FAINT if is_changing else T.COLOR_GOLD

    # 修复：Widget 必须设置 size_hint_y=None 和 height
    yw = Widget(size_hint=(0.6, None), height=dp(14))

    def redraw(*args):
        yw.canvas.clear()
        w = yw.width
        h = yw.height
        if w < 1 or h < 1:
            return
        cy = (h - dp(7)) / 2
        with yw.canvas:
            Color(*yc)
            if is_yang:
                RoundedRectangle(pos=(0, cy), size=(w, dp(7)), radius=[dp(2)] * 4)
            else:
                half = (w - dp(6)) / 2
                Rectangle(pos=(0, cy), size=(half, dp(7)))
                Rectangle(pos=(half + dp(6), cy), size=(half, dp(7)))

    yw.bind(size=redraw)
    row.add_widget(yw)
    row.add_widget(Label(text='', size_hint_x=0.2))
    return row


# ==================== 主应用 ====================

class WuaibaguaApp(App):
    """我爱八卦 v2.0.1 主类"""

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

        # 标题栏
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(52), padding=(dp(16), dp(8)))
        with header.canvas.before:
            Color(*T.COLOR_BG_HEADER)
            header._bg = RoundedRectangle(size=header.size, pos=header.pos)
            header.bind(size=lambda *a: setattr(header._bg, 'size', header.size))
            header.bind(pos=lambda *a: setattr(header._bg, 'pos', header.pos))
        header.add_widget(Label(text='我爱八卦', font_size=dp(18), color=T.COLOR_GOLD, bold=True))
        self.header_sub = Label(text='周易六十四卦 · 卜卦解惑', font_size=dp(10), color=T.COLOR_TEXT_SECOND, halign='right')
        header.add_widget(self.header_sub)
        main_layout.add_widget(header)

        # Tab栏
        tab_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(42), padding=(dp(4), dp(4)), spacing=dp(4))
        with tab_bar.canvas.before:
            Color(*T.COLOR_BG_HEADER)
            tab_bar._bg = RoundedRectangle(size=tab_bar.size, pos=tab_bar.pos)
            tab_bar.bind(size=lambda *a: setattr(tab_bar._bg, 'size', tab_bar.size))
            tab_bar.bind(pos=lambda *a: setattr(tab_bar._bg, 'pos', tab_bar.pos))

        self.tab_btns = {}
        for name in ['起卦', '64卦', '运势', '设置']:
            btn = Button(text=name, font_size=dp(12), color=T.COLOR_TEXT_SECOND,
                         background_color=(0, 0, 0, 0), background_normal='')
            with btn.canvas.before:
                Color(0, 0, 0, 0)
                btn._bg = RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(8)] * 4)
                btn.bind(size=lambda *a, b=btn: setattr(b._bg, 'size', b.size))
                btn.bind(pos=lambda *a, b=btn: setattr(b._bg, 'pos', b.pos))
            self.tab_btns[name] = btn
        main_layout.add_widget(tab_bar)

        # 内容容器（用 ScrollView 包裹，支持滚动）
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        main_layout.add_widget(self.scroll)

        # 构建各 Tab
        self._tab_div = self._build_div_tab()
        self._tab_64 = self._build_64_tab()
        self._tab_fortune = self._build_fortune_tab()
        self._tab_settings = self._build_settings_tab()

        self._cur_tab = '起卦'
        self.content.add_widget(self._tab_div)

        # Tab切换
        def switch(name):
            for n, b in self.tab_btns.items():
                b.canvas.before.clear()
                if n == name:
                    with b.canvas.before:
                        Color(*T.COLOR_GOLD)
                        b._bg = RoundedRectangle(size=b.size, pos=b.pos, radius=[dp(8)] * 4)
                        b.bind(size=lambda *a, bb=b: setattr(bb._bg, 'size', bb.size))
                        b.bind(pos=lambda *a, bb=b: setattr(bb._bg, 'pos', bb.pos))
                    b.color = T.COLOR_BG; b.bold = True
                else:
                    with b.canvas.before:
                        Color(0, 0, 0, 0)
                        b._bg = RoundedRectangle(size=b.size, pos=b.pos, radius=[dp(8)] * 4)
                        b.bind(size=lambda *a, bb=b: setattr(bb._bg, 'size', bb.size))
                        b.bind(pos=lambda *a, bb=b: setattr(bb._bg, 'pos', bb.pos))
                    b.color = T.COLOR_TEXT_SECOND; b.bold = False
            self._switch(name)

        for name in ['起卦', '64卦', '运势', '设置']:
            self.tab_btns[name].bind(on_press=lambda x, n=name: switch(n))

        # 激活起卦
        b = self.tab_btns['起卦']
        b.canvas.before.clear()
        with b.canvas.before:
            Color(*T.COLOR_GOLD)
            b._bg = RoundedRectangle(size=b.size, pos=b.pos, radius=[dp(8)] * 4)
        b.color = T.COLOR_BG; b.bold = True

        # 状态
        self.current_gua = None
        self.current_yao_list = None
        self.current_gua_detail = None
        self.current_changing_gua = None
        self.current_duangua_result = None

        return main_layout

    def _switch(self, name):
        m = {'起卦': self._tab_div, '64卦': self._tab_64, '运势': self._tab_fortune, '设置': self._tab_settings}
        s = {'起卦': '周易六十四卦 · 卜卦解惑', '64卦': '快速查找 · 点击查看',
             '运势': '每日专属 · 趋吉避凶', '设置': '个性化 · 数据管理'}
        self.header_sub.text = s.get(name, '')
        self.content.clear_widgets()
        w = m.get(name)
        if w:
            self.content.add_widget(w)
        self._cur_tab = name

    # ========== 起卦 Tab ==========
    def _build_div_tab(self):
        layout = BoxLayout(orientation='vertical', padding=(dp(10), dp(4), dp(10), dp(10)), spacing=dp(6), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # 卦象显示区（初始固定高度，起卦后自动扩展）
        self.gua_area = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(4))
        self.gua_area.bind(minimum_height=self.gua_area.setter('height'))
        apply_card_bg(self.gua_area)
        self.empty_sym = Label(text='☯', font_size=dp(48), color=T.COLOR_GOLD, halign='center', valign='middle',
                                size_hint_y=None, height=dp(88))
        self.empty_hint = Label(text='选择起卦方式', font_size=dp(14), color=T.COLOR_TEXT_SECOND, halign='center',
                                 size_hint_y=None, height=dp(22))
        self.gua_area.add_widget(self.empty_sym)
        self.gua_area.add_widget(self.empty_hint)

        # 结果
        self.res = BoxLayout(orientation='vertical', spacing=dp(3), padding=(dp(8), dp(4)))
        self.res.size_hint_y = None
        self.res.bind(minimum_height=self.res.setter('height'))
        self.res.add_widget(Label(text='', font_size=dp(24), color=T.COLOR_GOLD, bold=True, halign='center',
                                   size_hint_y=None, height=dp(32)))  # [0] gua_name
        self.res.add_widget(Label(text='', font_size=dp(11), color=T.COLOR_TEXT_SECOND, halign='center',
                                   size_hint_y=None, height=dp(18)))  # [1] palace
        # 修复：移除固定高度，用 minimum_height 自适应
        yao_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(3), padding=(dp(30), dp(4)))
        yao_box.bind(minimum_height=yao_box.setter('height'))
        self.res.add_widget(yao_box)  # [2] yao_area
        self.res.add_widget(Label(text='', font_size=dp(12), color=T.COLOR_TEXT, halign='center',
                                   size_hint_y=None, height=dp(36)))  # [3] gua_ci
        self.res.add_widget(Label(text='', font_size=dp(11), color=T.COLOR_GOLD, halign='center',
                                   size_hint_y=None, height=dp(20)))  # [4] changing
        self.res._yao_area = yao_box

        layout.add_widget(self.gua_area)

        # 起卦方式 2x2
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(150))
        for txt, sub, m in [('随机起卦', '心诚则灵', 'auto'), ('手动选卦', '64卦列表', 'manual'),
                             ('金钱起卦', '模拟摇卦', 'jinqian'), ('时间起卦', '以时起卦', 'time')]:
            card = self._make_card(txt, sub)
            btn = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='')
            if m == 'auto': btn.bind(on_press=lambda x: self._divine([random.randint(6, 9) for _ in range(6)], '电脑起卦'))
            elif m == 'manual': btn.bind(on_press=lambda x: self._manual_select())
            elif m == 'jinqian': btn.bind(on_press=self._jinqian)
            else: btn.bind(on_press=self._time)
            card.add_widget(btn)
            grid.add_widget(card)
        layout.add_widget(grid)

        # 功能按钮（两行）
        r1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
        for t, a in [('详解', self._explanation), ('六爻排盘', self._liuyao), ('问豆包', self._doubao), ('分享', self._share)]:
            r1.add_widget(create_action_btn(f' {t}', on_press=a))
        layout.add_widget(r1)

        r2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
        for t, a in [('复制', self._copy), ('重新起卦', lambda x: self._divine([random.randint(6, 9) for _ in range(6)], '电脑起卦'))]:
            r2.add_widget(create_action_btn(f' {t}', on_press=a))
        layout.add_widget(r2)

        return layout

    def _make_card(self, txt, sub=None):
        c = BoxLayout(orientation='vertical', padding=(dp(12), dp(10)), spacing=dp(2), size_hint_y=None, height=dp(70))
        apply_card_bg(c)
        c.add_widget(Label(text=txt, font_size=dp(15), bold=True, color=T.COLOR_GOLD, size_hint_y=0.6))
        c.add_widget(Label(text=sub or '', font_size=dp(11), color=T.COLOR_TEXT_SECOND, size_hint_y=0.4))
        return c

    # ========== 64卦 Tab ==========
    def _build_64_tab(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # 搜索
        sb = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
        self.s64 = TextInput(hint_text='搜索卦名...', font_size=dp(13), size_hint_x=1, multiline=False,
                              background_color=T.COLOR_BG_CARD, foreground_color=T.COLOR_TEXT,
                              hint_text_color=T.COLOR_TEXT_SECOND, cursor_color=T.COLOR_GOLD)
        self.s64.bind(on_text_validate=lambda x: self._refresh_64())
        sb.add_widget(self.s64)
        sbtn = create_gold_button('搜索', font_size=dp(12), height=dp(40), size_hint_x=None, width=dp(56))
        sbtn.bind(on_press=lambda x: self._refresh_64())
        sb.add_widget(sbtn)
        layout.add_widget(sb)

        # 宫位
        palaces = ['全部', '乾宫', '坤宫', '震宫', '巽宫', '坎宫', '离宫', '艮宫', '兑宫']
        self.p64 = ['全部']
        pr = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(34), spacing=dp(4))
        self.p64_btns = []
        for p in palaces:
            btn = Button(text=p, size_hint_x=1, font_size=dp(11), color=T.COLOR_TEXT_SECOND,
                         background_color=(0, 0, 0, 0), background_normal='')
            apply_card_bg(btn)
            def on_p(inst, pn=p):
                self.p64[0] = pn
                for pb in self.p64_btns:
                    pb.canvas.before.clear()
                    if pb.text == pn:
                        apply_card_bg(pb)
                        with pb.canvas.before:
                            Color(*T.COLOR_GOLD)
                            pb._bg = RoundedRectangle(size=pb.size, pos=pb.pos, radius=[dp(8)] * 4)
                        pb.color = T.COLOR_BG
                    else:
                        apply_card_bg(pb); pb.color = T.COLOR_TEXT_SECOND
                self._refresh_64()
            btn.bind(on_press=on_p)
            self.p64_btns.append(btn)
            pr.add_widget(btn)
        layout.add_widget(pr)
        # 高亮全部
        self.p64_btns[0].canvas.before.clear(); apply_card_bg(self.p64_btns[0])
        with self.p64_btns[0].canvas.before:
            Color(*T.COLOR_GOLD)
            self.p64_btns[0]._bg = RoundedRectangle(size=self.p64_btns[0].size, pos=self.p64_btns[0].pos, radius=[dp(8)] * 4)
        self.p64_btns[0].color = T.COLOR_BG

        # 网格
        self.g64 = GridLayout(cols=4, spacing=dp(4), size_hint_y=None, row_default_height=dp(60), row_force_default=True)
        self.g64.bind(minimum_height=self.g64.setter('height'))
        layout.add_widget(self.g64)

        self._all_gua = get_all_gua_with_palace()
        self._refresh_64()
        return layout

    def _refresh_64(self):
        self.g64.clear_widgets()
        q = self.s64.text.strip().lower() if hasattr(self, 's64') else ''
        pal = self.p64[0] if hasattr(self, 'p64') else '全部'
        fl = self._all_gua
        if pal != '全部': fl = [g for g in fl if g['palace'] == pal]
        if q: fl = [g for g in fl if q in g['name'].lower()]
        for gua in fl:
            card = BoxLayout(orientation='vertical', spacing=dp(2), padding=dp(2))
            binary = get_binary_from_name(gua['name'])
            if binary:
                card.add_widget(MiniGuaWidget(binary_str=binary, size_hint=(None, None), size=(dp(32), dp(28))))
            card.add_widget(Label(text=gua['name'], font_size=dp(9), color=T.COLOR_GOLD, halign='center'))
            card.add_widget(Label(text=gua.get('palace', ''), font_size=dp(8), color=T.COLOR_TEXT_DIM, halign='center'))
            btn = Button(text='', background_color=(0, 0, 0, 0), background_normal='')
            apply_card_bg(btn); btn.add_widget(card)
            def on_d(inst, gn=gua['name']): self._gua_detail(gn)
            btn.bind(on_press=on_d)
            self.g64.add_widget(btn)

    def _gua_detail(self, gn):
        try:
            import gua_db
            db = gua_db.get_gua_by_name(gn)
            if not db: show_toast(f'未找到 {gn}'); return
            pl = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
            pl.add_widget(Label(text=f'☯ {gn}', size_hint_y=None, height=dp(32), font_size=dp(16), color=T.COLOR_GOLD, bold=True))
            info = f'宫位：{get_gua_palace(gn)}'
            if db.get('upper_gua') and db.get('lower_gua'): info += f'  上{db["upper_gua"]}下{db["lower_gua"]}'
            pl.add_widget(Label(text=info, size_hint_y=None, height=dp(18), font_size=dp(11), color=T.COLOR_TEXT_SECOND))

            sc = ScrollView(size_hint_y=1)
            cl = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
            cl.bind(minimum_height=cl.setter('height'))
            def add_s(lt, dt):
                cl.add_widget(Label(text=lt, size_hint_y=None, height=dp(22), font_size=dp(13), color=T.COLOR_GOLD, bold=True))
                t = Label(text=dt, size_hint_y=None, halign='left', font_size=dp(12), color=T.COLOR_TEXT, padding=(6, 2))
                t.bind(size=t.setter('text_size')); cl.add_widget(t)
            if db.get('description'): add_s('【卦辞】', db['description'])
            if db.get('bai_hua'): add_s('【白话】', db['bai_hua'][:200])
            if db.get('guan_xiang'): add_s('【卦象】', db['guan_xiang'][:200])
            sc.add_widget(cl); pl.add_widget(sc)

            qb = create_gold_button('以此卦起卦', font_size=dp(13), height=dp(40))
            qb.bind(on_press=lambda x: self._quick_div(gn, popup))
            pl.add_widget(qb)

            cb = Button(text='关闭', size_hint_y=None, height=dp(38), font_size=dp(13),
                        color=T.COLOR_TEXT_SECOND, background_color=(0, 0, 0, 0), background_normal='')
            cb.bind(on_press=lambda x: popup.dismiss()); pl.add_widget(cb)

            popup = Popup(title='', content=pl, size_hint=(0.92, 0.75), auto_dismiss=True, background_color=T.COLOR_BG)
            popup.open()
        except Exception as e:
            logger.error(f'[Error] gua_detail: {e}')

    def _quick_div(self, gn, popup):
        popup.dismiss()
        yl = gua_name_to_yao(gn)
        if yl:
            self._switch('起卦')
            for n, b in self.tab_btns.items():
                b.canvas.before.clear()
                if n == '起卦':
                    apply_card_bg(b)
                    with b.canvas.before:
                        Color(*T.COLOR_GOLD)
                        b._bg = RoundedRectangle(size=b.size, pos=b.pos, radius=[dp(8)] * 4)
                    b.color = T.COLOR_BG; b.bold = True
                else:
                    apply_card_bg(b); b.color = T.COLOR_TEXT_SECOND; b.bold = False
            self._divine(yl, '手动选卦')
        else:
            show_toast(f'无法解析 {gn}')

    # ========== 运势 Tab ==========
    def _build_fortune_tab(self):
        layout = BoxLayout(orientation='vertical', padding=(dp(8), dp(4), dp(8), dp(8)), spacing=dp(6), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        today = datetime.now()
        layout.add_widget(Label(text=f'{today.year}年{today.month}月{today.day}日', font_size=dp(12),
                                 color=T.COLOR_TEXT_DIM, size_hint_y=None, height=dp(20), halign='center'))

        self.f_card = BoxLayout(orientation='vertical', size_hint_y=None, padding=(dp(12), dp(8)), spacing=dp(4))
        self.f_card.bind(minimum_height=self.f_card.setter('height'))
        apply_card_bg(self.f_card)
        self.f_name = Label(text='点击下方按钮查看今日运势', font_size=dp(18), color=T.COLOR_GOLD, bold=True, halign='center',
                             size_hint_y=None, height=dp(28))
        self.f_card.add_widget(self.f_name)
        self.f_yao = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(3), padding=(dp(15), dp(2)))
        self.f_yao.bind(minimum_height=self.f_yao.setter('height'))
        self.f_card.add_widget(self.f_yao)
        self.f_desc = Label(text='', font_size=dp(12), color=T.COLOR_TEXT_SECOND, halign='center', size_hint_y=None)
        self.f_desc.bind(size=self.f_desc.setter('text_size'))
        self.f_card.add_widget(self.f_desc)
        layout.add_widget(self.f_card)

        fb = create_gold_button('查看今日运势', font_size=dp(14), height=dp(46))
        fb.bind(on_press=self._daily)
        layout.add_widget(fb)

        acts = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(38), spacing=dp(6))
        for t, a in [('详解', self._explanation), ('六爻排盘', self._liuyao), ('分享', self._share)]:
            acts.add_widget(create_action_btn(f' {t}', on_press=a))
        layout.add_widget(acts)
        return layout

    def _update_fortune(self, gn, yl, cn):
        if not hasattr(self, 'f_name'): return
        self.f_name.text = gn
        self.f_yao.clear_widgets()
        names = ['上', '五', '四', '三', '二', '初']
        for i in range(6):
            self.f_yao.add_widget(make_yao_row_fortune(yl[5 - i], names[i]))
        if self.current_gua_detail and self.current_gua_detail.get('bai_hua'):
            self.f_desc.text = self.current_gua_detail['bai_hua'][:80] + '...'
        else:
            self.f_desc.text = ''
        if cn:
            self.f_desc.text += f'\n变卦：{cn}'

    # ========== 设置 Tab ==========
    def _build_settings_tab(self):
        layout = BoxLayout(orientation='vertical', padding=(dp(10), dp(4), dp(10), dp(10)), spacing=dp(8), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        vc = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), padding=(dp(20), dp(12)), spacing=dp(6))
        apply_card_bg(vc)
        vc.add_widget(Label(text='我爱八卦', font_size=dp(20), color=T.COLOR_GOLD, bold=True, halign='center', size_hint_y=None, height=dp(26)))
        vc.add_widget(Label(text=f'v{__version__} · 周易六十四卦 · 卜卦解惑', font_size=dp(11), color=T.COLOR_TEXT_SECOND, halign='center', size_hint_y=None, height=dp(18)))
        layout.add_widget(vc)

        from kivy.uix.switch import Switch
        sc = BoxLayout(orientation='vertical', size_hint_y=None, padding=(dp(15), dp(10)), spacing=dp(8))
        sc.bind(minimum_height=sc.setter('height'))
        apply_card_bg(sc)
        sc.add_widget(Label(text='功能选项', font_size=dp(14), color=T.COLOR_GOLD, bold=True, size_hint_y=None, height=dp(24)))
        for lt in ['音效', '震动', '自动起卦']:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36), spacing=dp(10))
            row.add_widget(Label(text=lt, font_size=dp(13), color=T.COLOR_TEXT))
            row.add_widget(Widget())
            row.add_widget(Switch(active=True, size_hint_x=None, width=dp(46)))
            sc.add_widget(row)
        for txt, msg in [('问豆包 AI', '打开豆包对话'), ('检查更新', '当前已是最新版本')]:
            btn = create_gold_button(f' {txt}', font_size=dp(13), height=dp(40))
            if txt == '问豆包 AI': btn.bind(on_press=self._doubao)
            else: btn.bind(on_press=lambda x, m=msg: show_toast(f' {m}'))
            sc.add_widget(btn)
        layout.add_widget(sc)

        fc = BoxLayout(orientation='vertical', size_hint_y=None, padding=(dp(15), dp(10)), spacing=dp(4))
        fc.bind(minimum_height=fc.setter('height'))
        apply_card_bg(fc)
        fc.add_widget(Label(text='功能列表', font_size=dp(14), color=T.COLOR_GOLD, bold=True, size_hint_y=None, height=dp(24)))
        for f in ['随机起卦', '手动选卦', '金钱起卦', '时间起卦', '今日运势', '卦象详解', '六爻排盘', 'AI 问豆包']:
            fc.add_widget(Label(text=f' ☯ {f}', font_size=dp(11), color=T.COLOR_TEXT, size_hint_y=None, height=dp(20)))
        layout.add_widget(fc)
        return layout

    # ========== 起卦逻辑 ==========
    def _divine(self, yl, method):
        try:
            if GUA_CALC_AVAILABLE:
                _, gn, cn, _ = gua_calculator.format_gua_display(yl, method)
                self.current_changing_gua = cn
                self.current_gua_detail = gua_calculator.get_gua_detail(gn)
                self.current_duangua_result = gua_calculator.duangua_logic(yl)
            else:
                gn = '未知卦'; cn = None

            self.current_gua = gn
            self.current_yao_list = yl
            self._show_result(gn, yl, cn)
            self._update_fortune(gn, yl, cn)
            show_toast(f' {gn}')
        except Exception as e:
            logger.error(f'[Error] divine: {e}'); show_toast('显示失败')

    def _show_result(self, gn, yl, cn):
        if not hasattr(self, 'empty_sym'): return
        if self.empty_sym.parent: self.gua_area.remove_widget(self.empty_sym)
        if self.empty_hint.parent: self.gua_area.remove_widget(self.empty_hint)
        if not self.res.parent:
            self.gua_area.add_widget(self.res, index=0)
            # 移除空状态后，gua_area 高度由 minimum_height 自动计算
            # 但需要等待一帧让 Kivy 重新计算布局
            Clock.schedule_once(lambda dt: self.gua_area._trigger_layout(), 0)

        self.res.children[4].text = gn  # gua_name_label
        self.res.children[3].text = get_gua_palace(gn) or ''  # palace
        self.res._yao_area.clear_widgets()
        names = ['上', '五', '四', '三', '二', '初']
        for i in range(6):
            self.res._yao_area.add_widget(make_yao_row(yl[5 - i], names[i]))
        if self.current_gua_detail and self.current_gua_detail.get('gua_ci'):
            self.res.children[1].text = self.current_gua_detail['gua_ci'][:60]  # gua_ci
        else:
            self.res.children[1].text = ''
        self.res.children[0].text = f'变卦：{cn}' if cn else ''  # changing

    def _jinqian(self, inst):
        try:
            self._divine(gua_calculator.jinqian_qigua(), '金钱起卦')
        except Exception as e:
            logger.error(f'[Error] jinqian: {e}'); show_toast('金钱起卦失败')

    def _time(self, inst):
        try:
            now = datetime.now()
            self._divine(gua_calculator.time_qigua(now.year, now.month, now.day, now.hour, now.minute), '时间起卦')
        except Exception as e:
            logger.error(f'[Error] time: {e}'); show_toast('时间起卦失败')

    def _daily(self, inst):
        self._divine(get_daily_gua(), '今日运势')

    # ========== 手动选卦 ==========
    def _manual_select(self):
        try:
            all_gua = get_all_gua_with_palace()
            if not all_gua: show_toast('卦象数据加载失败'); return

            pl = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
            pl.add_widget(Label(text='选择卦象', size_hint_y=None, height=dp(36), font_size=dp(16), color=T.COLOR_GOLD, bold=True))

            palaces = ['全部', '乾宫', '坤宫', '震宫', '巽宫', '坎宫', '离宫', '艮宫', '兑宫']
            cur = ['全部']
            pr = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(34), spacing=dp(4))
            pbtns = []
            for p in palaces:
                btn = Button(text=p, size_hint_x=1, font_size=dp(11), color=T.COLOR_TEXT_SECOND,
                             background_color=(0, 0, 0, 0), background_normal='')
                apply_card_bg(btn)
                def on_p(inst, pn=p):
                    cur[0] = pn
                    for pb in pbtns:
                        pb.canvas.before.clear()
                        if pb.text == pn:
                            apply_card_bg(pb)
                            with pb.canvas.before:
                                Color(*T.COLOR_GOLD)
                                pb._bg = RoundedRectangle(size=pb.size, pos=pb.pos, radius=[dp(8)] * 4)
                            pb.color = T.COLOR_BG
                        else:
                            apply_card_bg(pb); pb.color = T.COLOR_TEXT_SECOND
                    refresh(pn)
                btn.bind(on_press=on_p)
                pbtns.append(btn)
                pr.add_widget(btn)
            pl.add_widget(pr)
            pbtns[0].canvas.before.clear(); apply_card_bg(pbtns[0])
            with pbtns[0].canvas.before:
                Color(*T.COLOR_GOLD)
                pbtns[0]._bg = RoundedRectangle(size=pbtns[0].size, pos=pbtns[0].pos, radius=[dp(8)] * 4)
            pbtns[0].color = T.COLOR_BG

            gl = GridLayout(cols=4, spacing=dp(4), size_hint_y=None)
            gl.bind(minimum_height=gl.setter('height'))

            popup = Popup(title='', content=pl, size_hint=(0.95, 0.8), auto_dismiss=True, background_color=T.COLOR_BG)

            def refresh(palace):
                gl.clear_widgets()
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
                        if yl: self._divine(yl, '手动选卦')
                        else: show_toast(f'无法解析 {gn}')
                    btn.bind(on_press=on_g)
                    gl.add_widget(btn)

            refresh('全部')
            pl.add_widget(gl)
            popup.open()
        except Exception as e:
            logger.error(f'[Error] manual_select: {e}'); show_toast('弹窗失败')

    # ========== 功能按钮 ==========
    def _explanation(self, inst):
        if not self.current_gua: show_toast('请先起卦'); return
        try:
            import gua_db
            db = gua_db.get_gua_by_name(self.current_gua)
            if not db: show_toast(f'未找到 {self.current_gua}'); return
            pl = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
            pl.add_widget(Label(text=f'【{self.current_gua}】详解', size_hint_y=None, height=dp(32), font_size=dp(15), color=T.COLOR_GOLD, bold=True))
            sc = ScrollView(size_hint_y=1)
            cl = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
            cl.bind(minimum_height=cl.setter('height'))
            def add_s(lt, dt):
                cl.add_widget(Label(text=lt, size_hint_y=None, height=dp(22), font_size=dp(13), color=T.COLOR_GOLD, bold=True))
                t = Label(text=dt, size_hint_y=None, halign='left', font_size=dp(12), color=T.COLOR_TEXT, padding=(6, 2))
                t.bind(size=t.setter('text_size')); cl.add_widget(t)
            has_content = False
            if db.get('description'): add_s('【卦辞】', db['description']); has_content = True
            if db.get('bai_hua'): add_s('【白话】', db['bai_hua']); has_content = True
            if db.get('guan_xiang'): add_s('【卦象】', db['guan_xiang']); has_content = True
            if self.current_duangua_result: add_s('【断卦】', self.current_duangua_result.get('duan_gua_method', '')); has_content = True
            if not has_content: cl.add_widget(Label(text='暂无详细数据', size_hint_y=None, height=dp(40), color=T.COLOR_TEXT_SECOND, halign='center'))
            sc.add_widget(cl); pl.add_widget(sc)
            popup = Popup(title='', content=pl, size_hint=(0.95, 0.85), auto_dismiss=True, background_color=T.COLOR_BG)
            cb = Button(text='关闭', size_hint_y=None, height=dp(40), font_size=dp(14), color=T.COLOR_TEXT_SECOND, background_color=(0,0,0,0), background_normal='')
            cb.bind(on_press=lambda x: popup.dismiss()); pl.add_widget(cb)
            popup.open()
        except Exception as e:
            logger.error(f'[Error] explanation: {e}'); show_toast('显示失败')

    def _liuyao(self, inst):
        if not self.current_gua: show_toast('请先起卦'); return
        try:
            from liuyao_paipan import format_liuyao_full
            text = format_liuyao_full(self.current_yao_list, self.current_gua)
            if not text: text = '暂无排盘数据'
            pl = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
            pl.add_widget(Label(text='六爻排盘', size_hint_y=None, height=dp(32), font_size=dp(15), color=T.COLOR_GOLD, bold=True))
            sc = ScrollView(size_hint_y=1)
            c = Label(text=text, markup=True, size_hint_y=None, halign='left', valign='top', font_size=dp(11), color=T.COLOR_TEXT, padding=(dp(6), dp(4)))
            c.bind(size=c.setter('text_size')); c.bind(texture_size=lambda *a: setattr(c, 'height', max(c.texture_size[1], dp(100))))
            sc.add_widget(c); pl.add_widget(sc)
            popup = Popup(title='', content=pl, size_hint=(0.95, 0.85), auto_dismiss=True, background_color=T.COLOR_BG)
            cb = create_gold_button('关闭', font_size=dp(13), height=dp(40))
            cb.bind(on_press=lambda x: popup.dismiss()); pl.add_widget(cb)
            popup.open()
        except Exception as e:
            logger.error(f'[Error] liuyao: {e}'); show_toast('排盘失败')

    def _share(self, inst):
        if not self.current_gua: show_toast('请先起卦'); return
        text = f'【{self.current_gua}】\n\n'
        if self.current_yao_list:
            yn = ['初', '二', '三', '四', '五', '上']
            for i in range(5, -1, -1):
                y = self.current_yao_list[i]
                text += f'{yn[i]}{"阳" if y in [7,9] else "阴"}{" " if y==9 else " " if y==6 else ""}\n'
        if self.current_changing_gua: text += f'\n变卦：{self.current_changing_gua}'

        pl = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        pl.add_widget(Label(text='选择分享方式', size_hint_y=None, height=dp(36), font_size=dp(15), color=T.COLOR_GOLD, bold=True))

        popup = Popup(title='', content=pl, size_hint=(0.85, 0.5), auto_dismiss=False, background_color=T.COLOR_BG)

        def do_copy():
            copy_to_clipboard(text); popup.dismiss(); show_toast('已复制')
        def do_share(platform):
            copy_to_clipboard(text); popup.dismiss(); show_toast(f'已复制，请打开{platform}粘贴')

        for name, cb in [('复制文本', do_copy), ('分享到微信', lambda: do_share('微信')), ('分享到 QQ', lambda: do_share('QQ'))]:
            btn = create_gold_button(f' {name}', font_size=dp(14), height=dp(42))
            btn.bind(on_press=lambda x, c=cb: c()); pl.add_widget(btn)

        cancel = Button(text='取消', size_hint_y=None, height=dp(40), font_size=dp(14), color=T.COLOR_TEXT_SECOND, background_color=(0,0,0,0), background_normal='')
        cancel.bind(on_press=lambda x: popup.dismiss()); pl.add_widget(cancel)
        popup.open()

    def _copy(self, inst):
        if not self.current_gua: show_toast('请先起卦'); return
        text = f'【{self.current_gua}】\n'
        if self.current_yao_list:
            yn = ['初', '二', '三', '四', '五', '上']
            for i in range(5, -1, -1):
                y = self.current_yao_list[i]
                text += f'{yn[i]}{"阳" if y in [7,9] else "阴"}{" " if y==9 else " " if y==6 else ""}\n'
        if self.current_changing_gua: text += f'\n变卦：{self.current_changing_gua}'
        copy_to_clipboard(text); show_toast('已复制')

    def _doubao(self, inst):
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
            logger.error(f'[Error] doubao: {e}'); show_toast('打开豆包失败')


if __name__ == '__main__':
    WuaibaguaApp().run()
