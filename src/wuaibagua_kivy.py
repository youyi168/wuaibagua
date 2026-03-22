#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 金钱卦算卦软件 (Kivy 版本)
版本：v1.1.0
支持 Windows 和 Android 平台
功能：电脑起卦、手动起卦、响应式 UI、网络搜索、历史记录、数据缓存
"""

import random
import os
from urllib.parse import quote
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.clock import Clock

# 导入配置和缓存模块
from config import Config
from history import get_history_manager
from cache import get_cache_manager
from logger import get_logger, info, success
from theme import get_theme_manager
from share import get_share_manager
from compact_gua import CompactGuaDisplay
from copy import copy_to_clipboard
from user import get_user_manager, get_daily_seed
from interpreter import get_interpreter
from quick_topic import create_quick_topic_bar

# Kivy 文本输入组件
from kivy.uix.textinput import TextInput

# 尝试导入 webbrowser（桌面端）
try:
    import webbrowser
    WEBBROWSER_AVAILABLE = True
except ImportError:
    WEBBROWSER_AVAILABLE = False

# 初始化日志
logger = get_logger()

# 打印应用信息
Config.print_info()
success('应用启动成功')


class ResponsiveUI:
    """响应式 UI 工具类 - 根据屏幕尺寸动态计算字体和组件大小"""
    
    BASE_WIDTH = 390    # iPhone 13/14/15 标准版宽度
    BASE_HEIGHT = 844   # iPhone 13/14/15 标准版高度
    
    def __init__(self):
        self.screen_width = Window.width
        self.screen_height = Window.height
        self.scale_factor = self._calculate_scale_factor()
        self.is_desktop = self._check_if_desktop()
    
    def _check_if_desktop(self):
        """判断是否为桌面设备"""
        return (self.screen_width > 1000 and 
                self.screen_width / self.screen_height > 1.3)
    
    def _calculate_scale_factor(self):
        """根据屏幕尺寸计算缩放因子"""
        width_scale = self.screen_width / self.BASE_WIDTH
        height_scale = self.screen_height / self.BASE_HEIGHT
        
        if self.is_desktop:
            return min(height_scale, 2.0)
        else:
            return min(width_scale, height_scale)
    
    def get_font_size(self, base_size=16):
        """动态字体大小"""
        return sp(base_size * self.scale_factor)
    
    def get_dp(self, base_dp=10):
        """动态密度无关像素"""
        return dp(base_dp * self.scale_factor)
    
    def get_height(self, base_height=40):
        """动态组件高度"""
        return dp(base_height * self.scale_factor)
    
    def get_spacing(self, base_spacing=10):
        """动态间距"""
        return dp(base_spacing * self.scale_factor)
    
    def get_padding(self, base_padding=10):
        """动态内边距"""
        return dp(base_padding * self.scale_factor)
    
    def update_scale(self, width, height):
        """窗口大小变化时更新缩放因子"""
        self.screen_width = width
        self.screen_height = height
        old_is_desktop = self.is_desktop
        self.is_desktop = self._check_if_desktop()
        
        if old_is_desktop != self.is_desktop:
            self.scale_factor = self._calculate_scale_factor()
            return True
        else:
            new_scale = self._calculate_scale_factor()
            if abs(new_scale - self.scale_factor) > 0.1:
                self.scale_factor = new_scale
                return True
            return False


class GuaData:
    """64 卦数据管理"""
    
    BAGUA_NAMES = ['乾', '坤', '震', '坎', '艮', '离', '兑', '巽']
    
    BAGUA_SYMBOLS = {
        '乾': '☰', '坤': '☷', '震': '☳', '坎': '☵',
        '艮': '☶', '离': '☲', '兑': '☱', '巽': '☴'
    }
    
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
        '地风升': '升卦', '地水师': '师卦', '地山谦': '谦卦',
        '天水讼': '讼卦'
    }
    
    YAO_NAMES = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
    
    def __init__(self):
        self.data_dir = Config.get_data_dir()
        self.gua_data = {}
        self.cache_manager = get_cache_manager()
        self.load_all_gua()
    
    def load_all_gua(self):
        """加载所有卦象数据（使用缓存）"""
        for gua_name in self.GUA_NAMES:
            self.gua_data[gua_name] = self.load_gua_data(gua_name)
    
    def load_gua_data(self, gua_name):
        """加载单个卦象数据（使用缓存加速）"""
        file_name = self.GUA_TO_FILE.get(gua_name, gua_name)
        filename = os.path.join(self.data_dir, f"{file_name}.txt")
        
        # 使用缓存管理器加载（带缓存）
        return self.cache_manager.get(gua_name, filename)
    
    def get_gua_by_index(self, upper, lower):
        """根据上下卦索引获取卦名"""
        return self.LIUSHI_GUA[upper][lower]
    
    def get_gua_info(self, gua_name):
        """获取卦象详细信息"""
        return self.gua_data.get(gua_name, "数据未找到")


class DivinationEngine:
    """算卦引擎"""
    
    COIN_RESULTS = {
        0: ('老阴', '━ ━×', '阴动', 6),   # 三个反面
        1: ('少阳', '━━━', '阳', 7),      # 两反一正
        2: ('少阴', '━ ━', '阴', 8),      # 两正一反
        3: ('老阳', '━━━○', '阳动', 9)    # 三个正面
    }
    
    def __init__(self):
        self.gua_data = GuaData()
    
    def cast_by_computer(self, seed=None):
        """电脑自动起卦
        
        Args:
            seed: 随机种子（可选），用于每日运势等场景
                   如果提供种子，同一用户同一天会得到相同结果
                   如果不提供，完全随机
        
        Returns:
            6 次投掷结果列表
        """
        if seed is not None:
            # 使用种子（可复现）
            random.seed(seed)
        
        results = []
        for i in range(6):
            coins = [random.randint(0, 1) for _ in range(3)]
            sum_coins = sum(coins)
            results.append(sum_coins)
        
        # 重置种子（避免影响其他随机操作）
        if seed is not None:
            random.seed()
        
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
        
        bian_gua = self._get_gua_from_yao(bian_yao_list) if dong_yao else None
        
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
        
        gua_name = self.gua_data.get_gua_by_index(upper, lower)
        return {
            'name': gua_name,
            'upper': upper,
            'lower': lower,
            'upper_name': self.gua_data.BAGUA_NAMES[upper],
            'lower_name': self.gua_data.BAGUA_NAMES[lower]
        }
    
    def _get_trigram(self, yao1, yao2, yao3):
        """根据三爻确定八卦"""
        bit1 = 1 if '阳' in yao1['yin_yang'] else 0
        bit2 = 1 if '阳' in yao2['yin_yang'] else 0
        bit3 = 1 if '阳' in yao3['yin_yang'] else 0
        
        index = bit3 * 4 + bit2 * 2 + bit1
        trigram_map = {7: 0, 0: 1, 4: 2, 2: 3, 6: 4, 5: 5, 3: 6, 1: 7}
        return trigram_map.get(index, 0)


class ManualCastDialog(Popup):
    """手动起卦对话框"""
    
    def __init__(self, callback, responsive=None, manual_mode=True, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.responsive = responsive or ResponsiveUI()
        self.results = [None] * 6
        self.current_yao = 0
        self.manual_mode = manual_mode
        
        layout = BoxLayout(orientation='vertical', 
                          padding=self.responsive.get_padding(20), 
                          spacing=self.responsive.get_spacing(10))
        
        # 标题
        title = Label(
            text="手动投掷铜钱",
            font_size=self.responsive.get_font_size(20),
            size_hint_y=None,
            height=self.responsive.get_height(45),
            bold=True
        )
        layout.add_widget(title)
        
        # 当前爻位
        self.yao_label = Label(
            text="请投掷第 1 爻（初爻）",
            font_size=self.responsive.get_font_size(18),
            size_hint_y=None,
            height=self.responsive.get_height(40)
        )
        layout.add_widget(self.yao_label)
        
        # 投掷按钮
        btn = Button(
            text="投掷铜钱",
            font_size=self.responsive.get_font_size(18),
            background_color=(0.55, 0.27, 0.07, 1)
        )
        btn.bind(on_press=self.on_throw)
        layout.add_widget(btn)
        
        # 结果显示
        self.result_label = Label(
            text="",
            font_size=self.responsive.get_font_size(16),
            size_hint_y=None,
            height=self.responsive.get_height(40)
        )
        layout.add_widget(self.result_label)
        
        self.content = layout
        self.size_hint = (0.9, 0.5)
        self.title = "手动起卦"
    
    def on_throw(self, instance):
        """投掷铜钱"""
        coins = [random.randint(0, 1) for _ in range(3)]
        result = sum(coins)
        self.results[self.current_yao] = result
        
        name, symbol, yin_yang, number = DivinationEngine.COIN_RESULTS[result]
        self.result_label.text = f"结果：{name} {symbol}"
        
        self.current_yao += 1
        if self.current_yao < 6:
            yao_names = GuaData.YAO_NAMES
            self.yao_label.text = f"请投掷第{self.current_yao + 1}爻（{yao_names[self.current_yao]}）"
        else:
            self.callback(self.results, self.manual_mode)
            self.dismiss()


class GuaDisplay(GridLayout):
    """卦象显示组件 - 响应式版本"""
    
    def __init__(self, title="", responsive=None, **kwargs):
        super().__init__(**kwargs)
        self.responsive = responsive or ResponsiveUI()
        self.cols = 1
        self.spacing = self.responsive.get_spacing(3)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        self.title_label = Label(
            text=title,
            font_size=self.responsive.get_font_size(15),
            size_hint_y=None,
            height=self.responsive.get_height(32),
            color=(0.6, 0.3, 0.1, 1),
            halign='center',
            valign='middle'
        )
        self.add_widget(self.title_label)
        
        self.gua_name_label = Label(
            text="未起卦",
            font_size=self.responsive.get_font_size(24),
            size_hint_y=None,
            height=self.responsive.get_height(50),
            bold=True,
            color=(0.5, 0.2, 0, 1),
            halign='center',
            valign='middle'
        )
        self.add_widget(self.gua_name_label)
        
        self.yao_labels = []
        for i in range(6):
            label = Label(
                text="",
                font_size=self.responsive.get_font_size(19),
                size_hint_y=None,
                height=self.responsive.get_height(42),
                font_name='DroidSansFallback',
                halign='left',
                valign='middle'
            )
            self.yao_labels.append(label)
            self.add_widget(label)
        
        self.height = self.responsive.get_height(300)
    
    def update_display(self, gua_info, yao_list, is_ben_gua=True):
        """更新显示"""
        if gua_info:
            self.gua_name_label.text = gua_info['name']
        
        if yao_list:
            for i, label in enumerate(self.yao_labels):
                yao = yao_list[5 - i]
                yao_text = f"{yao['symbol']}  {GuaData.YAO_NAMES[5-i]}"
                if is_ben_gua and yao.get('is_dong'):
                    label.text = f"[color=ff0000]{yao_text} ○[/color]"
                    label.markup = True
                else:
                    label.text = yao_text


class MainScreen(BoxLayout):
    """主界面 - 响应式版本（支持手动起卦、历史记录）"""
    
    def __init__(self, responsive=None, **kwargs):
        super().__init__(**kwargs)
        self.responsive = responsive or ResponsiveUI()
        self.orientation = 'vertical'
        self.padding = self.responsive.get_padding(12)
        self.spacing = self.responsive.get_spacing(12)
        
        self.engine = DivinationEngine()
        self.current_result = None
        self.manual_mode = False
        self.divination_topic = ''  # 占卜事项
        
        # 用户管理器（个性化运势）
        self.user_manager = get_user_manager()
        user_info = self.user_manager.get_user_info()
        info(f'用户 ID: {user_info["user_id_short"]} (设备：{user_info["device_id"]})')
        
        # 管理器初始化
        self.history_manager = get_history_manager()
        self.theme_manager = get_theme_manager()
        self.share_manager = get_share_manager()
        
        # 日志
        info('主界面初始化完成')
        
        # 标题
        title = Label(
            text="我爱八卦",
            font_size=self.responsive.get_font_size(32),
            size_hint_y=None,
            height=self.responsive.get_height(60),
            bold=True,
            color=(0.6, 0.3, 0.1, 1),
            halign='center',
            valign='middle'
        )
        self.add_widget(title)
        
        # 顶部工具栏（主题切换 + 分享 + 复制 + 历史记录）
        toolbar = BoxLayout(
            size_hint_y=None,
            height=self.responsive.get_height(45),
            spacing=self.responsive.get_spacing(8)
        )
        
        # 主题切换按钮
        self.btn_theme = Button(
            text="🌙 深色" if self.theme_manager.is_light() else "☀️ 浅色",
            font_size=self.responsive.get_font_size(14),
            background_color=(0.3, 0.3, 0.3, 1) if self.theme_manager.is_light() else (0.8, 0.8, 0.8, 1)
        )
        self.btn_theme.bind(on_press=self.on_toggle_theme)
        toolbar.add_widget(self.btn_theme)
        
        # 分享按钮
        self.btn_share = Button(
            text="📤",
            font_size=self.responsive.get_font_size(16),
            background_color=(0.2, 0.5, 0.2, 1),
            size_hint_x=None,
            width=self.responsive.get_height(45)
        )
        self.btn_share.bind(on_press=self.on_share)
        toolbar.add_widget(self.btn_share)
        
        # 复制按钮
        self.btn_copy = Button(
            text="📋",
            font_size=self.responsive.get_font_size(16),
            background_color=(0.3, 0.5, 0.7, 1),
            size_hint_x=None,
            width=self.responsive.get_height(45)
        )
        self.btn_copy.bind(on_press=self.on_copy)
        toolbar.add_widget(self.btn_copy)
        
        # 历史记录按钮
        self.btn_history = Button(
            text="📜",
            font_size=self.responsive.get_font_size(16),
            background_color=(0.4, 0.3, 0.5, 1),
            size_hint_x=None,
            width=self.responsive.get_height(45)
        )
        self.btn_history.bind(on_press=self.on_history)
        toolbar.add_widget(self.btn_history)
        
        self.add_widget(toolbar)
        
        # 占卜事项区域（快捷输入 + 手动输入）
        topic_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=self.responsive.get_height(130),
            spacing=self.responsive.get_spacing(5)
        )
        
        # 快捷事项栏
        self.quick_topic_bar = create_quick_topic_bar(self.on_topic_select)
        topic_layout.add_widget(self.quick_topic_bar)
        
        # 手动输入框
        input_layout = BoxLayout(
            size_hint_y=None,
            height=self.responsive.get_height(40),
            spacing=self.responsive.get_spacing(5)
        )
        
        self.topic_input = TextInput(
            text='',
            hint_text='或手动输入事项...',
            font_size=self.responsive.get_font_size(14),
            multiline=False,
            write_tab=False,
            background_color=(1, 1, 1, 0.95),
            foreground_color=(0, 0, 0, 1),
            padding=(10, 10)
        )
        self.topic_input.bind(on_text_validate=lambda x: self.focus_next())
        input_layout.add_widget(self.topic_input)
        
        # 清空按钮
        clear_topic_btn = Button(
            text='❌',
            font_size=self.responsive.get_font_size(14),
            size_hint_x=None,
            width=self.responsive.get_height(40),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        clear_topic_btn.bind(on_press=lambda x: self.clear_topic())
        input_layout.add_widget(clear_topic_btn)
        
        topic_layout.add_widget(input_layout)
        
        self.add_widget(topic_layout)
        
        # 每日运势按钮
        self.btn_daily = Button(
            text="📅 今日运势",
            font_size=self.responsive.get_font_size(17),
            size_hint_y=None,
            height=self.responsive.get_height(55),
            background_color=(0.6, 0.3, 0.6, 1)
        )
        self.btn_daily.bind(on_press=lambda x: self.on_daily_fortune())
        self.add_widget(self.btn_daily)
        
        # 起卦按钮区域
        btn_layout = BoxLayout(
            size_hint_y=None,
            height=self.responsive.get_height(65),
            spacing=self.responsive.get_spacing(12)
        )
        
        self.btn_auto = Button(
            text="电脑起卦",
            font_size=self.responsive.get_font_size(18),
            background_color=self.theme_manager.get_color('btn_auto')
        )
        self.btn_auto.bind(on_press=self.on_auto_cast)
        btn_layout.add_widget(self.btn_auto)
        
        self.btn_manual = Button(
            text="手动起卦",
            font_size=self.responsive.get_font_size(18),
            background_color=self.theme_manager.get_color('btn_manual')
        )
        self.btn_manual.bind(on_press=self.on_manual_cast)
        btn_layout.add_widget(self.btn_manual)
        
        self.add_widget(btn_layout)
        
        # 清空按钮
        self.btn_clear = Button(
            text="清空",
            font_size=self.responsive.get_font_size(18),
            size_hint_y=None,
            height=self.responsive.get_height(50),
            background_color=self.theme_manager.get_color('btn_clear')
        )
        self.btn_clear.bind(on_press=self.on_clear)
        self.add_widget(self.btn_clear)
        
        # 卦象显示区域（紧凑版）
        self.compact_gua = CompactGuaDisplay(responsive=self.responsive)
        self.add_widget(self.compact_gua)
        
        # 保留旧的 GuaDisplay 用于兼容性（隐藏）
        gua_layout = BoxLayout(
            size_hint_y=0.25,
            spacing=self.responsive.get_spacing(12),
            opacity=0
        )
        self.ben_gua_display = GuaDisplay(title="本卦", responsive=self.responsive)
        gua_layout.add_widget(self.ben_gua_display)
        self.bian_gua_display = GuaDisplay(title="变卦", responsive=self.responsive)
        gua_layout.add_widget(self.bian_gua_display)
        self.add_widget(gua_layout)
        
        # 动爻信息
        self.dong_info = Label(
            text="动爻：无",
            font_size=self.responsive.get_font_size(16),
            size_hint_y=None,
            height=self.responsive.get_height(35),
            color=(0.8, 0.2, 0.2, 1),
            halign='center',
            valign='middle'
        )
        self.add_widget(self.dong_info)
        
        # 解卦区域（滚动）- 增大到 45%
        scroll = ScrollView(
            size_hint_y=0.45,
            do_scroll_x=False,
            scroll_type=['bars', 'content'],
            bar_width=self.responsive.get_dp(4)
        )
        self.result_label = Label(
            text="点击「电脑起卦」或「手动起卦」开始",
            font_size=self.responsive.get_font_size(14),
            size_hint_y=None,
            padding=(self.responsive.get_padding(12), self.responsive.get_padding(12)),
            markup=True,
            valign='top',
            halign='left'
        )
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        self.result_label.bind(
            width=lambda *args: self.result_label.setter('text_size')(
                self.result_label, (self.result_label.width, None)
            )
        )
        scroll.add_widget(self.result_label)
        self.add_widget(scroll)
        
        # 搜索按钮
        search_layout = BoxLayout(
            size_hint_y=None,
            height=self.responsive.get_height(50),
            spacing=self.responsive.get_spacing(10)
        )
        
        self.btn_search = Button(
            text="🔍 百度搜索卦象详解",
            font_size=self.responsive.get_font_size(15),
            background_color=(0.2, 0.5, 0.2, 1)
        )
        self.btn_search.bind(on_press=self.on_search)
        search_layout.add_widget(self.btn_search)
        
        self.add_widget(search_layout)
    
    def on_auto_cast(self, instance, use_daily_seed=False):
        """自动起卦
        
        Args:
            use_daily_seed: 是否使用每日种子（用于每日运势）
        """
        # 保存占卜事项
        topic = self.topic_input.text.strip()
        self.divination_topic = topic
        
        # 起卦
        if use_daily_seed:
            # 每日运势：使用个性化种子
            seed = get_daily_seed()
            results = self.engine.cast_by_computer(seed=seed)
            info(f'每日运势：种子={seed}')
        else:
            # 普通起卦：完全随机
            results = self.engine.cast_by_computer()
        
        self.current_result = self.engine.analyze_gua(results)
        self.display_result()
        
        # 保存到历史记录（包含占卜事项）
        self.history_manager.add_record(
            self.current_result,
            manual_mode=False,
            topic=topic
        )
        
        info(f'电脑起卦：{self.current_result["ben_gua"]["name"]}' + 
             (f' - 事项：{topic}' if topic else '') +
             (f' (每日运势)' if use_daily_seed else ''))
    
    def on_daily_fortune(self, instance):
        """每日运势"""
        # 获取今日日期
        from datetime import datetime
        today = datetime.now()
        date_str = today.strftime('%Y年%m月%d日')
        
        # 使用每日种子起卦
        self.on_auto_cast(instance, use_daily_seed=True)
        
        # 显示提示
        success(f'📅 {date_str} 运势已生成\n（同一用户今日结果相同）')
    
    def on_manual_cast(self, instance):
        """手动起卦"""
        # 保存占卜事项
        topic = self.topic_input.text.strip()
        self.divination_topic = topic
        
        def on_complete(results, manual_mode=True):
            self.current_result = self.engine.analyze_gua(results)
            self.display_result()
            # 保存到历史记录（包含占卜事项）
            self.history_manager.add_record(
                self.current_result,
                manual_mode=manual_mode,
                topic=topic
            )
            info(f'手动起卦：{self.current_result["ben_gua"]["name"]}' + 
                 (f' - 事项：{topic}' if topic else ''))
        
        dialog = ManualCastDialog(on_complete, self.responsive, manual_mode=True)
        dialog.open()
    
    def on_clear(self, instance):
        """清空"""
        self.current_result = None
        self.ben_gua_display.update_display(None, None)
        self.ben_gua_display.gua_name_label.text = "未起卦"
        self.bian_gua_display.update_display(None, None)
        self.bian_gua_display.gua_name_label.text = "无变卦"
        self.dong_info.text = "动爻：无"
        self.result_label.text = "点击「电脑起卦」或「手动起卦」开始"
    
    def on_toggle_theme(self, instance):
        """切换主题（完全应用）"""
        new_theme = self.theme_manager.toggle_theme()
        theme = self.theme_manager.get_theme()
        
        # 更新按钮文字和颜色
        if new_theme == 'dark':
            self.btn_theme.text = "☀️ 浅色"
            self.btn_theme.background_color = theme['bg_tertiary']
            self.btn_theme.color = theme['text_primary']
            info('已切换到深色模式')
        else:
            self.btn_theme.text = "🌙 深色"
            self.btn_theme.background_color = theme['bg_secondary']
            self.btn_theme.color = theme['text_primary']
            info('已切换到浅色模式')
        
        # 应用主题到所有组件
        self._apply_theme()
        
        success(f'主题已切换：{self.theme_manager.get_theme_name()}')
    
    def _apply_theme(self):
        """应用当前主题到所有 UI 组件"""
        theme = self.theme_manager.get_theme()
        
        # 背景色
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*theme['bg_primary'])
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        
        # 标题颜色
        for child in self.children:
            if isinstance(child, Label):
                child.color = theme['text_primary']
            elif isinstance(child, Button):
                child.color = theme['text_primary']
        
        # 强制刷新
        self.canvas.ask_update()
    
    def on_copy(self, instance):
        """复制卦象结果"""
        if not self.current_result:
            info('复制失败：没有起卦结果')
            return
        
        # 生成完整文本
        text = self._generate_full_text()
        
        # 复制到剪贴板
        if copy_to_clipboard(text):
            success('✅ 已复制到剪贴板')
    
    def _generate_full_text(self):
        """生成完整卦象文本"""
        if not self.current_result:
            return ''
        
        result = self.current_result
        ben_gua = result.get('ben_gua', {})
        bian_gua = result.get('bian_gua')
        dong_yao = result.get('dong_yao', [])
        topic = getattr(self, 'divination_topic', '')
        
        text = f"【{Config.APP_NAME}】起卦结果\n\n"
        from datetime import datetime
        text += f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        if topic:
            text += f"📝 事项：{topic}\n\n"
        
        text += f"🔮 本卦：{ben_gua.get('name', '未知')}\n"
        
        if bian_gua:
            text += f"🔄 变卦：{bian_gua.get('name')}\n"
        else:
            text += f"🔄 变卦：无（六爻皆静）\n"
        
        if dong_yao:
            yao_names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
            dong_text = '、'.join([yao_names[i-1] for i in dong_yao])
            text += f"⚡ 动爻：{dong_text}\n"
        
        text += f"\n—— {Config.APP_NAME} v{Config.VERSION}"
        
        return text
    
    def on_share(self, instance):
        """分享卦象结果"""
        if not self.current_result:
            info('分享失败：没有起卦结果')
            return
        
        # 使用系统分享菜单
        self.share_manager.share_system(self.current_result)
        info('已打开分享菜单')
    
    def on_history(self, instance):
        """打开历史记录"""
        try:
            from history_screen import HistoryScreen
            from kivy.factory import Factory
            
            # 注册屏幕
            Factory.register('HistoryScreen', cls=HistoryScreen)
            
            # 获取屏幕管理器
            app = Factory.App.get_running_app()
            if app and hasattr(app, 'screen_manager'):
                app.screen_manager.current = 'history'
            else:
                # 如果没有屏幕管理器，显示简单提示
                info('历史记录功能开发中...')
        except Exception as e:
            error(f'打开历史记录失败：{e}')
    
    def on_topic_select(self, topic):
        """选择快捷事项"""
        self.topic_input.text = topic
        info(f'选择事项：{topic}')
    
    def clear_topic(self):
        """清空事项"""
        self.topic_input.text = ''
        self.divination_topic = ''
        info('已清空事项')
    
    def focus_next(self):
        """输入框回车后聚焦到起卦按钮"""
        self.btn_auto.focus = True
    
    def on_search(self, instance):
        """打开百度搜索（带占卜事项）"""
        if not self.current_result:
            return
        
        gua_name = self.current_result['ben_gua']['name']
        
        # 获取占卜事项
        topic = self.topic_input.text.strip()
        self.divination_topic = topic
        
        # 构建搜索关键词
        if topic:
            # 有占卜事项：包含卦名 + 事项
            query = f"周易 {gua_name} {topic} 详解"
            info(f'搜索：{query}')
        else:
            # 无占卜事项：只搜索卦名
            query = f"周易 {gua_name} 详解"
        
        url = f"https://www.baidu.com/s?wd={quote(query)}"
        
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            PythonActivity.mActivity.startActivity(intent)
        except:
            if WEBBROWSER_AVAILABLE:
                webbrowser.open(url)
    
    def display_result(self):
        """显示结果"""
        if not self.current_result:
            return
        
        result = self.current_result
        
        # 使用紧凑卦象显示
        self.compact_gua.update_display(result)
        
        # 显示动爻
        if result['dong_yao']:
            dong_text = f"动爻：第{'、第'.join(map(str, result['dong_yao']))}爻"
        else:
            dong_text = "动爻：无"
        self.dong_info.text = dong_text
        
        self.display_jie_gua()
    
    def display_jie_gua(self):
        """显示解卦（智能解读版）"""
        result = self.current_result
        topic = self.divination_topic
        
        # 使用智能解读器
        interpreter = get_interpreter()
        text = interpreter.interpret(result, topic)
        
        # 添加传统卦辞爻辞
        text += "\n"
        text += "[b]▌完整卦辞爻辞[/b]\n"
        
        ben_gua = result['ben_gua']
        ben_gua_name = ben_gua['name']
        ben_gua_data = self.engine.gua_data.get_gua_info(ben_gua_name)
        text += ben_gua_data
        
        self.result_label.text = text
        
        # ========== 1. 本卦变卦对比 ==========
        text += "[b]▌本卦 ⇄ 变卦[/b]\n"
        text += f"[b]{ben_gua_name}[/b] ䷀ ⇄  "
        
        if bian_gua:
            bian_gua_name = bian_gua['name']
            text += f"[b]{bian_gua_name}[/b]\n"
            
            # 卦象结构对比
            text += f"上{ben_gua['upper_name']}{GuaData.BAGUA_SYMBOLS.get(ben_gua['upper_name'], '')} → 上{bian_gua['upper_name']}{GuaData.BAGUA_SYMBOLS.get(bian_gua['upper_name'], '')}\n"
            text += f"下{ben_gua['lower_name']}{GuaData.BAGUA_SYMBOLS.get(ben_gua['lower_name'], '')} → 下{bian_gua['lower_name']}{GuaData.BAGUA_SYMBOLS.get(bian_gua['lower_name'], '')}\n"
        else:
            text += "无变卦（六爻皆静）\n"
        
        text += "\n"
        
        # ========== 2. 卦辞对比 ==========
        text += "[b]▌卦辞对比[/b]\n"
        text += f"[b]本卦【{ben_gua_name}】[/b]\n"
        
        # 提取卦辞（第一行）
        ben_lines = ben_gua_data.strip().split('\n')
        if ben_lines:
            text += f"{ben_lines[0]}\n"
            # 查找白话解释
            for i, line in enumerate(ben_lines):
                if '【白话】' in line and i < 3:
                    text += f"{line}\n"
                    break
        
        if bian_gua:
            bian_gua_name = bian_gua['name']
            bian_gua_data = self.engine.gua_data.get_gua_info(bian_gua_name)
            text += f"\n[b]变卦【{bian_gua_name}】[/b]\n"
            bian_lines = bian_gua_data.strip().split('\n')
            if bian_lines:
                text += f"{bian_lines[0]}\n"
                for i, line in enumerate(bian_lines):
                    if '【白话】' in line and i < 3:
                        text += f"{line}\n"
                        break
        
        text += "\n"
        
        # ========== 3. 断卦规则 ==========
        if not dong_yao:
            text += "六爻皆静，以本卦卦辞断之。\n"
        elif len(dong_yao) == 1:
            yao_pos = dong_yao[0]
            yao_name = GuaData.YAO_NAMES[yao_pos - 1]
            text += f"一爻动（{yao_name}），以动爻爻辞断之。\n"
        elif len(dong_yao) == 2:
            yin_count = sum(1 for p in dong_yao if '阴' in yao_list[p-1]['yin_yang'])
            if yin_count == 1:
                text += "两爻动（一阴一阳），以阴爻为主。\n"
            else:
                text += f"两爻动（同{'阴' if yin_count == 2 else '阳'}），以上爻为主。\n"
        elif len(dong_yao) == 3:
            text += f"三爻动，取中间爻（第{dong_yao[1]}爻）断之。\n"
        elif len(dong_yao) == 4:
            static = [i for i in range(1,7) if i not in dong_yao]
            text += f"四爻动，看下静爻（第{static[0]}爻）断之。\n"
        elif len(dong_yao) == 5:
            static = [i for i in range(1,7) if i not in dong_yao][0]
            text += f"五爻动，看静爻（第{static}爻）断之。\n"
        else:
            if ben_gua_name == '乾为天':
                text += "六爻皆动，乾卦用「用九」断之。\n"
            elif ben_gua_name == '坤为地':
                text += "六爻皆动，坤卦用「用六」断之。\n"
            else:
                text += f"六爻皆动，看变卦（{bian_gua['name'] if bian_gua else '无'}）断之。\n"
        
        text += "\n"
        
        # ========== 4. 动爻详解 ==========
        if dong_yao:
            text += "[b]▌动爻详解[/b]\n"
            
            for yao_pos in dong_yao:
                idx = yao_pos - 1  # 索引从 0 开始
                yao_name = GuaData.YAO_NAMES[idx]
                ben_yao = yao_list[idx]
                
                text += f"\n[b]{yao_name}[/b]\n"
                
                # 本卦爻辞
                text += f"本：{ben_yao['name']} {ben_yao['symbol']}\n"
                
                # 查找爻辞原文
                for line in ben_lines:
                    if yao_name in line and ('九' in yao_name or '六' in yao_name):
                        text += f"{line}\n"
                        # 查找白话
                        ben_idx = ben_lines.index(line)
                        for j in range(ben_idx + 1, min(ben_idx + 3, len(ben_lines))):
                            if '【白话】' in ben_lines[j]:
                                text += f"{ben_lines[j]}\n"
                                break
                        break
                
                # 变卦爻辞（如果有变化）
                if bian_gua and idx < len(bian_yao_list):
                    bian_yao = bian_yao_list[idx]
                    if ben_yao['yin_yang'] != bian_yao['yin_yang']:
                        text += f"变：{bian_yao['name']} {bian_yao['symbol']}\n"
                        # 查找变卦爻辞
                        bian_gua_name = bian_gua['name']
                        bian_gua_data = self.engine.gua_data.get_gua_info(bian_gua_name)
                        bian_lines = bian_gua_data.strip().split('\n')
                        for line in bian_lines:
                            if yao_name in line:
                                text += f"{line}\n"
                                bian_idx = bian_lines.index(line)
                                for j in range(bian_idx + 1, min(bian_idx + 3, len(bian_lines))):
                                    if '【白话】' in bian_lines[j]:
                                        text += f"{bian_lines[j]}\n"
                                        break
                                break
                
                # 解读
                text += f"[i]【解读】[/i]"
                if '阳' in ben_yao['yin_yang'] and '阴' in bian_yao['yin_yang'] if bian_gua and idx < len(bian_yao_list) else False:
                    text += "阳变阴，表示由刚转柔，宜退守...\n"
                elif '阴' in ben_yao['yin_yang'] and '阳' in bian_yao['yin_yang'] if bian_gua and idx < len(bian_yao_list) else False:
                    text += "阴变阳，表示由柔转刚，宜进取...\n"
                else:
                    text += "此爻变动，需结合卦象综合判断...\n"
        
        text += "\n"
        
        # ========== 5. 完整爻辞 ==========
        text += "[b]▌完整爻辞（本卦）[/b]\n"
        text += f"{gua_data}"
        
        self.result_label.text = text


class WuaibaguaApp(App):
    """我爱八卦应用 - 响应式版本"""
    
    def build(self):
        self.responsive = ResponsiveUI()
        return MainScreen(responsive=self.responsive)
    
    def on_start(self):
        Window.bind(on_resize=self.on_window_resize)
    
    def on_window_resize(self, window, width, height):
        if self.responsive.update_scale(width, height):
            Clock.schedule_once(lambda dt: self.update_ui_scale(), 0.15)
    
    def update_ui_scale(self):
        pass
    
    def get_application_config(self):
        return super().get_application_config('~/.wuaibagua')


if __name__ == '__main__':
    WuaibaguaApp().run()
