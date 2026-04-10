#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 v1.3.0 - 周易六十四卦 · 卜卦解惑
功能：电脑起卦、手动选卦、金钱起卦、时间起卦、今日运势、64卦速查
      卦象解释、六爻排盘、分享功能、Android JNI 兼容

【重要】OPPO 设备 Vulkan 禁用
必须在 import kivy 之前设置环境变量和 Config！

v1.3.0 更新：
- 全新 Tabbed UI 架构（起卦 | 64卦 | 运势 | 设置）
- 手动选卦改为 64 卦列表选择（支持宫位筛选）
- 全新配色方案：深蓝黑 + 古铜金
- 修复 get_device_id Android 兼容性
- 卡片式布局，圆角按钮，视觉升级
"""

__version__ = '1.3.0'

# ==================== 全局异常处理器 ====================
import sys
import traceback
import logging

def setup_global_exception_handler():
    """设置全局异常处理器，记录所有未捕获的异常"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.error("============= 全局异常捕获 =============")
        logging.error(f"异常类型：{exc_type.__name__}")
        logging.error(f"异常信息：{exc_value}")
        logging.error("堆栈跟踪:")
        logging.error(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        logging.error("========================================")
        try:
            from kivy.clock import Clock
            def show_error():
                try:
                    show_toast(f' 错误：{str(exc_value)[:50]}')
                except:
                    pass
            Clock.schedule_once(lambda dt: show_error(), 0)
        except:
            pass
    sys.excepthook = handle_exception
    try:
        import threading
        threading.excepthook = lambda args: handle_exception(
            args.exc_type, args.exc_value, args.exc_traceback
        )
    except:
        pass

setup_global_exception_handler()

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('wuaibagua')

# ==================== Android JNI（延迟初始化） ====================
ANDROID_AVAILABLE = False
autoclass = None

def init_android_jni():
    """延迟初始化 Android JNI（在应用启动后调用）"""
    global ANDROID_AVAILABLE, autoclass
    if ANDROID_AVAILABLE:
        return
    try:
        from jnius import autoclass as jni_autoclass
        autoclass = jni_autoclass
        ANDROID_AVAILABLE = True
        logger.info('[INFO] Android JNI 初始化成功')
    except ImportError as e:
        autoclass = None
        ANDROID_AVAILABLE = False
        logger.warning(f'[WARN] jnius not available (desktop mode): {e}')
    except Exception as e:
        autoclass = None
        ANDROID_AVAILABLE = False
        logger.error(f'[ERROR] Android JNI 初始化失败：{e}')

ANDROID_CLIPBOARD_AVAILABLE = False

def init_android_clipboard():
    """延迟初始化 Android 剪贴板"""
    global ANDROID_CLIPBOARD_AVAILABLE
    init_android_jni()
    ANDROID_CLIPBOARD_AVAILABLE = ANDROID_AVAILABLE

# ==================== Vulkan 禁用（必须在 Kivy 导入前） ====================
import os
os.environ['KIVY_GL_BACKEND'] = 'gl'
os.environ['KIVY_NO_VULKAN'] = '1'
os.environ['KIVY_VIDEO_OPTS'] = 'gl'
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

from kivy.config import Config
Config.set('graphics', 'backend', 'gl')
Config.set('graphics', 'gl_backend', 'gl')
Config.set('graphics', 'vsync', '0')
Config.set('graphics', 'max_buffers', '1')
Config.set('input', 'mouse', 'mouse,disable_multitouch,multitouch_on_demand')
Config.set('kivy', 'log_level', 'error')
Config.set('kivy', 'log_dir', '/dev/null')

# 全局默认字体（⚠️ 必须在任何 Kivy import 之前设置）
# 这样所有 Widget 自动使用该字体，无需单独设置 font_name
Config.set(
    'kivy', 'default_font',
    ['NotoSansSC', 'fonts/NotoSansSC-Regular.ttf', 'fonts/NotoSansSC-Regular.ttf',
     'fonts/NotoSansSC-Regular.ttf', 'fonts/NotoSansSC-Regular.ttf']
)

# ==================== 标准导入 ====================
import random
import hashlib
from datetime import datetime

try:
    import gua_calculator
    GUA_CALC_AVAILABLE = True
except ImportError:
    GUA_CALC_AVAILABLE = False
    print('[WARN] gua_calculator module not available')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle

# ==================== 配色方案（v1.3.0） ====================
COLOR_BG = (0.086, 0.133, 0.243, 1)         # #16213e 深蓝黑
COLOR_BG_CARD = (0.118, 0.173, 0.302, 1)     # #1e2c4a 卡片背景
COLOR_BG_CARD_LIGHT = (0.157, 0.220, 0.353, 1)  # #283858 浅卡片
COLOR_GOLD = (0.788, 0.663, 0.431, 1)        # #c9a96e 古铜金
COLOR_GOLD_LIGHT = (0.85, 0.75, 0.55, 1)     # 浅金
COLOR_TEXT = (0.878, 0.835, 0.757, 1)        # #e0d5c1 米白
COLOR_TEXT_SECOND = (0.541, 0.494, 0.420, 1) # #8a7e6b 次级文字
COLOR_TEXT_DIM = (0.420, 0.420, 0.369, 1)    # #6b6b5e 暗淡文字
COLOR_WHITE = (1, 1, 1, 1)
COLOR_RED = (0.8, 0.3, 0.3, 1)
COLOR_GREEN = (0.3, 0.7, 0.4, 1)

# ==================== 卦象符号组件 ====================

def yao_lines_from_binary(binary_str):
    """将 6 位二进制字符串转为 6 爻列表（从下往上）"""
    if not binary_str or len(binary_str) != 6:
        return [7, 7, 7, 7, 7, 7]  # 默认全阳
    # binary_str 是从上往上的，但 draw 是从下往上的
    return [7 if b == '1' else 8 for b in binary_str]


class GuaSymbolWidget(BoxLayout):
    """卦象符号组件：用 Kivy Canvas 绘制 6 爻（不依赖字体）"""
    def __init__(self, yao_list=None, binary_str=None, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(2), **kwargs)
        self.size_hint_y = None
        self.height = dp(50)
        
        if binary_str:
            self.yao_list = yao_lines_from_binary(binary_str)
        elif yao_list:
            self.yao_list = yao_list
        else:
            self.yao_list = [7, 7, 7, 7, 7, 7]
        
        self._draw_yao()
    
    def _draw_yao(self):
        """绘制 6 爻"""
        self.clear_widgets()
        yao_height = dp(5)
        total_h = 6 * (yao_height + dp(2))
        self.height = total_h
        
        # 从下往上画（传统顺序）
        for i in range(5, -1, -1):
            yao_type = self.yao_list[i] if i < len(self.yao_list) else 7
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=yao_height)
            y_pos = (5 - i) * (yao_height + dp(2))
            
            is_yang = yao_type in [7, 9]
            is_changing = yao_type in [6, 9]
            margin = dp(2)
            line_w = dp(40)
            
            if is_yang:
                # 阳爻：实线
                line = BoxLayout(size_hint_x=None, width=line_w)
                with line.canvas:
                    if is_changing:
                        Color(*COLOR_GOLD_LIGHT)
                    else:
                        Color(*COLOR_GOLD)
                    line._rect = RoundedRectangle(size=(line_w, yao_height), radius=[dp(2)])
                    line.bind(size=lambda *a: setattr(line._rect, 'size', (line_w, yao_height)))
                row.add_widget(Widget())
                row.add_widget(line)
                row.add_widget(Widget())
            else:
                # 阴爻：两段
                gap = dp(6)
                half_w = (line_w - gap) / 2
                left = BoxLayout(size_hint_x=None, width=line_w)
                with left.canvas:
                    Color(*COLOR_GOLD)
                    left._rect = RoundedRectangle(pos=(margin, 0), size=(half_w, yao_height), radius=[dp(2)])
                    left._rect2 = RoundedRectangle(pos=(margin + half_w + gap, 0), size=(half_w, yao_height), radius=[dp(2)])
                row.add_widget(Widget())
                row.add_widget(left)
                row.add_widget(Widget())
            
            self.add_widget(row)


class MiniGuaWidget(Widget):
    """迷你卦象符号（用于 64 卦卡片，固定尺寸）"""
    def __init__(self, yao_list=None, binary_str=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.width = dp(40)
        self.height = dp(40)
        
        if binary_str:
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
                    Color(*COLOR_GOLD)
                    RoundedRectangle(pos=(self.x + dp(3), y), size=(line_w, yao_h), radius=[dp(1)])
                else:
                    half = (line_w - dp(4)) / 2
                    Color(*COLOR_GOLD)
                    RoundedRectangle(pos=(self.x + dp(3), y), size=(half, yao_h), radius=[dp(1)])
                    RoundedRectangle(pos=(self.x + dp(3) + half + dp(4), y), size=(half, yao_h), radius=[dp(1)])


# ==================== 8 宫映射 ====================
GUA_PALACE_MAP = {
    # 乾宫
    '乾为天': '乾宫', '天风姤': '乾宫', '天山遁': '乾宫', '天地否': '乾宫',
    '风地观': '乾宫', '山地剥': '乾宫', '火地晋': '乾宫', '火天大有': '乾宫',
    # 坎宫
    '坎为水': '坎宫', '水泽节': '坎宫', '水雷屯': '坎宫', '水火既济': '坎宫',
    '泽火革': '坎宫', '雷火丰': '坎宫', '地火明夷': '坎宫', '地水师': '坎宫',
    # 艮宫
    '艮为山': '艮宫', '山火贲': '艮宫', '山天大畜': '艮宫', '山泽损': '艮宫',
    '火泽睽': '艮宫', '天泽履': '艮宫', '风泽中孚': '艮宫', '风山渐': '艮宫',
    # 震宫
    '震为雷': '震宫', '雷地豫': '震宫', '雷水解': '震宫', '雷风恒': '震宫',
    '地风升': '震宫', '水风井': '震宫', '泽风大过': '震宫', '泽雷随': '震宫',
    # 巽宫
    '巽为风': '巽宫', '风天小畜': '巽宫', '风火家人': '巽宫', '风雷益': '巽宫',
    '天雷无妄': '巽宫', '火雷噬嗑': '巽宫', '山雷颐': '巽宫', '山风蛊': '巽宫',
    # 离宫
    '离为火': '离宫', '火山旅': '离宫', '火风鼎': '离宫', '火水未济': '离宫',
    '山水蒙': '离宫', '风水涣': '离宫', '天水讼': '离宫', '天火同人': '离宫',
    # 坤宫
    '坤为地': '坤宫', '地雷复': '坤宫', '地泽临': '坤宫', '地天泰': '坤宫',
    '雷天大壮': '坤宫', '泽天夬': '坤宫', '水天需': '坤宫', '水地比': '坤宫',
    # 兑宫
    '兑为泽': '兑宫', '泽水困': '兑宫', '泽地萃': '兑宫', '泽山咸': '兑宫',
    '水山蹇': '兑宫', '地山谦': '兑宫', '雷山小过': '兑宫', '雷泽归妹': '兑宫',
}

# 八宫卦序（每宫 8 卦，共 64 卦）
# 乾宫：乾为天(本)、天风姤(1)、天山遁(2)、天地否(3)、风地观(4)、山地剥(5)、火地晋(游魂)、火天大有(归魂)
# 兑宫：兑为泽(本)、泽水困(1)、泽地萃(2)、泽山咸(3)、水山蹇(4)、地山谦(5)、雷山小过(游魂)、雷泽归妹(归魂)

# ==================== 工具函数 ====================

def copy_to_clipboard(text):
    """复制文本到剪贴板（修复版：更安全地获取 Context）"""
    try:
        if not ANDROID_CLIPBOARD_AVAILABLE:
            init_android_clipboard()
        if ANDROID_CLIPBOARD_AVAILABLE and autoclass:
            Context = autoclass('android.content.Context')
            ClipboardManager = autoclass('android.content.ClipboardManager')
            ClipData = autoclass('android.content.ClipData')
            app = App.get_running_app()
            context = None
            if app:
                context = _get_android_context(app)
            # 回退：通过 PythonActivity 获取
            if not context:
                try:
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    context = PythonActivity.mActivity
                except:
                    pass
            if context:
                clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE)
                clip = ClipData.newPlainText('wuaibagua', text)
                clipboard.setPrimaryClip(clip)
                logger.info(f'[INFO] 已复制到剪贴板：{text[:50]}...')
            else:
                logger.warning('[WARN] 无法获取 Android Context')
        else:
            logger.info(f'[INFO] Copy: {text[:50]}...')
    except Exception as e:
        logger.error(f'[ERROR] Copy failed: {e}')


def _get_android_context(app):
    """安全获取 Android Context（修复 getApplicationContext 问题）"""
    try:
        if hasattr(app, 'getApplicationContext'):
            return app.getApplicationContext()
        # 回退方案：通过 mActivity 获取
        if hasattr(app, 'mActivity') and app.mActivity:
            return app.mActivity.getApplicationContext()
        # 终极方案：通过 autoclass 获取 Activity
        if autoclass:
            Activity = autoclass('android.app.Activity')
            if hasattr(Activity, 'mActivity') and Activity.mActivity:
                return Activity.mActivity.getApplicationContext()
    except Exception:
        pass
    return None


def show_toast(message):
    """显示 Toast 提示"""
    try:
        if not ANDROID_CLIPBOARD_AVAILABLE:
            init_android_clipboard()
        if ANDROID_CLIPBOARD_AVAILABLE and autoclass:
            Toast = autoclass('android.widget.Toast')
            app = App.get_running_app()
            if app:
                context = _get_android_context(app)
                if context:
                    toast = Toast.makeText(context, message, Toast.LENGTH_SHORT)
                    toast.show()
                    return
        logger.info(f'[TOAST] {message}')
    except Exception as e:
        logger.error(f'[ERROR] Toast failed: {e}')


def get_device_id():
    """获取设备识别码（Android）—— 修复版"""
    try:
        if not ANDROID_CLIPBOARD_AVAILABLE:
            init_android_clipboard()
        if ANDROID_CLIPBOARD_AVAILABLE and autoclass:
            Settings = autoclass('android.provider.Settings$Secure')
            app = App.get_running_app()
            if app:
                context = _get_android_context(app)
                if context:
                    resolver = context.getContentResolver()
                    android_id = Settings.Secure.getString(resolver, 'android_id')
                    return android_id if android_id else 'default'
        return 'default'
    except Exception as e:
        logger.error(f'[ERROR] get_device_id: {e}')
        return 'default'


def get_daily_gua():
    """
    今日运势算法
    根据日期 + 设备 ID 生成 deterministic 卦象
    """
    try:
        today = datetime.now().strftime('%Y%m%d')
        device_id = get_device_id()
        seed_str = f"{today}_{device_id}"
        seed_hash = hashlib.sha256(seed_str.encode()).hexdigest()
        yao_list = []
        for i in range(6):
            byte_val = int(seed_hash[i*4:(i+1)*4], 16)
            mod = byte_val % 100
            if mod < 10:
                yao = 6
            elif mod < 45:
                yao = 7
            elif mod < 55:
                yao = 8
            else:
                yao = 9
            yao_list.append(yao)
        return yao_list
    except Exception as e:
        print(f'[ERROR] get_daily_gua: {e}')
        return [random.randint(6, 9) for _ in range(6)]


# ==================== UI 样式辅助 ====================

def apply_card_bg(widget, radius=None):
    """给 Widget 应用卡片背景（圆角矩形）"""
    if radius is None:
        radius = [dp(12), dp(12), dp(12), dp(12)]
    with widget.canvas.before:
        Color(*COLOR_BG_CARD)
        widget._bg_rect = RoundedRectangle(size=widget.size, pos=widget.pos, radius=radius)
        def update_rect(*args):
            widget._bg_rect.size = widget.size
            widget._bg_rect.pos = widget.pos
        widget.bind(size=update_rect, pos=update_rect)
    return widget


def apply_gold_bg(widget, radius=None):
    """金色渐变背景（按钮用）"""
    if radius is None:
        radius = [dp(10), dp(10), dp(10), dp(10)]
    with widget.canvas.before:
        Color(*COLOR_GOLD)
        widget._bg_rect = RoundedRectangle(size=widget.size, pos=widget.pos, radius=radius)
        def update_rect(*args):
            widget._bg_rect.size = widget.size
            widget._bg_rect.pos = widget.pos
        widget.bind(size=update_rect, pos=update_rect)
    return widget


def create_round_button(text, font_size=None, height=None, **kwargs):
    """创建圆角金色按钮"""
    btn = Button(
        text=text,
        font_size=font_size or dp(15),
        size_hint_y=None,
        height=height or dp(48),
        color=COLOR_BG,
        bold=True,
        background_color=(0, 0, 0, 0),
        background_normal='',
        **kwargs
    )
    apply_gold_bg(btn)
    return btn


def create_card_button(text, font_size=None, height=None, subtitle=None, **kwargs):
    """创建卡片式按钮（带副标题）"""
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
        color=COLOR_GOLD,
        size_hint_y=0.6,
    )
    layout.add_widget(main_label)

    if subtitle:
        sub_label = Label(
            text=subtitle,
            font_size=dp(11),
            color=COLOR_TEXT_SECOND,
            size_hint_y=0.4,
        )
        layout.add_widget(sub_label)
    else:
        spacer = Label(text='', size_hint_y=0.4)
        layout.add_widget(spacer)

    return layout


def draw_yao_symbol(canvas_obj, yao_type, width, y_pos, yao_height=dp(8)):
    """在 canvas 上画爻符（阳爻实线 / 阴爻虚线）"""
    is_yang = yao_type in [7, 9]
    is_changing = yao_type in [6, 9]
    margin = width * 0.15
    line_w = width - 2 * margin

    with canvas_obj:
        if is_changing:
            Color(*COLOR_GOLD_LIGHT)
        else:
            Color(*COLOR_GOLD)

        if is_yang:
            # 阳爻：一条实线
            RoundedRectangle(
                pos=(margin, y_pos),
                size=(line_w, yao_height),
                radius=[dp(2), dp(2), dp(2), dp(2)]
            )
        else:
            # 阴爻：两条短横线
            gap = line_w * 0.08
            half = (line_w - gap) / 2
            RoundedRectangle(
                pos=(margin, y_pos),
                size=(half, yao_height),
                radius=[dp(2), dp(2), dp(2), dp(2)]
            )
            RoundedRectangle(
                pos=(margin + half + gap, y_pos),
                size=(half, yao_height),
                radius=[dp(2), dp(2), dp(2), dp(2)]
            )

        # 变爻标记
        if is_changing:
            Color(*COLOR_TEXT_SECOND)
            mark = '' if yao_type == 9 else ''
            from kivy.graphics import Canvas
            # 简单文本标记，用额外 Label 会更好


def get_gua_palace(gua_name):
    """获取卦象所属宫位"""
    return GUA_PALACE_MAP.get(gua_name, '')


def get_all_gua_with_palace():
    """获取所有卦象及宫位信息"""
    try:
        import gua_db
        names = gua_db.get_all_gua_names()
        result = []
        for item in names:
            name = item['name']
            palace = get_gua_palace(name)
            result.append({'name': name, 'short': item.get('short_name', name[:2]), 'palace': palace})
        return result
    except Exception as e:
        logger.error(f'[ERROR] get_all_gua_with_palace: {e}')
        return []


def get_binary_from_name(gua_name):
    """通过卦名获取二进制表示"""
    try:
        import gua_db
        names = gua_db.get_all_gua_names()
        for item in names:
            if item['name'] == gua_name:
                return item.get('binary', '')
    except:
        pass
    # 回退：通过 gua_calculator 遍历
    try:
        for binary, name in gua_calculator.HEXAGRAM_NAMES.items():
            if name == gua_name:
                return binary
    except:
        pass
    return ''


# ==================== 分享弹窗 ====================

def show_share_popup(text):
    """分享弹窗"""
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        title = Label(
            text='选择分享方式',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18),
            color=COLOR_GOLD,
            bold=True,
        )
        layout.add_widget(title)

        options = [
            (' 复制文本', lambda: _share_copy(text, popup)),
            (' 分享到微信', lambda: _share_wechat(text, popup)),
            (' 分享到 QQ', lambda: _share_qq(text, popup)),
        ]

        for name, callback in options:
            btn = create_round_button(name, font_size=dp(15), height=dp(48))
            btn.bind(on_press=lambda x, cb=callback: cb())
            layout.add_widget(btn)

        cancel_btn = Button(
            text='取消',
            size_hint_y=None,
            height=dp(45),
            font_size=dp(15),
            color=COLOR_TEXT_SECOND,
            background_color=(0, 0, 0, 0),
            background_normal='',
        )
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(cancel_btn)

        popup = Popup(
            title='分享',
            title_color=COLOR_GOLD,
            content=layout,
            size_hint=(0.85, 0.65),
            auto_dismiss=False,
            background_color=COLOR_BG,
        )
        popup.open()
    except Exception as e:
        logger.error(f'[ERROR] show_share_popup: {e}')


def _share_copy(text, popup):
    copy_to_clipboard(text)
    popup.dismiss()
    show_toast(' 已复制')

def _share_wechat(text, popup):
    copy_to_clipboard(text)
    popup.dismiss()
    show_toast(' 已复制，请打开微信粘贴')

def _share_qq(text, popup):
    copy_to_clipboard(text)
    popup.dismiss()
    show_toast(' 已复制，请打开 QQ 粘贴')


# ==================== 六爻排盘弹窗 ====================

def show_liuyao_popup(panduan_text):
    """六爻排盘弹窗"""
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))

        title = Label(
            text='六爻排盘',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(17),
            color=COLOR_GOLD,
            bold=True,
        )
        layout.add_widget(title)

        # ScrollView 必须有 size_hint_y=1 才能正确填充剩余空间
        scroll = ScrollView(size_hint_y=1)
        content = Label(
            text=panduan_text,
            markup=True,  # 启用 markup 支持中文换行
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=dp(12),
            color=COLOR_TEXT,
            padding=(dp(8), dp(4)),
        )
        content.bind(size=content.setter('text_size'))
        content.bind(texture_size=lambda *a: setattr(content, 'height', content.texture_size[1]))
        scroll.add_widget(content)
        layout.add_widget(scroll)

        # 先创建 popup 变量，再绑定按钮事件
        popup = Popup(
            title='',
            content=layout,
            size_hint=(0.95, 0.85),
            auto_dismiss=True,
            background_color=COLOR_BG,
        )
        close_btn = create_round_button(' 关闭', font_size=dp(15), height=dp(42))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)

        popup.open()
    except Exception as e:
        import traceback
        logger.error(f'[ERROR] show_liuyao_popup: {e}')
        logger.error(traceback.format_exc())
        show_toast(' 排盘失败')


# ==================== 设置弹窗 ====================

def show_settings_popup():
    """设置弹窗"""
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))

        title = Label(
            text='设置',
            size_hint_y=None,
            height=dp(45),
            font_size=dp(20),
            color=COLOR_GOLD,
            bold=True,
        )
        layout.add_widget(title)

        info_text = (
            f'版本：v{__version__}\n'
            f'作者：浩哥\n\n'
            f'☯ 周易六十四卦 · 卜卦解惑\n\n'
            f'起卦方式：\n'
            f'   电脑起卦（随机）\n'
            f'   手动选卦（64卦列表）\n'
            f'   金钱起卦（模拟摇卦）\n'
            f'   时间起卦（以时起卦）\n\n'
            f'更多功能开发中...'
        )
        info_label = Label(
            text=info_text,
            size_hint_y=None,
            height=dp(200),
            font_size=dp(14),
            color=COLOR_TEXT,
            halign='left',
            valign='top',
            padding=(10, 5),
        )
        info_label.bind(size=info_label.setter('text_size'))
        layout.add_widget(info_label)

        close_btn = create_round_button('关闭', font_size=dp(15), height=dp(45))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)

        popup = Popup(
            title='设置',
            title_color=COLOR_GOLD,
            content=layout,
            size_hint=(0.8, 0.65),
            auto_dismiss=False,
            background_color=COLOR_BG,
        )
        popup.open()
    except Exception as e:
        logger.error(f'[ERROR] show_settings_popup: {e}')


# ==================== 卦象解释弹窗 ====================

def show_gua_explanation_with_duangua(gua_name, detail_data, yao_list, changing_gua_name=None, duangua_result=None):
    """显示卦象解释和断卦结果（数据库完整版）"""
    try:
        import gua_db

        db_data = gua_db.get_gua_by_name(gua_name)
        if not db_data:
            show_toast(f' 未找到 {gua_name} 的数据')
            return

        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        title = Label(
            text=f'【{gua_name}】详解',
            size_hint_y=None,
            height=dp(45),
            font_size=dp(18),
            color=COLOR_GOLD,
            bold=True,
        )
        layout.add_widget(title)

        scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        content_layout.bind(minimum_height=content_layout.setter('height'))

        def add_section(label_text, detail_text, font_size=dp(14)):
            section_label = Label(
                text=label_text,
                size_hint_y=None,
                height=dp(28),
                font_size=dp(15),
                color=COLOR_GOLD,
                bold=True,
                halign='left',
            )
            content_layout.add_widget(section_label)
            text_label = Label(
                text=detail_text,
                size_hint_y=None,
                halign='left',
                valign='top',
                font_size=font_size,
                color=COLOR_TEXT,
                padding=(10, 5),
            )
            text_label.bind(size=text_label.setter('text_size'))
            content_layout.add_widget(text_label)

        if db_data.get('description'):
            add_section('【卦辞】', db_data['description'])
        if db_data.get('bai_hua'):
            add_section('【白话解释】', db_data['bai_hua'])
        if db_data.get('guan_xiang'):
            add_section('【卦象分析】', db_data['guan_xiang'])
        if db_data.get('ren_sheng'):
            add_section('【人生启示】', db_data['ren_sheng'])

        if duangua_result:
            add_section('【断卦方法】', duangua_result['duan_gua_method'])
            add_section('动爻数', str(duangua_result['dong_yao_count']))
            if duangua_result.get('zhi_gua'):
                add_section('变卦', duangua_result['zhi_gua'])

        # 爻辞
        yao_ci_list = gua_db.get_yao_ci(gua_name)
        if yao_ci_list:
            yao_section = Label(
                text='【爻辞详解】',
                size_hint_y=None,
                height=dp(28),
                font_size=dp(15),
                color=COLOR_GOLD,
                bold=True,
                halign='left',
            )
            content_layout.add_widget(yao_section)

            for yao in yao_ci_list:
                yao_name = yao['yao_name']
                yao_text = yao['yao_text']
                xiang_text = yao.get('xiang_text', '')

                yao_type = 7
                if '九' in yao_name:
                    yao_type = 9
                elif '六' in yao_name:
                    yao_type = 6

                is_changing = yao_type in [6, 9]
                mark = ' ' if yao_type == 9 else ' ' if yao_type == 6 else ''

                yao_label = Label(
                    text=f'{yao_name}{mark}: {yao_text}',
                    size_hint_y=None,
                    halign='left',
                    valign='top',
                    font_size=dp(14),
                    color=COLOR_TEXT,
                    padding=(10, 3),
                )
                yao_label.bind(size=yao_label.setter('text_size'))
                content_layout.add_widget(yao_label)

                if xiang_text:
                    xiang_label = Label(
                        text=f'象曰：{xiang_text}',
                        size_hint_y=None,
                        halign='left',
                        font_size=dp(12),
                        color=COLOR_TEXT_SECOND,
                        padding=(20, 0),
                    )
                    xiang_label.bind(size=xiang_label.setter('text_size'))
                    content_layout.add_widget(xiang_label)

        scroll.add_widget(content_layout)
        layout.add_widget(scroll)

        close_btn = create_round_button('关闭', font_size=dp(16), height=dp(50))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)

        popup = Popup(
            title='卦象详解',
            title_color=COLOR_GOLD,
            content=layout,
            size_hint=(0.95, 0.9),
            auto_dismiss=False,
            background_color=COLOR_BG,
        )
        popup.open()
    except Exception as e:
        logger.error(f'[ERROR] show_gua_explanation_with_duangua: {e}')
        show_toast(' 显示失败')


# ==================== 手动选卦弹窗（v1.3.0 新版：64卦选择） ====================

def show_manual_select_gua_popup(app):
    """手动选卦弹窗 —— 64卦列表 + 宫位筛选"""
    try:
        all_gua = get_all_gua_with_palace()
        if not all_gua:
            show_toast(' 卦象数据加载失败')
            return

        popup_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        title = Label(
            text='☯ 选择卦象',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18),
            color=COLOR_GOLD,
            bold=True,
        )
        popup_layout.add_widget(title)

        # 宫位筛选
        palaces = ['全部', '乾宫', '坤宫', '震宫', '巽宫', '坎宫', '离宫', '艮宫', '兑宫']
        current_palace = ['全部']

        palace_scroll = ScrollView(size_hint_y=None, height=dp(38), do_scroll_x=True, do_scroll_y=False)
        palace_row = BoxLayout(orientation='horizontal', size_hint=(None, 1), spacing=dp(6),
                               width=dp(38) * len(palaces) + dp(20))
        palace_buttons = []

        for p in palaces:
            btn = Button(
                text=p,
                size_hint=(None, 1),
                width=dp(60),
                font_size=dp(12),
                color=COLOR_TEXT_SECOND,
                background_color=(0, 0, 0, 0),
                background_normal='',
            )
            apply_card_bg(btn, radius=[dp(8), dp(8), dp(8), dp(8)])

            def on_palace(instance, palace_name=p):
                current_palace[0] = palace_name
                for pb in palace_buttons:
                    if pb.text == palace_name:
                        pb.canvas.before.clear()
                        apply_gold_bg(pb, radius=[dp(8), dp(8), dp(8), dp(8)])
                        pb.color = COLOR_BG
                    else:
                        pb.canvas.before.clear()
                        apply_card_bg(pb, radius=[dp(8), dp(8), dp(8), dp(8)])
                        pb.color = COLOR_TEXT_SECOND
                _update_gua_grid(grid, palace_name, all_gua, app, popup)

            btn.bind(on_press=on_palace)
            palace_buttons.append(btn)
            palace_row.add_widget(btn)

        palace_scroll.add_widget(palace_row)
        popup_layout.add_widget(palace_scroll)

        # 64卦网格
        grid_scroll = ScrollView()
        grid = GridLayout(cols=4, spacing=dp(6), size_hint_y=None,
                          row_default_height=dp(55),
                          row_force_default=True)
        grid.bind(minimum_height=grid.setter('height'))
        grid_scroll.add_widget(grid)
        popup_layout.add_widget(grid_scroll)

        # 先创建 Popup（在调用 _update_gua_grid 之前！）
        popup = Popup(
            title='',
            content=popup_layout,
            size_hint=(0.95, 0.85),
            auto_dismiss=True,
            background_color=COLOR_BG,
        )

        # 初始填充（此时 popup 已存在）
        _update_gua_grid(grid, '全部', all_gua, app, popup)

        popup.open()

    except Exception as e:
        logger.error(f'[ERROR] show_manual_select_gua_popup: {e}')
        show_toast(' 弹窗失败')


def _update_gua_grid(grid, palace, all_gua, app, popup):
    """更新卦象网格（带卦象符号）"""
    grid.clear_widgets()

    filtered = all_gua if palace == '全部' else [g for g in all_gua if g['palace'] == palace]

    for gua in filtered:
        # 卡片布局：符号 + 名称 + 宫位
        card = BoxLayout(orientation='vertical', spacing=dp(2), padding=dp(3))
        
        # 卦象符号
        binary = get_binary_from_name(gua['name'])
        if binary:
            mini_gua = MiniGuaWidget(binary_str=binary, size_hint=(None, None), size=(dp(40), dp(36)))
            card.add_widget(mini_gua)
        
        # 卦名
        name_label = Label(
            text=gua['name'],
            font_size=dp(10),
            color=COLOR_GOLD,
            halign='center',
        )
        name_label.bind(size=name_label.setter('text_size'))
        card.add_widget(name_label)
        
        # 创建按钮包裹卡片
        btn = Button(
            text='',
            background_color=(0, 0, 0, 0),
            background_normal='',
        )
        apply_card_bg(btn, radius=[dp(8), dp(8), dp(8), dp(8)])
        btn.add_widget(card)
        
        def on_gua(instance, g_name=gua['name']):
            try:
                if popup and hasattr(popup, 'dismiss'):
                    popup.dismiss()
            except:
                pass
            yao_list = _gua_name_to_yao(g_name)
            if yao_list:
                app.display_gua(yao_list, '手动选卦')
            else:
                show_toast(f' 无法解析 {g_name}')

        btn.bind(on_press=on_gua)
        grid.add_widget(btn)


def _gua_name_to_yao(gua_name):
    """通过卦名生成 6 爻列表"""
    try:
        binary = get_binary_from_name(gua_name)
        if not binary or len(binary) != 6:
            return None
        # 默认都是少阳/少阴（无变爻）
        return [7 if b == '1' else 8 for b in binary]
    except:
        return None


# ==================== 主应用 ====================

class WuaibaguaApp(App):
    """我爱八卦 v1.3.0 主类"""

    def init_android_features(self):
        """延迟初始化 Android 功能"""
        try:
            logger.info('[INFO] 初始化 Android 功能...')
            init_android_clipboard()
        except Exception as e:
            logger.error(f'[ERROR] Android 功能初始化失败：{e}')

    def build(self):
        """构建应用界面"""
        self.title = '我爱八卦'

        Window.clearcolor = COLOR_BG[:3]

        Clock.schedule_once(lambda dt: self.init_android_features(), 0.5)

        # 注册字体（关键修复：必须先注册再使用）
        from pathlib import Path as _Path
        _font_dir = _Path(__file__).parent / 'fonts'
        _font_path = _font_dir / 'NotoSansSC-Regular.ttf'
        if _font_path.exists():
            try:
                LabelBase.register(name='NotoSansSC', fn_regular=str(_font_path))
                logger.info('[INFO] 字体 NotoSansSC 已注册')
            except Exception as _e:
                logger.warning(f'[WARN] 字体注册失败: {_e}')
        else:
            logger.warning(f'[WARN] 字体文件不存在: {_font_path}')

        # ⚠️ 禁止类级别设置 font_name！会覆盖 Kivy AliasProperty 导致 Cython 崩溃
        # 改用 Config 设置全局默认字体（在 Kivy 初始化前生效）
        # Label.font_name = 'NotoSansSC'  ← 删除
        # Button.font_name = 'NotoSansSC'  ← 删除
        # TextInput.font_name = 'NotoSansSC'  ← 删除

        # ========== 自定义 Tab 布局 ==========
        main_layout = BoxLayout(orientation='vertical', padding=0, spacing=0)

        # 顶部标题栏
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            padding=(dp(15), dp(8)),
        )
        with header.canvas.before:
            Color(*COLOR_BG_CARD)
            header._bg_rect = RoundedRectangle(size=header.size, pos=header.pos)
            def _upd(*a):
                header._bg_rect.size = header.size
                header._bg_rect.pos = header.pos
            header.bind(size=_upd, pos=_upd)

        title_label = Label(
            text='☯ 我爱八卦',
            font_size=dp(20),
            color=COLOR_GOLD,
            bold=True,
            halign='left',
        )
        header.add_widget(title_label)

        # 动态标题：根据当前 Tab 变化
        self.header_subtitle = Label(
            text='周易六十四卦 · 卜卦解惑',
            font_size=dp(11),
            color=COLOR_TEXT_SECOND,
            halign='right',
        )
        header.add_widget(self.header_subtitle)
        main_layout.add_widget(header)

        # Tab 导航栏
        tab_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            padding=(dp(4), dp(4)),
            spacing=dp(4),
        )
        with tab_bar.canvas.before:
            Color(*COLOR_BG_CARD)
            tab_bar._bg_rect = RoundedRectangle(size=tab_bar.size, pos=tab_bar.pos)
            def _upd2(*a):
                tab_bar._bg_rect.size = tab_bar.size
                tab_bar._bg_rect.pos = tab_bar.pos
            tab_bar.bind(size=_upd2, pos=_upd2)

        self.tab_buttons = {}
        # Tab 定义
        tab_defs = ['起卦', '64卦', '运势', '设置']

        for name in tab_defs:
            btn = Button(
                text=name,
                font_size=dp(13),
                color=COLOR_TEXT_SECOND,
                background_color=(0, 0, 0, 0),
                background_normal='',
            )
            with btn.canvas.before:
                Color(0, 0, 0, 0)
                btn._bg_rect = RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(8), dp(8), dp(8), dp(8)])
                def _upd_btn(*a, b=btn):
                    b._bg_rect.size = b.size
                    b._bg_rect.pos = b.pos
                btn.bind(size=_upd_btn, pos=_upd_btn)
            self.tab_buttons[name] = btn

        def switch_tab(name):
            for n, b in self.tab_buttons.items():
                b.canvas.before.clear()
                if n == name:
                    with b.canvas.before:
                        Color(*COLOR_GOLD)
                        b._bg_rect = RoundedRectangle(size=b.size, pos=b.pos, radius=[dp(8), dp(8), dp(8), dp(8)])
                        def _upd_gold(*a, bb=b):
                            bb._bg_rect.size = bb.size
                            bb._bg_rect.pos = bb.pos
                        b.bind(size=_upd_gold, pos=_upd_gold)
                    b.color = COLOR_BG
                    b.bold = True
                else:
                    with b.canvas.before:
                        Color(0, 0, 0, 0)
                        b._bg_rect = RoundedRectangle(size=b.size, pos=b.pos, radius=[dp(8), dp(8), dp(8), dp(8)])
                        def _upd_clear(*a, bb=b):
                            bb._bg_rect.size = bb.size
                            bb._bg_rect.pos = bb.pos
                        b.bind(size=_upd_clear, pos=_upd_clear)
                    b.color = COLOR_TEXT_SECOND
                    b.bold = False
            self._switch_content(name)

        for name in tab_defs:
            btn = self.tab_buttons[name]
            btn.bind(on_press=lambda x, n=name: switch_tab(n))
            tab_bar.add_widget(btn)

        main_layout.add_widget(tab_bar)

        # 内容容器（直接放 Tab 内容，不用 ScrollView，避免双重嵌套）
        self.content_container = BoxLayout(orientation='vertical')
        main_layout.add_widget(self.content_container)

        # 构建各 Tab 内容
        self._tab_divination = self._build_divination_tab()
        self._tab_gua64 = self._build_gua64_tab()
        self._tab_fortune = self._build_fortune_tab()
        self._tab_settings = self._build_settings_tab()

        # 默认显示起卦 Tab
        self._current_tab = '起卦'
        self.content_container.add_widget(self._tab_divination)

        # 激活起卦按钮
        self.tab_buttons['起卦'].canvas.before.clear()
        with self.tab_buttons['起卦'].canvas.before:
            Color(*COLOR_GOLD)
            self.tab_buttons['起卦']._bg_rect = RoundedRectangle(
                size=self.tab_buttons['起卦'].size,
                pos=self.tab_buttons['起卦'].pos,
                radius=[dp(8), dp(8), dp(8), dp(8)]
            )
        self.tab_buttons['起卦'].color = COLOR_BG
        self.tab_buttons['起卦'].bold = True

        # 状态
        self.current_gua = None
        self.current_yao_list = None
        self.current_gua_detail = None
        self.current_changing_gua = None
        self.current_image_info = None
        self.current_duangua_result = None

        return main_layout

    def _switch_content(self, name):
        """切换 Tab 内容"""
        tab_map = {
            '起卦': self._tab_divination,
            '64卦': self._tab_gua64,
            '运势': self._tab_fortune,
            '设置': self._tab_settings,
        }
        # 更新副标题
        subtitle_map = {
            '起卦': '周易六十四卦 · 卜卦解惑',
            '64卦': '快速查找 · 点击查看',
            '运势': '每日专属 · 趋吉避凶',
            '设置': '个性化 · 数据管理',
        }
        if hasattr(self, 'header_subtitle'):
            self.header_subtitle.text = subtitle_map.get(name, '')
        self.content_container.clear_widgets()
        widget = tab_map.get(name)
        if widget:
            self.content_container.add_widget(widget)
        self._current_tab = name

    # ---------- 起卦 Tab ----------

    def _build_divination_tab(self):
        """起卦 Tab"""
        # 根布局：紧凑布局，卦象卡片紧贴顶部
        layout = BoxLayout(orientation='vertical', padding=(dp(10), dp(4), dp(10), dp(10)), spacing=dp(6), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # 卦象显示区（紧凑高度，空状态无多余空白）
        self.gua_display_area = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(119),  # 精确：empty_state 90 + spacing 4 + empty_hint 25
            spacing=dp(4),
        )
        apply_card_bg(self.gua_display_area, radius=[dp(14), dp(14), dp(14), dp(14)])

        # 空状态
        self.empty_state = Label(
            text='☯',
            font_size=dp(48),
            color=COLOR_GOLD,
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(90),
        )
        self.empty_state.bind(size=self.empty_state.setter('text_size'))

        self.empty_hint = Label(
            text='选择起卦方式',
            font_size=dp(16),
            color=COLOR_TEXT_SECOND,
            halign='center',
            size_hint_y=None,
            height=dp(25),
        )

        # 初始显示空状态
        self.gua_display_area.add_widget(self.empty_state)
        self.gua_display_area.add_widget(self.empty_hint)

        # 结果状态（紧凑布局，减少顶部空白）
        self.result_state = BoxLayout(orientation='vertical', spacing=dp(4), padding=(dp(10), dp(4)))
        self.result_state.size_hint_y = None
        self.result_state.bind(minimum_height=self.result_state.setter('height'))

        self.gua_name_label = Label(
            text='',
            font_size=dp(26),
            color=COLOR_GOLD,
            bold=True,
            halign='center',
            size_hint_y=None,
            height=dp(36),
        )
        self.result_state.add_widget(self.gua_name_label)

        self.gua_palace_label = Label(
            text='',
            font_size=dp(12),
            color=COLOR_TEXT_SECOND,
            halign='center',
            size_hint_y=None,
            height=dp(20),
        )
        self.result_state.add_widget(self.gua_palace_label)

        # 爻符显示区（加大到 dp(130)，6爻 × dp(18) + spacing + padding）
        self.yao_draw_area = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(130),
            spacing=dp(4),
            padding=(dp(30), dp(5)),
        )
        self.result_state.add_widget(self.yao_draw_area)

        self.gua_ci_label = Label(
            text='',
            font_size=dp(13),
            color=COLOR_TEXT,
            halign='center',
            size_hint_y=None,
            height=dp(40),
        )
        self.gua_ci_label.bind(size=self.gua_ci_label.setter('text_size'))
        self.result_state.add_widget(self.gua_ci_label)

        self.changing_label = Label(
            text='',
            font_size=dp(12),
            color=COLOR_GOLD_LIGHT,
            halign='center',
            size_hint_y=None,
            height=dp(22),
        )
        self.result_state.add_widget(self.changing_label)
        layout.add_widget(self.gua_display_area)

        # 起卦方式 2x2 网格
        method_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(160))

        # 随机起卦
        card1 = create_card_button(' 随机起卦', subtitle='心诚则灵', height=dp(72))
        card1_btn = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='')
        card1_btn.bind(on_press=self.auto_gua)
        card1.add_widget(card1_btn)
        method_grid.add_widget(card1)

        # 手动选卦
        card2 = create_card_button(' 手动选卦', subtitle='64卦列表', height=dp(72))
        card2_btn = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='')
        card2_btn.bind(on_press=self.manual_gua)
        card2.add_widget(card2_btn)
        method_grid.add_widget(card2)

        # 金钱起卦
        card3 = create_card_button(' 金钱起卦', subtitle='模拟摇卦', height=dp(72))
        card3_btn = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='')
        card3_btn.bind(on_press=self.jinqian_gua)
        card3.add_widget(card3_btn)
        method_grid.add_widget(card3)

        # 时间起卦
        card4 = create_card_button(' 时间起卦', subtitle='以时起卦', height=dp(72))
        card4_btn = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='')
        card4_btn.bind(on_press=self.time_gua)
        card4.add_widget(card4_btn)
        method_grid.add_widget(card4)

        layout.add_widget(method_grid)

        # 快捷功能按钮
        quick_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(42), spacing=dp(8))

        qbtn1 = create_round_button(' 卦象解释', font_size=dp(13), height=dp(42))
        qbtn1.bind(on_press=self.show_explanation)
        quick_row.add_widget(qbtn1)

        qbtn2 = create_round_button(' 六爻排盘', font_size=dp(13), height=dp(42))
        qbtn2.bind(on_press=self.show_liuyao)
        quick_row.add_widget(qbtn2)

        qbtn3 = create_round_button(' 分享', font_size=dp(13), height=dp(42))
        qbtn3.bind(on_press=self.share_gua)
        quick_row.add_widget(qbtn3)

        qbtn4 = create_round_button(' 复制', font_size=dp(13), height=dp(42))
        qbtn4.bind(on_press=self.copy_result)
        quick_row.add_widget(qbtn4)

        layout.add_widget(quick_row)

        # 重新起卦按钮
        self.redivide_btn = create_round_button(' 重新起卦', font_size=dp(15), height=dp(45))
        self.redivide_btn.bind(on_press=self.auto_gua)
        self.redivide_btn.opacity = 0
        layout.add_widget(self.redivide_btn)

        return layout

    # ---------- 64卦速查 Tab ----------

    def _build_gua64_tab(self):
        """64卦速查 Tab"""
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # 搜索框
        search_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(42), spacing=dp(8))
        self.gua64_search = TextInput(
            hint_text='搜索卦名...',
            font_size=dp(14),
            font_name='NotoSansSC',
            size_hint_x=1,
            multiline=False,
            background_color=COLOR_BG_CARD,
            foreground_color=COLOR_TEXT,
            hint_text_color=COLOR_TEXT_SECOND,
            cursor_color=COLOR_GOLD,
        )
        self.gua64_search.bind(on_text_validate=self._on_gua64_search)
        search_box.add_widget(self.gua64_search)

        search_btn = create_round_button('搜索', font_size=dp(13), width=dp(60), size_hint_x=None)
        search_btn.bind(on_press=self._on_gua64_search)
        search_box.add_widget(search_btn)
        layout.add_widget(search_box)

        # 宫位筛选
        palaces = ['全部', '乾宫', '坤宫', '震宫', '巽宫', '坎宫', '离宫', '艮宫', '兑宫']
        self.gua64_palace = ['全部']

        palace_scroll = ScrollView(size_hint_y=None, height=dp(38), do_scroll_x=True, do_scroll_y=False)
        palace_row = BoxLayout(orientation='horizontal', size_hint=(None, 1), spacing=dp(6),
                               width=dp(38) * len(palaces) + dp(20))
        self.gua64_palace_btns = []

        for p in palaces:
            btn = Button(
                text=p,
                size_hint=(None, 1),
                width=dp(60),
                font_size=dp(12),
                color=COLOR_TEXT_SECOND,
                background_color=(0, 0, 0, 0),
                background_normal='',
            )
            apply_card_bg(btn, radius=[dp(8), dp(8), dp(8), dp(8)])

            def on_palace(instance, palace_name=p):
                self.gua64_palace[0] = palace_name
                for pb in self.gua64_palace_btns:
                    pb.canvas.before.clear()
                    if pb.text == palace_name:
                        apply_gold_bg(pb, radius=[dp(8), dp(8), dp(8), dp(8)])
                        pb.color = COLOR_BG
                    else:
                        apply_card_bg(pb, radius=[dp(8), dp(8), dp(8), dp(8)])
                        pb.color = COLOR_TEXT_SECOND
                self._refresh_gua64_grid()

            btn.bind(on_press=on_palace)
            self.gua64_palace_btns.append(btn)
            palace_row.add_widget(btn)

        palace_scroll.add_widget(palace_row)
        layout.add_widget(palace_scroll)

        # 激活"全部"按钮
        self.gua64_palace_btns[0].canvas.before.clear()
        apply_gold_bg(self.gua64_palace_btns[0], radius=[dp(8), dp(8), dp(8), dp(8)])
        self.gua64_palace_btns[0].color = COLOR_BG

        # 卦象网格（不再嵌套 ScrollView，外层 content_scroll 已提供滚动）
        self.gua64_grid = GridLayout(
            cols=3, spacing=dp(8), size_hint_y=None,
            row_default_height=dp(80),  # 增加高度：符号dp(36)+卦名+宫位+间距
            row_force_default=True,
        )
        self.gua64_grid.bind(minimum_height=self.gua64_grid.setter('height'))
        layout.add_widget(self.gua64_grid)

        # 加载数据
        self._all_gua_data = get_all_gua_with_palace()
        self._refresh_gua64_grid()

        return layout

    def _on_gua64_search(self, instance):
        """搜索卦象"""
        self._refresh_gua64_grid()

    def _refresh_gua64_grid(self):
        """刷新 64 卦网格（带卦象符号）"""
        self.gua64_grid.clear_widgets()

        query = self.gua64_search.text.strip().lower() if hasattr(self, 'gua64_search') else ''
        palace = self.gua64_palace[0] if hasattr(self, 'gua64_palace') else '全部'

        filtered = self._all_gua_data
        if palace != '全部':
            filtered = [g for g in filtered if g['palace'] == palace]
        if query:
            filtered = [g for g in filtered if query in g['name'].lower()]

        for gua in filtered:
            # 卡片布局：符号 + 名称
            card = BoxLayout(orientation='vertical', spacing=dp(2), padding=dp(3))
            
            # 卦象符号
            binary = get_binary_from_name(gua['name'])
            if binary:
                mini_gua = MiniGuaWidget(binary_str=binary, size_hint=(None, None), size=(dp(40), dp(36)))
                card.add_widget(mini_gua)
            
            # 卦名
            name_label = Label(
                text=gua['name'],
                font_size=dp(10),
                color=COLOR_GOLD,
                halign='center',
            )
            name_label.bind(size=name_label.setter('text_size'))
            card.add_widget(name_label)
            
            # 宫位标签
            palace_label = Label(
                text=gua.get('palace', ''),
                font_size=dp(8),
                color=COLOR_TEXT_SECOND,
                halign='center',
            )
            card.add_widget(palace_label)
            
            # 按钮包裹
            btn = Button(
                text='',
                background_color=(0, 0, 0, 0),
                background_normal='',
            )
            apply_card_bg(btn, radius=[dp(8), dp(8), dp(8), dp(8)])
            btn.add_widget(card)

            def on_gua_detail(instance, g_name=gua['name']):
                self._show_gua_detail_popup(g_name)

            btn.bind(on_press=on_gua_detail)
            self.gua64_grid.add_widget(btn)

    def _show_gua_detail_popup(self, gua_name):
        """显示卦象详情弹窗"""
        try:
            import gua_db
            db_data = gua_db.get_gua_by_name(gua_name)
            if not db_data:
                show_toast(f' 未找到 {gua_name}')
                return

            popup_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

            title = Label(
                text=f'☯ {gua_name}',
                size_hint_y=None,
                height=dp(40),
                font_size=dp(20),
                color=COLOR_GOLD,
                bold=True,
            )
            popup_layout.add_widget(title)

            # 基本信息
            palace = get_gua_palace(gua_name)
            info = f'宫位：{palace}'
            if db_data.get('upper_gua') and db_data.get('lower_gua'):
                info += f'\n上卦：{db_data["upper_gua"]}  下卦：{db_data["lower_gua"]}'
            info_label = Label(
                text=info,
                size_hint_y=None,
                height=dp(40),
                font_size=dp(13),
                color=COLOR_TEXT_SECOND,
                halign='left',
            )
            info_label.bind(size=info_label.setter('text_size'))
            popup_layout.add_widget(info_label)

            scroll = ScrollView()
            content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
            content_layout.bind(minimum_height=content_layout.setter('height'))

            def add_sec(label_text, detail_text, fs=dp(13)):
                sec = Label(
                    text=label_text,
                    size_hint_y=None, height=dp(26),
                    font_size=dp(14), color=COLOR_GOLD, bold=True, halign='left',
                )
                content_layout.add_widget(sec)
                txt = Label(
                    text=detail_text,
                    size_hint_y=None,
                    halign='left', valign='top',
                    font_size=fs, color=COLOR_TEXT, padding=(8, 3),
                )
                txt.bind(size=txt.setter('text_size'))
                content_layout.add_widget(txt)

            if db_data.get('description'):
                add_sec('【卦辞】', db_data['description'])
            if db_data.get('da_xiang'):
                add_sec('【大象】', db_data['da_xiang'])
            if db_data.get('bai_hua'):
                add_sec('【白话解释】', db_data['bai_hua'], dp(12))
            if db_data.get('guan_xiang'):
                add_sec('【卦象分析】', db_data['guan_xiang'], dp(12))

            scroll.add_widget(content_layout)
            popup_layout.add_widget(scroll)

            # 快速起卦按钮
            qi_btn = create_round_button(f' 以此卦起卦', font_size=dp(14), height=dp(45))
            qi_btn.bind(on_press=lambda x, gn=gua_name: self._quick_divine(gn, popup))
            popup_layout.add_widget(qi_btn)

            close_btn = Button(
                text='关闭',
                size_hint_y=None, height=dp(42),
                font_size=dp(14), color=COLOR_TEXT_SECOND,
                background_color=(0, 0, 0, 0), background_normal='',
            )
            close_btn.bind(on_press=lambda x: popup.dismiss())
            popup_layout.add_widget(close_btn)

            popup = Popup(
                title='',
                content=popup_layout,
                size_hint=(0.92, 0.8),
                auto_dismiss=True,
                background_color=COLOR_BG,
            )
            popup.open()
        except Exception as e:
            logger.error(f'[ERROR] _show_gua_detail_popup: {e}')

    def _quick_divine(self, gua_name, popup):
        """从 64 卦速查快速起卦"""
        popup.dismiss()
        yao_list = _gua_name_to_yao(gua_name)
        if yao_list:
            # 切换到起卦 Tab
            self._switch_content('起卦')
            self.tab_buttons['起卦'].canvas.before.clear()
            with self.tab_buttons['起卦'].canvas.before:
                Color(*COLOR_GOLD)
                self.tab_buttons['起卦']._bg_rect = RoundedRectangle(
                    size=self.tab_buttons['起卦'].size,
                    pos=self.tab_buttons['起卦'].pos,
                    radius=[dp(8), dp(8), dp(8), dp(8)]
                )
            self.tab_buttons['起卦'].color = COLOR_BG
            self.tab_buttons['64卦'].canvas.before.clear()
            apply_card_bg(self.tab_buttons['64卦'], radius=[dp(8), dp(8), dp(8), dp(8)])
            self.tab_buttons['64卦'].color = COLOR_TEXT_SECOND
            self.display_gua(yao_list, '手动选卦')
        else:
            show_toast(f' 无法解析 {gua_name}')

    # ---------- 运势 Tab ----------

    def _build_fortune_tab(self):
        """运势 Tab"""
        layout = BoxLayout(orientation='vertical', padding=(dp(10), dp(4), dp(10), dp(10)), spacing=dp(6), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # 今日日期
        today = datetime.now().strftime('%Y年%m月%d日')
        date_label = Label(
            text=f' {today}',
            font_size=dp(15),
            color=COLOR_TEXT_SECOND,
            size_hint_y=None,
            height=dp(28),
            halign='center',
        )
        layout.add_widget(date_label)

        # 运势卡片（极致紧凑，消除空白）
        self.fortune_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(190),  # 紧凑：卦名30 + 爻符90 + 描述40 + padding 20 + spacing 10
            padding=(dp(12), dp(6)),
            spacing=dp(4),
        )
        apply_card_bg(self.fortune_card, radius=[dp(14), dp(14), dp(14), dp(14)])

        self.fortune_gua_name = Label(
            text='点击下方按钮查看今日运势',
            font_size=dp(20),
            color=COLOR_GOLD,
            bold=True,
            halign='center',
            size_hint_y=None,
            height=dp(30),
        )
        self.fortune_card.add_widget(self.fortune_gua_name)

        self.fortune_yao_area = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(90),  # 紧凑：6爻 × dp(12) + spacing
            spacing=dp(3),
            padding=(dp(20), dp(3)),
        )
        self.fortune_card.add_widget(self.fortune_yao_area)

        self.fortune_desc = Label(
            text='',
            font_size=dp(13),
            color=COLOR_TEXT,
            halign='center',
            size_hint_y=None,
            height=dp(60),
        )
        self.fortune_desc.bind(size=self.fortune_desc.setter('text_size'))
        self.fortune_card.add_widget(self.fortune_desc)

        layout.add_widget(self.fortune_card)

        # 按钮
        fortune_btn = create_round_button(' 查看今日运势', font_size=dp(16), height=dp(50))
        fortune_btn.bind(on_press=self.daily_gua)
        layout.add_widget(fortune_btn)

        fortune_actions = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(42), spacing=dp(8))
        fbtn1 = create_round_button(' 详解', font_size=dp(13), height=dp(42))
        fbtn1.bind(on_press=self.show_explanation)
        fortune_actions.add_widget(fbtn1)
        fbtn2 = create_round_button(' 六爻', font_size=dp(13), height=dp(42))
        fbtn2.bind(on_press=self.show_liuyao)
        fortune_actions.add_widget(fbtn2)
        fbtn3 = create_round_button(' 分享', font_size=dp(13), height=dp(42))
        fbtn3.bind(on_press=self.share_gua)
        fortune_actions.add_widget(fbtn3)
        layout.add_widget(fortune_actions)

        return layout

    # ---------- 设置 Tab ----------

    def _build_settings_tab(self):
        """设置 Tab"""
        layout = BoxLayout(orientation='vertical', padding=(dp(10), dp(4), dp(10), dp(10)), spacing=dp(8), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # 版本信息卡片
        version_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=(dp(20), dp(12)),
            spacing=dp(6),
        )
        apply_card_bg(version_card, radius=[dp(14), dp(14), dp(14), dp(14)])

        app_name = Label(
            text='☯ 我爱八卦',
            font_size=dp(20),
            color=COLOR_GOLD,
            bold=True,
            halign='center',
            size_hint_y=None,
            height=dp(28),
        )
        version_card.add_widget(app_name)

        version_info = Label(
            text=f'v{__version__}  ·  周易六十四卦  ·  卜卦解惑',
            font_size=dp(12),
            color=COLOR_TEXT_SECOND,
            halign='center',
            size_hint_y=None,
            height=dp(20),
        )
        version_card.add_widget(version_info)

        layout.add_widget(version_card)

        # 设置选项卡片（必须设置 size_hint_y=None + minimum_height，否则子控件重叠）
        settings_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=(dp(15), dp(10)),
            spacing=dp(8),
        )
        settings_card.bind(minimum_height=settings_card.setter('height'))
        apply_card_bg(settings_card, radius=[dp(14), dp(14), dp(14), dp(14)])

        settings_title = Label(
            text='设置选项',
            font_size=dp(15),
            color=COLOR_GOLD,
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign='left',
        )
        settings_card.add_widget(settings_title)

        # 深色主题开关
        theme_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        theme_label = Label(text='深色主题', font_size=dp(14), color=COLOR_TEXT, halign='left')
        theme_row.add_widget(theme_label)
        from kivy.uix.switch import Switch
        self.theme_switch = Switch(active=True, size_hint_x=None, width=dp(50))
        theme_row.add_widget(Widget())
        theme_row.add_widget(self.theme_switch)
        settings_card.add_widget(theme_row)

        # 保存历史记录
        history_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        history_label = Label(text='保存历史记录', font_size=dp(14), color=COLOR_TEXT, halign='left')
        history_row.add_widget(history_label)
        self.history_switch = Switch(active=True, size_hint_x=None, width=dp(50))
        history_row.add_widget(Widget())
        history_row.add_widget(self.history_switch)
        settings_card.add_widget(history_row)

        # 检查更新
        update_btn = create_round_button(' 检查更新', font_size=dp(13), height=dp(42))
        update_btn.bind(on_press=lambda x: show_toast(' 当前已是最新版本'))
        settings_card.add_widget(update_btn)

        # 意见反馈
        feedback_btn = create_round_button(' 意见反馈', font_size=dp(13), height=dp(42))
        feedback_btn.bind(on_press=lambda x: show_toast(' 请通过 GitHub Issues 反馈'))
        settings_card.add_widget(feedback_btn)

        # 清除缓存
        cache_btn = create_round_button('清除缓存', font_size=dp(13), height=dp(42))
        cache_btn.bind(on_press=lambda x: show_toast(' 缓存已清除'))
        settings_card.add_widget(cache_btn)

        layout.add_widget(settings_card)

        # 功能说明卡片（必须设置 size_hint_y=None + minimum_height，否则子控件重叠）
        features_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=(dp(15), dp(10)),
            spacing=dp(6),
        )
        features_card.bind(minimum_height=features_card.setter('height'))
        apply_card_bg(features_card, radius=[dp(14), dp(14), dp(14), dp(14)])

        feat_title = Label(
            text='功能列表',
            font_size=dp(15),
            color=COLOR_GOLD,
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign='left',
        )
        features_card.add_widget(feat_title)

        features = [
            ' 电脑起卦 —— 随机生成卦象',
            ' 手动选卦 —— 从 64 卦中自由选择',
            ' 金钱起卦 —— 模拟三枚铜钱摇卦',
            ' 时间起卦 —— 根据当前时辰起卦',
            ' 今日运势 —— 每日专属卦象',
            ' 卦象详解 —— 卦辞、爻辞、白话解释',
            ' 六爻排盘 —— 完整排盘信息',
            ' 分享卦象 —— 复制分享给好友',
        ]
        for feat in features:
            feat_label = Label(
                text=feat,
                font_size=dp(12),
                color=COLOR_TEXT,
                halign='left',
                size_hint_y=None,
                height=dp(22),
            )
            features_card.add_widget(feat_label)

        layout.add_widget(features_card)

        return layout

    # ==================== 起卦逻辑 ====================

    def auto_gua(self, instance):
        """电脑起卦"""
        yao_list = [random.randint(6, 9) for _ in range(6)]
        self.display_gua(yao_list, '电脑起卦')

    def manual_gua(self, instance):
        """手动选卦"""
        show_manual_select_gua_popup(self)

    def daily_gua(self, instance):
        """今日运势"""
        yao_list = get_daily_gua()
        self.display_gua(yao_list, '今日运势')

    def jinqian_gua(self, instance):
        """金钱起卦"""
        yao_list = gua_calculator.jinqian_qigua()
        self.display_gua(yao_list, '金钱起卦')

    def time_gua(self, instance):
        """时间起卦"""
        now = datetime.now()
        yao_list = gua_calculator.time_qigua(now.year, now.month, now.day, now.hour, now.minute)
        self.display_gua(yao_list, '时间起卦')

    # ==================== 卦象显示 ====================

    def display_gua(self, yao_list, method):
        """显示卦象"""
        try:
            if GUA_CALC_AVAILABLE:
                text, gua_name, changing_gua_name, image_info = gua_calculator.format_gua_display(yao_list, method)
                self.current_changing_gua = changing_gua_name
                self.current_image_info = image_info
            else:
                text = f'{method}\n\n卦名：未知卦'
                gua_name = '未知卦'
                self.current_changing_gua = None
                image_info = {}

            self.current_gua = gua_name
            self.current_yao_list = yao_list

            # 读取详细数据
            self.current_gua_detail = None
            self.current_duangua_result = None
            if GUA_CALC_AVAILABLE:
                self.current_gua_detail = gua_calculator.get_gua_detail(gua_name)
                self.current_duangua_result = gua_calculator.duangua_logic(yao_list)

            # 更新 UI - 显示结果
            self._show_gua_result(gua_name, yao_list, changing_gua_name)

            # 更新运势 Tab
            self._update_fortune_display(gua_name, yao_list, changing_gua_name)

            show_toast(f' {gua_name}')
        except Exception as e:
            logger.error(f'[ERROR] display_gua: {e}')
            logger.error(traceback.format_exc())
            show_toast(' 显示失败')

    def _show_gua_result(self, gua_name, yao_list, changing_gua_name):
        """更新起卦 Tab 的卦象显示"""
        if not hasattr(self, 'empty_state'):
            return

        # 移除空状态，添加结果状态（动态切换，释放空白空间）
        if self.empty_state.parent:
            self.gua_display_area.remove_widget(self.empty_state)
        if self.empty_hint.parent:
            self.gua_display_area.remove_widget(self.empty_hint)
        if not self.result_state.parent:
            self.gua_display_area.add_widget(self.result_state, index=0)
            # 触发高度重算（加上 gua_display_area 的 spacing）
            Clock.schedule_once(lambda dt: setattr(self.gua_display_area, 'height', self.result_state.minimum_height + dp(4)), 0)

        # 卦名
        self.gua_name_label.text = gua_name

        # 宫位
        palace = get_gua_palace(gua_name)
        self.gua_palace_label.text = palace if palace else ''

        # 画爻符
        self.yao_draw_area.clear_widgets()
        yao_names = ['上', '五', '四', '三', '二', '初']
        for i in range(6):
            yao = yao_list[5 - i]
            is_yang = yao in [7, 9]
            is_changing = yao in [6, 9]
            mark = ' ' if yao == 9 else ' ' if yao == 6 else ''

            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(16),
                spacing=dp(4),
            )

            label = Label(
                text=f'{yao_names[i]}',
                font_size=dp(10),
                color=COLOR_TEXT_SECOND,
                size_hint_x=0.15,
            )
            row.add_widget(label)

            yao_canvas = Label(
                text='───' if is_yang else '- -',
                font_size=dp(14),
                color=COLOR_GOLD_LIGHT if is_changing else COLOR_GOLD,
                halign='center',
                size_hint_x=0.7,
            )
            row.add_widget(yao_canvas)

            mark_label = Label(
                text=mark,
                font_size=dp(11),
                color=COLOR_GOLD_LIGHT,
                size_hint_x=0.15,
            )
            row.add_widget(mark_label)

            self.yao_draw_area.add_widget(row)

        # 卦辞
        if self.current_gua_detail and self.current_gua_detail.get('gua_ci'):
            self.gua_ci_label.text = self.current_gua_detail['gua_ci'][:60]
        else:
            self.gua_ci_label.text = ''

        # 变卦
        if changing_gua_name:
            self.changing_label.text = f'变卦：{changing_gua_name}'
        else:
            self.changing_label.text = ''

        # 显示重新起卦按钮
        self.redivide_btn.opacity = 1

    def _show_empty_state(self):
        """恢复空状态显示（移除结果，显示☯图标）"""
        if not hasattr(self, 'empty_state'):
            return

        # 移除结果状态，添加空状态
        if self.result_state.parent:
            self.gua_display_area.remove_widget(self.result_state)
        if not self.empty_state.parent:
            self.gua_display_area.add_widget(self.empty_state, index=0)
        if not self.empty_hint.parent:
            self.gua_display_area.add_widget(self.empty_hint, index=1)

        # 恢复空状态高度
        self.gua_display_area.height = dp(180)

        # 隐藏重新起卦按钮
        if hasattr(self, 'redivide_btn'):
            self.redivide_btn.opacity = 0

        # 清空结果数据
        self.gua_name_label.text = ''
        self.gua_palace_label.text = ''
        self.gua_ci_label.text = ''
        self.changing_label.text = ''
        self.yao_draw_area.clear_widgets()

    def _update_fortune_display(self, gua_name, yao_list, changing_gua_name):
        """更新运势 Tab 显示"""
        if not hasattr(self, 'fortune_gua_name'):
            return

        self.fortune_gua_name.text = gua_name

        # 画爻符
        self.fortune_yao_area.clear_widgets()
        yao_names = ['上', '五', '四', '三', '二', '初']
        for i in range(6):
            yao = yao_list[5 - i]
            is_yang = yao in [7, 9]
            is_changing = yao in [6, 9]

            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(16),
                spacing=dp(4),
            )
            row.add_widget(Label(
                text=f'{yao_names[i]}',
                font_size=dp(10),
                color=COLOR_TEXT_SECOND,
                size_hint_x=0.15,
            ))
            row.add_widget(Label(
                text='───' if is_yang else '- -',
                font_size=dp(14),
                color=COLOR_GOLD_LIGHT if is_changing else COLOR_GOLD,
                halign='center',
                size_hint_x=0.7,
            ))
            row.add_widget(Label(text='', size_hint_x=0.15))
            self.fortune_yao_area.add_widget(row)

        # 描述
        if self.current_gua_detail and self.current_gua_detail.get('bai_hua'):
            self.fortune_desc.text = self.current_gua_detail['bai_hua'][:100] + '...'
        if changing_gua_name:
            self.fortune_desc.text += f'\n\n变卦：{changing_gua_name}'

    # ==================== 功能按钮 ====================

    def show_explanation(self, instance):
        """显示卦象解释"""
        if not self.current_gua:
            show_toast(' 请先起卦')
            return
        show_gua_explanation_with_duangua(
            self.current_gua,
            self.current_gua_detail,
            self.current_yao_list,
            self.current_changing_gua,
            self.current_duangua_result,
        )

    def show_liuyao(self, instance):
        """显示六爻排盘"""
        if not self.current_gua:
            show_toast(' 请先起卦')
            return
        try:
            from liuyao_paipan import format_liuyao_full
            panduan_text = format_liuyao_full(self.current_yao_list, self.current_gua)
            show_liuyao_popup(panduan_text)
        except Exception as e:
            logger.error(f'[ERROR] show_liuyao: {e}')
            show_toast(' 排盘失败')

    def share_gua(self, instance):
        """分享卦象"""
        if not self.current_gua:
            show_toast(' 请先起卦')
            return

        share_text = f'【{self.current_gua}】\n\n'
        if self.current_yao_list:
            yao_names = ['初', '二', '三', '四', '五', '上']
            for i in range(5, -1, -1):
                yao = self.current_yao_list[i]
                yao_type = '阳' if yao in [7, 9] else '阴'
                mark = ' ' if yao == 9 else ' ' if yao == 6 else ''
                share_text += f'{yao_names[i]}{yao_type}{mark}\n'
        if self.current_changing_gua:
            share_text += f'\n变卦：{self.current_changing_gua}'

        show_share_popup(share_text)

    def copy_result(self, instance):
        """复制卦象"""
        if not self.current_gua:
            show_toast(' 请先起卦')
            return

        text = f'【{self.current_gua}】\n'
        if self.current_yao_list:
            yao_names = ['初', '二', '三', '四', '五', '上']
            for i in range(5, -1, -1):
                yao = self.current_yao_list[i]
                yao_type = '阳' if yao in [7, 9] else '阴'
                mark = ' ' if yao == 9 else ' ' if yao == 6 else ''
                text += f'{yao_names[i]}{yao_type}{mark}\n'
        if self.current_changing_gua:
            text += f'\n变卦：{self.current_changing_gua}'

        copy_to_clipboard(text)
        show_toast(' 已复制')


if __name__ == '__main__':
    WuaibaguaApp().run()
