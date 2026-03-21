#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 金钱卦算卦软件 (Android版)
版本：1.0.1
使用 Kivy 框架，可打包为 Android APK
支持点击卦名跳转百度搜索
"""

import os
import sys
import webbrowser

# 在导入 Kivy 之前设置环境变量（用于 CI/CD 打包）
if os.environ.get('PYINSTALLER_ANALYZE') or os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
    # 设置无头模式，避免初始化 OpenGL
    os.environ['KIVY_NO_ARGS'] = '1'
    os.environ['KIVY_LOG_MODE'] = 'PYTHON'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy import Config
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy import metrics
import random

# 注册中文字体 - 解决 Android/Windows 上汉字显示乱码问题
def register_chinese_font():
    """注册支持中文的字体"""
    import os
    import sys
    
    # 获取应用根目录（兼容打包后的环境）
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的环境
        app_dir = os.path.dirname(sys.executable)
        # PyInstaller 解压目录
        if hasattr(sys, '_MEIPASS'):
            app_dir = sys._MEIPASS
    else:
        # 开发环境
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Windows 系统字体路径
    windows_fonts = [
        'C:/Windows/Fonts/msyh.ttc',      # 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',    # 黑体
        'C:/Windows/Fonts/simsun.ttc',    # 宋体
    ]
    
    # Android 系统字体路径
    android_fonts = [
        '/system/fonts/NotoSansSC-Regular.otf',
        '/system/fonts/DroidSansFallback.ttf',
        '/system/fonts/DroidSansFallbackFull.ttf',
        '/system/fonts/Roboto-Regular.ttf',
    ]
    
    # 应用目录字体（打包后的相对路径）
    app_fonts = [
        os.path.join(app_dir, 'fonts', 'NotoSansSC-Regular.ttf'),
        os.path.join(app_dir, 'fonts', 'SourceHanSansSC-Regular.ttf'),
        os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansSC-Regular.ttf'),
    ]
    
    # 优先级：应用字体 > Windows字体 > Android字体
    all_fonts = app_fonts + windows_fonts + android_fonts
    
    # 尝试注册字体
    font_path = None
    for path in all_fonts:
        if os.path.exists(path):
            font_path = path
            break
    
    if font_path:
        try:
            LabelBase.register(name='Chinese', fn_regular=font_path)
            print(f'[INFO] Registered Chinese font: {font_path}')
        except Exception as e:
            print(f'[WARN] Failed to register font {font_path}: {e}')
            # 尝试使用系统默认字体
            try:
                LabelBase.register(name='Chinese', fn_regular='msyh.ttc')
                print('[INFO] Using fallback: Microsoft YaHei')
            except:
                print('[WARN] Fallback font also failed')
    else:
        print('[WARN] No Chinese font found, using default font')


def register_symbol_font():
    """注册支持八卦符号的字体"""
    # 八卦符号（☰☱☲☳☴☵☶☷）需要特殊字体支持
    # Windows 系统字体 - Segoe UI Symbol 支持八卦符号
    windows_symbol_fonts = [
        'C:/Windows/Fonts/seguisym.ttf',   # Segoe UI Symbol (支持八卦符号)
    ]
    
    # Android 系统字体 - Noto Sans Symbols
    android_symbol_fonts = [
        '/system/fonts/NotoSansSymbols-Regular-VF.ttf',
        '/system/fonts/NotoSansSymbols-Regular.ttf',
    ]
    
    # 应用目录字体
    app_dir = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            app_dir = sys._MEIPASS
        else:
            app_dir = os.path.dirname(sys.executable)
    
    app_symbol_fonts = [
        os.path.join(app_dir, 'fonts', 'seguisym.ttf'),
        os.path.join(app_dir, 'fonts', 'NotoSansSymbols-Regular.ttf'),
    ]
    
    all_symbol_fonts = app_symbol_fonts + windows_symbol_fonts + android_symbol_fonts
    
    font_path = None
    for path in all_symbol_fonts:
        if os.path.exists(path):
            font_path = path
            break
    
    if font_path:
        try:
            LabelBase.register(name='Symbol', fn_regular=font_path)
            print(f'[INFO] Registered Symbol font: {font_path}')
        except Exception as e:
            print(f'[WARN] Failed to register symbol font: {e}')
    else:
        print('[WARN] No Symbol font found, using Chinese font as fallback')
        # 打印调试信息
        print(f'[DEBUG] App dir: {app_dir}')
        print(f'[DEBUG] __file__: {__file__}')
        print(f'[DEBUG] Frozen: {getattr(sys, "frozen", False)}')

# 在导入 Builder 前注册字体
register_chinese_font()
register_symbol_font()

# 配置窗口（Android 上自动全屏）
Config.set('graphics', 'width', '1080')
Config.set('graphics', 'height', '1920')
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'minimum_width', '320')
Config.set('graphics', 'minimum_height', '480')


# ==================== 可点击标签组件 ====================
class ClickableLabel(ButtonBehavior, Label):
    """可点击的标签，用于跳转到网络搜索"""
    
    def __init__(self, **kwargs):
        self.search_query = kwargs.pop('search_query', None)
        super().__init__(**kwargs)
        self.font_name = 'Chinese'
        self.color = (0.2, 0.4, 0.8, 1)  # 蓝色链接颜色
        self.bold = True
        self.markup = True
    
    def on_press(self):
        """点击时跳转到搜索页面"""
        if self.search_query:
            url = f'https://www.baidu.com/s?wd={self.search_query}'
            print(f'[INFO] Opening URL: {url}')
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f'[ERROR] Failed to open browser: {e}')


class SearchButton(Button):
    """搜索按钮"""
    
    def __init__(self, **kwargs):
        self.search_query = kwargs.pop('search_query', None)
        super().__init__(**kwargs)
        self.text = '🔍'
        self.size_hint_x = None
        self.width = dp(40)
        self.font_size = dp(18)
        self.background_color = (0.9, 0.9, 0.95, 1)
    
    def on_press(self):
        if self.search_query:
            url = f'https://www.baidu.com/s?wd={self.search_query}'
            print(f'[INFO] Opening URL: {url}')
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f'[ERROR] Failed to open browser: {e}')


# KV 语言定义界面
KV = '''
#:kivy 2.0
#:import Config kivy.config.Config

# 屏幕适配设置
#:import sm kivy.metrics.dp


# 全局字体设置 - 使用注册的中文字体
<Label>:
    font_name: 'Chinese'

<Button>:
    font_name: 'Chinese'

<Spinner>:
    font_name: 'Chinese'

<ToggleButton>:
    font_name: 'Chinese'

<ClickableLabel>:
    font_name: 'Chinese'
    color: 0.2, 0.4, 0.8, 1
    markup: True

<SearchButton>:
    font_name: 'Chinese'

<YaoButton@ToggleButton>:
    font_size: dp(16)
    size_hint_y: None
    height: dp(40)
    
<GuaDisplay@Label>:
    font_size: dp(20)
    markup: True
    halign: 'center'
    valign: 'middle'
    text_size: self.size
    font_name: 'Chinese'

<MainLayout>:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(10)
    size_hint: (1, 1)
    
    # 标题
    Label:
        text: '我爱八卦'
        font_size: dp(28)
        size_hint_y: None
        height: dp(50)
        bold: True
        
    # 起卦方式
    BoxLayout:
        size_hint_y: None
        height: dp(40)
        
        ToggleButton:
            id: auto_btn
            text: '电脑起卦'
            group: 'method'
            state: 'down'
            on_press: root.set_method('auto')
            
        ToggleButton:
            id: manual_btn
            text: '手动起卦'
            group: 'method'
            on_press: root.set_method('manual')
    
    # 手动输入区域
    GridLayout:
        id: manual_input
        cols: 2
        size_hint_y: None
        height: 0
        spacing: dp(5)
        opacity: 0
    
    # 起卦按钮
    Button:
        text: '开始起卦'
        font_size: dp(20)
        size_hint_y: None
        height: dp(50)
        background_color: 0.55, 0.27, 0.07, 1
        on_press: root.do_divination()
        
    # 卦象显示
    BoxLayout:
        size_hint_y: 0.4
        
        # 本卦
        BoxLayout:
            orientation: 'vertical'
            
            Label:
                text: '本卦'
                font_size: dp(16)
                size_hint_y: None
                height: dp(30)
            
            # 本卦名称（可点击）+ 搜索按钮
            BoxLayout:
                size_hint_y: None
                height: dp(35)
                
                ClickableLabel:
                    id: ben_gua_name
                    text: '未起卦'
                    font_size: dp(18)
                    halign: 'center'
                    valign: 'middle'
                
                SearchButton:
                    id: ben_gua_search
                
            ScrollView:
                Label:
                    id: ben_gua_display
                    text: ''
                    font_size: dp(24)
                    markup: True
                    halign: 'center'
                    valign: 'middle'
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1]
        
        # 变卦
        BoxLayout:
            orientation: 'vertical'
            
            Label:
                text: '变卦'
                font_size: dp(16)
                size_hint_y: None
                height: dp(30)
            
            # 变卦名称（可点击）+ 搜索按钮
            BoxLayout:
                size_hint_y: None
                height: dp(35)
                
                ClickableLabel:
                    id: bian_gua_name
                    text: '无变卦'
                    font_size: dp(18)
                    halign: 'center'
                    valign: 'middle'
                
                SearchButton:
                    id: bian_gua_search
    
    # 动爻信息（可点击）+ 搜索按钮
    BoxLayout:
        size_hint_y: None
        height: dp(35)
        
        ClickableLabel:
            id: dong_yao_info
            text: '动爻：无'
            font_size: dp(16)
            halign: 'left'
            valign: 'middle'
            size_hint_x: 0.85
        
        SearchButton:
            id: dong_yao_search
            size_hint_x: 0.15
        font_size: dp(16)
        size_hint_y: None
        height: dp(30)
        
    # 解卦显示
    ScrollView:
        Label:
            id: jie_gua_display
            text: '点击"开始起卦"开始算卦'
            font_size: dp(16)
            markup: True
            halign: 'left'
            valign: 'top'
            text_size: self.width, None
            size_hint_y: None
            height: max(self.texture_size[1], dp(100))
'''


class GuaData:
    """64卦数据管理"""
    
    # 八卦名称（按先天八卦数序：乾 1 兑 2 离 3 震 4 巽 5 坎 6 艮 7 坤 8）
    BAGUA_NAMES = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']
    
    BAGUA_SYMBOLS = {
        '乾': '☰', '兑': '☱', '离': '☲', '震': '☳',
        '巽': '☴', '坎': '☵', '艮': '☶', '坤': '☷'
    }
    
    # 六十四卦名称
    GUA_NAMES = [
        '乾为天', '天泽履', '天火同人', '天雷无妄', '天风姤', '天水讼', '天山遁', '天地否',
        '泽天夬', '兑为泽', '泽火革', '泽雷随', '泽风大过', '泽水困', '泽山咸', '泽地萃',
        '火天大有', '火泽睽', '离为火', '火雷噬嗑', '火风鼎', '火水未济', '火山旅', '火地晋',
        '雷天大壮', '雷泽归妹', '雷火丰', '震为雷', '雷风恒', '雷水解', '雷山小过', '雷地豫',
        '风天小畜', '风泽中孚', '风火家人', '风雷益', '巽为风', '风水涣', '风山渐', '风地观',
        '水天需', '水泽节', '水火既济', '水雷屯', '水风井', '坎为水', '水山蹇', '水地比',
        '山天大畜', '山泽损', '山火贲', '山雷颐', '山风蛊', '山水蒙', '艮为山', '山地剥',
        '地天泰', '地泽临', '地火明夷', '地雷复', '地风升', '地水师', '地山谦', '坤为地'
    ]
    
    # 卦名到文件名映射
    GUA_TO_FILE = {
        '乾为天': '乾卦', '坤为地': '坤卦', '震为雷': '震卦', '巽为风': '巽卦',
        '坎为水': '坎卦', '离为火': '离卦', '艮为山': '艮卦', '兑为泽': '兑卦',
        '天泽履': '履卦', '天火同人': '同人', '天雷无妄': '无妄卦', '天风姤': '姤卦',
        '天水讼': '讼卦', '天山遁': '遯卦', '天地否': '否卦',
        '泽天夬': '夬卦', '泽火革': '革卦', '泽雷随': '随卦', '泽风大过': '大过卦',
        '泽水困': '困卦', '泽山咸': '咸卦', '泽地萃': '萃卦',
        '火天大有': '大有', '火泽睽': '睽卦', '火雷噬嗑': '噬嗑卦', '火风鼎': '鼎卦',
        '火水未济': '未济卦', '火山旅': '旅卦', '火地晋': '晋卦',
        '雷天大壮': '大壮卦', '雷泽归妹': '归妹卦', '雷火丰': '丰卦', '雷风恒': '恒卦',
        '雷水解': '解卦', '雷山小过': '小过卦', '雷地豫': '豫卦',
        '风天小畜': '小畜卦', '风泽中孚': '中孚卦', '风火家人': '家人卦', '风雷益': '益卦',
        '风水涣': '涣卦', '风山渐': '渐卦', '风地观': '观卦',
        '水天需': '需卦', '水泽节': '节卦', '水火既济': '既济卦', '水雷屯': '屯卦',
        '水风井': '井卦', '水山蹇': '蹇卦', '水地比': '比卦',
        '山天大畜': '大畜卦', '山泽损': '损卦', '山火贲': '贲卦', '山雷颐': '颐卦',
        '山风蛊': '蛊卦', '山水蒙': '蒙卦', '山地剥': '剥卦',
        '地天泰': '泰卦', '地泽临': '临卦', '地火明夷': '明夷卦', '地雷复': '复卦',
        '地风升': '升卦', '地水师': '师卦', '地山谦': '谦卦'
    }
    
    YAO_NAMES = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
    
    def __init__(self):
        # Android 打包时数据文件在 assets 目录
        self.data_dir = self._find_data_dir()
        self.gua_data = {}
        self.load_all_gua()
    
    def _find_data_dir(self):
        """查找数据目录"""
        # 尝试多个可能的位置
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'data'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'),
            'data',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 如果都找不到，返回第一个
        return possible_paths[0]
    
    def load_all_gua(self):
        """加载所有卦象数据"""
        for gua_name in self.GUA_NAMES:
            self.gua_data[gua_name] = self.load_gua_data(gua_name)
    
    def load_gua_data(self, gua_name):
        """加载单个卦象数据"""
        file_name = self.GUA_TO_FILE.get(gua_name, gua_name)
        filename = os.path.join(self.data_dir, f"{file_name}.txt")
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"{gua_name}的数据加载失败: {str(e)}"
        return f"{gua_name}的数据文件不存在"

    def get_gua_info(self, gua_name):
        """获取卦象信息（用于解卦显示）"""
        return self.gua_data.get(gua_name, f"暂无 {gua_name} 的详细解释")


class DivinationEngine:
    """算卦引擎"""
    
    COIN_RESULTS = {
        0: ('老阴', '━ ━×', '阴动', 6),
        1: ('少阳', '━━━', '阳', 7),
        2: ('少阴', '━ ━', '阴', 8),
        3: ('老阳', '━━━○', '阳动', 9)
    }
    
    # 六十四卦表
    LIUSHI_GUA = [
        ['乾为天', '天泽履', '天火同人', '天雷无妄', '天风姤', '天水讼', '天山遁', '天地否'],
        ['泽天夬', '兑为泽', '泽火革', '泽雷随', '泽风大过', '泽水困', '泽山咸', '泽地萃'],
        ['火天大有', '火泽睽', '离为火', '火雷噬嗑', '火风鼎', '火水未济', '火山旅', '火地晋'],
        ['雷天大壮', '雷泽归妹', '雷火丰', '震为雷', '雷风恒', '雷水解', '雷山小过', '雷地豫'],
        ['风天小畜', '风泽中孚', '风火家人', '风雷益', '巽为风', '风水涣', '风山渐', '风地观'],
        ['水天需', '水泽节', '水火既济', '水雷屯', '水风井', '坎为水', '水山蹇', '水地比'],
        ['山天大畜', '山泽损', '山火贲', '山雷颐', '山风蛊', '山水蒙', '艮为山', '山地剥'],
        ['地天泰', '地泽临', '地火明夷', '地雷复', '地风升', '地水师', '地山谦', '坤为地']
    ]
    
    def __init__(self):
        self.gua_data = GuaData()
    
    def cast_by_computer(self):
        """电脑自动起卦"""
        results = []
        for i in range(6):
            coins = [random.randint(0, 1) for _ in range(3)]
            sum_coins = sum(coins)
            results.append(sum_coins)
        return results
    
    def analyze_gua(self, results):
        """分析卦象"""
        yao_list = []
        dong_yao = []
        
        for i, r in enumerate(results):
            name, symbol, yin_yang, number = self.COIN_RESULTS[r]
            is_dong = (r == 0 or r == 3)
            yao_list.append({
                'position': i + 1,
                'name': name,
                'symbol': symbol,
                'yin_yang': yin_yang,
                'number': number,
                'is_dong': is_dong
            })
            if is_dong:
                dong_yao.append(i + 1)
        
        ben_gua = self._get_gua_from_yao(yao_list)
        
        bian_yao_list = []
        for yao in yao_list:
            if yao['is_dong']:
                if '阳' in yao['yin_yang']:
                    new_symbol = '━ ━'
                    new_yin_yang = '阴'
                else:
                    new_symbol = '━━━'
                    new_yin_yang = '阳'
                bian_yao_list.append({
                    'position': yao['position'],
                    'symbol': new_symbol,
                    'yin_yang': new_yin_yang,
                    'is_dong': False
                })
            else:
                bian_yao_list.append(yao.copy())
        
        bian_gua = self._get_gua_from_yao(bian_yao_list) if dong_yao else ben_gua
        
        return {
            'yao_list': yao_list,
            'dong_yao': dong_yao,
            'ben_gua': ben_gua,
            'bian_gua': bian_gua,
            'bian_yao_list': bian_yao_list
        }
    
    def _get_gua_from_yao(self, yao_list):
        """根据六爻确定卦象"""
        upper = self._get_trigram(yao_list[3], yao_list[4], yao_list[5])
        lower = self._get_trigram(yao_list[0], yao_list[1], yao_list[2])
        
        gua_name = self.LIUSHI_GUA[upper][lower]
        return {
            'name': gua_name,
            'upper': upper,
            'lower': lower,
            'upper_name': self.gua_data.BAGUA_NAMES[upper],
            'lower_name': self.gua_data.BAGUA_NAMES[lower]
        }
    
    def _get_trigram(self, yao1, yao2, yao3):
        """根据三爻确定八卦（从下往上：yao1=下爻，yao2=中爻，yao3=上爻）"""
        bit1 = 1 if '阳' in yao1['yin_yang'] else 0  # 下爻
        bit2 = 1 if '阳' in yao2['yin_yang'] else 0  # 中爻
        bit3 = 1 if '阳' in yao3['yin_yang'] else 0  # 上爻
        
        # 先天八卦二进制：上爻*4 + 中爻*2 + 下爻*1
        index = bit3 * 4 + bit2 * 2 + bit1
        
        # 先天八卦映射（索引 = 先天数 - 1）
        # 乾☰111=7→0, 兑☱110=6→1, 离☲101=5→2, 震☳100=4→3
        # 巽☴011=3→4, 坎☵010=2→5, 艮☶001=1→6, 坤☷000=0→7
        trigram_map = {7: 0, 6: 1, 5: 2, 4: 3, 3: 4, 2: 5, 1: 6, 0: 7}
        return trigram_map.get(index, 7)


class MainLayout(BoxLayout):
    """主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = DivinationEngine()
        self.current_result = None
        self.method = 'auto'
        self.yao_spinners = []
        
        # 绑定窗口大小变化事件
        Window.bind(on_resize=self.on_window_resize)
        
        # 延迟初始化界面
        from kivy.clock import Clock
        Clock.schedule_once(self._init_ui)
        Clock.schedule_once(self._adjust_font_size, 0.5)
    
    def on_window_resize(self, window, width, height):
        """窗口大小变化时调整布局"""
        # 根据屏幕高度调整字体大小
        scale = min(width / 360, height / 640)
        base_font_size = dp(16)
        self.font_size = base_font_size * max(0.8, min(1.5, scale))
    
    def _adjust_font_size(self, dt):
        """根据屏幕尺寸调整字体"""
        width, height = Window.size
        scale = min(width / 360, height / 640)
        base_font_size = dp(16)
        self.font_size = base_font_size * max(0.8, min(1.5, scale))
    
    def _init_ui(self, dt):
        """初始化界面"""
        # 创建手动输入的 Spinner
        manual_grid = self.ids['manual_input']
        yao_options = ['老阴(三反)', '少阳(两反一正)', '少阴(两正一反)', '老阳(三正)']
        
        for i in range(6):
            label = Label(text=GuaData.YAO_NAMES[i], size_hint_x=0.3)
            spinner = Spinner(
                text=yao_options[1],
                values=yao_options,
                size_hint_x=0.7
            )
            manual_grid.add_widget(label)
            manual_grid.add_widget(spinner)
            self.yao_spinners.append(spinner)
    
    def set_method(self, method):
        """设置起卦方式"""
        self.method = method
        manual_input = self.ids['manual_input']
        
        if method == 'manual':
            manual_input.height = dp(240)
            manual_input.opacity = 1
        else:
            manual_input.height = 0
            manual_input.opacity = 0
    
    def do_divination(self):
        """执行起卦"""
        try:
            if self.method == 'auto':
                results = self.engine.cast_by_computer()
            else:
                # 手动起卦：获取每个 Spinner 的选中值索引
                results = []
                for i, spinner in enumerate(self.yao_spinners):
                    try:
                        idx = spinner.values.index(spinner.text)
                        results.append(idx)
                    except ValueError:
                        # 如果 text 不在 values 中，使用默认值 1（少阳）
                        print(f"[WARN] Spinner {i} text '{spinner.text}' not in values, using default")
                        results.append(1)
            
            print(f"[DEBUG] 起卦结果：{results}")
            self.current_result = self.engine.analyze_gua(results)
            self.display_result()
            
        except Exception as e:
            import traceback
            error_msg = f"起卦失败：{str(e)}\n\n{traceback.format_exc()}"
            print(f"[ERROR] {error_msg}")
            popup = Popup(
                title='错误',
                content=Label(text=error_msg, markup=True),
                size_hint=(0.8, 0.4)
            )
            popup.open()
    
    def display_result(self):
        """显示结果"""
        if not self.current_result:
            return
        
        result = self.current_result
        
        # 显示本卦
        ben_gua_name = result['ben_gua']['name']
        self.ids['ben_gua_name'].text = f'[u]{ben_gua_name}[/u]'
        self.ids['ben_gua_name'].search_query = f'{ben_gua_name} 卦象详解'
        self.ids['ben_gua_display'].text = self.format_gua_display(result['yao_list'])
        
        # 显示变卦
        if result['dong_yao']:
            bian_gua_name = result['bian_gua']['name']
            self.ids['bian_gua_name'].text = f'[u]{bian_gua_name}[/u]'
            self.ids['bian_gua_name'].search_query = f'{bian_gua_name} 卦象详解'
            self.ids['bian_gua_display'].text = self.format_gua_display(result['bian_yao_list'])
        else:
            self.ids['bian_gua_name'].text = '无变卦'
            self.ids['bian_gua_name'].search_query = None
            self.ids['bian_gua_display'].text = '六爻皆静'
        
        # 显示动爻
        if result['dong_yao']:
            dong_text = f"动爻：第{'、第'.join(map(str, result['dong_yao']))}爻"
            self.ids['dong_yao_info'].text = dong_text
        else:
            self.ids['dong_yao_info'].text = '动爻：无'
        
        # 显示解卦
        self.display_jie_gua()
    
    def format_gua_display(self, yao_list):
        """格式化卦象显示"""
        lines = []
        for yao in reversed(yao_list):
            if 'is_dong' in yao and yao['is_dong']:
                lines.append(f"[color=ff0000]{yao['symbol']}[/color]")
            else:
                lines.append(yao['symbol'])
        return '\n'.join(lines)
    
    def display_jie_gua(self):
        """显示解卦"""
        if not self.current_result:
            return
        
        result = self.current_result
        ben_gua_name = result['ben_gua']['name']
        bian_gua_name = result['bian_gua']['name']
        dong_yao = result['dong_yao']
        yao_list = result['yao_list']
        
        # 更新搜索按钮的查询内容
        self.ids['ben_gua_name'].text = f'[u]{ben_gua_name}[/u]'
        self.ids['ben_gua_name'].search_query = f'{ben_gua_name} 卦象详解'
        self.ids['ben_gua_search'].search_query = f'{ben_gua_name} 卦象详解'
        
        if dong_yao:
            self.ids['bian_gua_name'].text = f'[u]{bian_gua_name}[/u]'
            self.ids['bian_gua_name'].search_query = f'{bian_gua_name} 卦象详解'
            self.ids['bian_gua_search'].search_query = f'{bian_gua_name} 卦象详解'
            self.ids['dong_yao_search'].search_query = f'{ben_gua_name} 动爻'
        else:
            self.ids['bian_gua_name'].text = '无变卦'
            self.ids['bian_gua_name'].search_query = None
            self.ids['bian_gua_search'].search_query = None
            self.ids['dong_yao_search'].search_query = None
        
        ben_gua_data = self.engine.gua_data.get_gua_info(ben_gua_name)
        bian_gua_data = self.engine.gua_data.get_gua_info(bian_gua_name) if dong_yao else ""
        
        # 本卦信息
        text = f"[b]【本卦：{ben_gua_name}】[/b]\n"
        text += f"上卦：{result['ben_gua']['upper_name']} {GuaData.BAGUA_SYMBOLS.get(result['ben_gua']['upper_name'], '')}\n"
        text += f"下卦：{result['ben_gua']['lower_name']} {GuaData.BAGUA_SYMBOLS.get(result['ben_gua']['lower_name'], '')}\n\n"
        
        # 动爻详细信息
        if dong_yao:
            text += "[b]【动爻】[/b]\n"
            for pos in dong_yao:
                yao = yao_list[pos - 1]
                yao_name = GuaData.YAO_NAMES[pos - 1]
                text += f"{yao_name}：{yao['name']} {yao['symbol']}（{yao['yin_yang']}）\n"
            text += "\n"
        
        # 变卦信息
        if dong_yao:
            text += f"[b]【变卦：{bian_gua_name}】[/b]\n"
            text += f"上卦：{result['bian_gua']['upper_name']} {GuaData.BAGUA_SYMBOLS.get(result['bian_gua']['upper_name'], '')}\n"
            text += f"下卦：{result['bian_gua']['lower_name']} {GuaData.BAGUA_SYMBOLS.get(result['bian_gua']['lower_name'], '')}\n\n"
        
        # 断卦规则
        text += "[b]【断卦规则】[/b]\n"
        if not dong_yao:
            text += "六爻皆静，以本卦卦辞占断。\n\n"
        elif len(dong_yao) == 1:
            yao = yao_list[dong_yao[0] - 1]
            text += f"一爻动（第{dong_yao[0]}爻），以动爻爻辞占断。\n"
            text += f"动爻：{yao['name']}，{yao['symbol']}\n\n"
        elif len(dong_yao) == 2:
            yin_count = sum(1 for pos in dong_yao if '阴' in yao_list[pos-1]['yin_yang'])
            text += f"[b]两爻动[/b]（第{dong_yao[0]}、第{dong_yao[1]}爻）\n"
            if yin_count == 1:
                text += "一阴一阳，以阴动爻为主。\n\n"
            else:
                text += f"同{'阴' if yin_count == 2 else '阳'}，以上爻为主。\n\n"
        elif len(dong_yao) == 3:
            text += f"[b]三爻动[/b]（第{dong_yao[0]}、第{dong_yao[1]}、第{dong_yao[2]}爻）\n"
            text += "本卦、变卦卦辞参看，以本卦为主。\n\n"
        elif len(dong_yao) == 4:
            static = [i for i in range(1, 7) if i not in dong_yao]
            text += f"[b]四爻动[/b]，以下静爻（第{static[0]}爻）占断。\n\n"
        elif len(dong_yao) == 5:
            static = [i for i in range(1, 7) if i not in dong_yao][0]
            text += f"[b]五爻动[/b]，以静爻（第{static}爻）占断。\n\n"
        else:
            if ben_gua_name == '乾为天':
                text += "[b]六爻皆动[/b]，以「用九」爻辞占断。\n\n"
            elif ben_gua_name == '坤为地':
                text += "[b]六爻皆动[/b]，以「用六」爻辞占断。\n\n"
            else:
                text += f"[b]六爻皆动[/b]，以变卦（{bian_gua_name}）卦辞占断。\n\n"
        
        text += "─" * 30 + "\n"
        text += ben_gua_data
        
        if dong_yao and bian_gua_data:
            text += "\n" + "─" * 30 + "\n"
            text += f"[b]【变卦解释：{bian_gua_name}】[/b]\n\n"
            text += bian_gua_data
        
        self.ids['jie_gua_display'].text = text


class WoAiBaGuaApp(App):
    """应用程序"""
    
    def build(self):
        self.title = '我爱八卦 v1.0.0'
        Builder.load_string(KV)
        return MainLayout()
    
    def get_application_config(self):
        """配置文件路径"""
        return super().get_application_config()


if __name__ == '__main__':
    WoAiBaGuaApp().run()
