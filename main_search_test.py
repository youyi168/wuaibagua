#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 测试版本（带网络搜索功能）
测试点击卦名跳转到百度搜索
"""

import os
import sys
import webbrowser

# 在导入 Kivy 之前设置环境变量（用于 CI/CD 打包）
if os.environ.get('PYINSTALLER_ANALYZE') or os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
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
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy import Config
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.uix.behaviors import ButtonBehavior
import random

# 注册中文字体
def register_chinese_font():
    """注册支持中文的字体"""
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
    ]
    
    # 应用目录字体
    app_dir = os.path.dirname(os.path.abspath(__file__))
    app_fonts = [
        os.path.join(app_dir, 'fonts', 'NotoSansSC-Regular.ttf'),
    ]
    
    all_fonts = app_fonts + windows_fonts + android_fonts
    
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
            print(f'[WARN] Failed to register font: {e}')


def register_symbol_font():
    """注册支持八卦符号的字体"""
    windows_symbol_fonts = [
        'C:/Windows/Fonts/seguisym.ttf',
    ]
    
    android_symbol_fonts = [
        '/system/fonts/NotoSansSymbols-Regular-VF.ttf',
    ]
    
    app_dir = os.path.dirname(os.path.abspath(__file__))
    app_symbol_fonts = [
        os.path.join(app_dir, 'fonts', 'seguisym.ttf'),
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


register_chinese_font()
register_symbol_font()

# 配置窗口
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', '1')


# ==================== 可点击标签组件 ====================
class ClickableLabel(ButtonBehavior, Label):
    """可点击的标签，用于跳转到网络搜索"""
    
    def __init__(self, **kwargs):
        self.search_url = kwargs.pop('search_url', None)
        self.gua_name = kwargs.pop('gua_name', None)
        super().__init__(**kwargs)
        
        # 设置样式
        self.font_name = 'Chinese'
        self.color = (0.2, 0.4, 0.8, 1)  # 蓝色链接颜色
        self.bold = True
        
        # 添加下划线效果（通过 markup）
        if self.text:
            self.text = f'[u]{self.text}[/u]'
            self.markup = True
    
    def on_press(self):
        """点击时跳转到搜索页面"""
        if self.search_url:
            print(f'[INFO] Opening URL: {self.search_url}')
            webbrowser.open(self.search_url)
        elif self.gua_name:
            url = f'https://www.baidu.com/s?wd={self.gua_name}+卦象详解'
            print(f'[INFO] Opening URL: {url}')
            webbrowser.open(url)


class SearchButton(Button):
    """搜索按钮"""
    
    def __init__(self, **kwargs):
        self.gua_name = kwargs.pop('gua_name', None)
        super().__init__(**kwargs)
        self.text = '🔍'
        self.size_hint_x = None
        self.width = dp(40)
        self.font_size = dp(18)
        self.background_color = (0.9, 0.9, 0.9, 1)
    
    def on_press(self):
        if self.gua_name:
            url = f'https://www.baidu.com/s?wd={self.gua_name}+卦象详解'
            print(f'[INFO] Opening URL: {url}')
            webbrowser.open(url)


# ==================== KV 界面定义 ====================
KV = '''
#:kivy 2.0
#:import dp kivy.metrics.dp

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

<MainLayout>:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(10)
    
    # 标题
    Label:
        text: '我爱八卦 (测试版)'
        font_size: dp(24)
        size_hint_y: None
        height: dp(40)
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
    
    # 卦象显示区域
    BoxLayout:
        size_hint_y: None
        height: dp(180)
        
        # 本卦
        BoxLayout:
            orientation: 'vertical'
            
            Label:
                text: '本卦'
                font_size: dp(14)
                size_hint_y: None
                height: dp(25)
            
            # 本卦名称（可点击）
            BoxLayout:
                size_hint_y: None
                height: dp(35)
                
                ClickableLabel:
                    id: ben_gua_link
                    text: '未起卦'
                    font_size: dp(16)
                    halign: 'center'
                
                SearchButton:
                    id: ben_gua_search
            
            Label:
                id: ben_gua_display
                text: ''
                font_size: dp(20)
                markup: True
                halign: 'center'
                valign: 'middle'
        
        # 变卦
        BoxLayout:
            orientation: 'vertical'
            
            Label:
                text: '变卦'
                font_size: dp(14)
                size_hint_y: None
                height: dp(25)
            
            # 变卦名称（可点击）
            BoxLayout:
                size_hint_y: None
                height: dp(35)
                
                ClickableLabel:
                    id: bian_gua_link
                    text: '无变卦'
                    font_size: dp(16)
                    halign: 'center'
                
                SearchButton:
                    id: bian_gua_search
            
            Label:
                id: bian_gua_display
                text: ''
                font_size: dp(20)
                markup: True
                halign: 'center'
                valign: 'middle'
    
    # 动爻信息（可点击）
    BoxLayout:
        size_hint_y: None
        height: dp(35)
        
        ClickableLabel:
            id: dong_yao_link
            text: '动爻：无'
            font_size: dp(14)
            halign: 'center'
        
        SearchButton:
            id: dong_yao_search
    
    # 解卦显示
    ScrollView:
        Label:
            id: jie_gua_display
            text: '点击"开始起卦"开始算卦\\n\\n点击卦名或搜索按钮可跳转到百度搜索'
            font_size: dp(14)
            markup: True
            halign: 'left'
            valign: 'top'
            text_size: self.width, None
            size_hint_y: None
            height: max(self.texture_size[1], dp(100))
'''


# ==================== 数据类 ====================
class GuaData:
    """64卦数据管理"""
    
    BAGUA_NAMES = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']
    
    BAGUA_SYMBOLS = {
        '乾': '☰', '兑': '☱', '离': '☲', '震': '☳',
        '巽': '☴', '坎': '☵', '艮': '☶', '坤': '☷'
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
    
    YAO_NAMES = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']


class DivinationEngine:
    """算卦引擎"""
    
    COIN_RESULTS = {
        0: ('老阴', '━ ━×', '阴动', 6),
        1: ('少阳', '━━━', '阳', 7),
        2: ('少阴', '━ ━', '阴', 8),
        3: ('老阳', '━━━○', '阳动', 9)
    }
    
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
    
    def cast_by_computer(self):
        results = []
        for i in range(6):
            coins = [random.randint(0, 1) for _ in range(3)]
            sum_coins = sum(coins)
            results.append(sum_coins)
        return results
    
    def analyze_gua(self, results):
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
        upper = self._get_trigram(yao_list[3], yao_list[4], yao_list[5])
        lower = self._get_trigram(yao_list[0], yao_list[1], yao_list[2])
        
        gua_name = self.LIUSHI_GUA[upper][lower]
        return {
            'name': gua_name,
            'upper': upper,
            'lower': lower,
            'upper_name': GuaData.BAGUA_NAMES[upper],
            'lower_name': GuaData.BAGUA_NAMES[lower]
        }
    
    def _get_trigram(self, yao1, yao2, yao3):
        bit1 = 1 if '阳' in yao1['yin_yang'] else 0
        bit2 = 1 if '阳' in yao2['yin_yang'] else 0
        bit3 = 1 if '阳' in yao3['yin_yang'] else 0
        
        index = bit3 * 4 + bit2 * 2 + bit1
        trigram_map = {7: 0, 6: 1, 5: 2, 4: 3, 3: 4, 2: 5, 1: 6, 0: 7}
        return trigram_map.get(index, 7)


# ==================== 主界面 ====================
class MainLayout(BoxLayout):
    """主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = DivinationEngine()
        self.current_result = None
        self.method = 'auto'
        self.yao_spinners = []
        
        from kivy.clock import Clock
        Clock.schedule_once(self._init_ui)
    
    def _init_ui(self, dt):
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
        self.method = method
        manual_input = self.ids['manual_input']
        
        if method == 'manual':
            manual_input.height = dp(240)
            manual_input.opacity = 1
        else:
            manual_input.height = 0
            manual_input.opacity = 0
    
    def do_divination(self):
        try:
            if self.method == 'auto':
                results = self.engine.cast_by_computer()
            else:
                results = []
                for spinner in self.yao_spinners:
                    idx = spinner.values.index(spinner.text)
                    results.append(idx)
            
            print(f'[DEBUG] 起卦结果：{results}')
            self.current_result = self.engine.analyze_gua(results)
            self.display_result()
            
        except Exception as e:
            import traceback
            error_msg = f"起卦失败：{str(e)}\n\n{traceback.format_exc()}"
            print(f"[ERROR] {error_msg}")
    
    def display_result(self):
        """显示结果"""
        if not self.current_result:
            return
        
        result = self.current_result
        ben_gua_name = result['ben_gua']['name']
        bian_gua_name = result['bian_gua']['name']
        dong_yao = result['dong_yao']
        
        # 更新本卦可点击链接
        ben_link = self.ids['ben_gua_link']
        ben_link.text = f'[u]{ben_gua_name}[/u]'
        ben_link.gua_name = ben_gua_name
        ben_link.search_url = f'https://www.baidu.com/s?wd={ben_gua_name}+卦象详解'
        
        # 更新本卦搜索按钮
        ben_search = self.ids['ben_gua_search']
        ben_search.gua_name = ben_gua_name
        
        # 更新卦象显示
        self.ids['ben_gua_display'].text = self.format_gua_display(result['yao_list'])
        
        # 更新变卦
        if dong_yao:
            bian_link = self.ids['bian_gua_link']
            bian_link.text = f'[u]{bian_gua_name}[/u]'
            bian_link.gua_name = bian_gua_name
            bian_link.search_url = f'https://www.baidu.com/s?wd={bian_gua_name}+卦象详解'
            
            bian_search = self.ids['bian_gua_search']
            bian_search.gua_name = bian_gua_name
            
            self.ids['bian_gua_display'].text = self.format_gua_display(result['bian_yao_list'])
        else:
            self.ids['bian_gua_link'].text = '无变卦'
            self.ids['bian_gua_link'].gua_name = None
            self.ids['bian_gua_search'].gua_name = None
            self.ids['bian_gua_display'].text = '六爻皆静'
        
        # 更新动爻
        if dong_yao:
            dong_text = f"动爻：第{'、第'.join(map(str, dong_yao))}爻"
            dong_search_text = ' '.join([f'第{pos}爻' for pos in dong_yao])
            
            dong_link = self.ids['dong_yao_link']
            dong_link.text = f'[u]{dong_text}[/u]'
            dong_link.gua_name = f'{ben_gua_name} {dong_search_text}'
            dong_link.search_url = f'https://www.baidu.com/s?wd={ben_gua_name}+动爻'
            
            self.ids['dong_yao_search'].gua_name = f'{ben_gua_name} 动爻'
        else:
            self.ids['dong_yao_link'].text = '动爻：无'
            self.ids['dong_yao_link'].gua_name = None
            self.ids['dong_yao_search'].gua_name = None
        
        # 更新解卦显示
        self.display_jie_gua()
    
    def format_gua_display(self, yao_list):
        lines = []
        for yao in reversed(yao_list):
            if 'is_dong' in yao and yao['is_dong']:
                lines.append(f"[color=ff0000]{yao['symbol']}[/color]")
            else:
                lines.append(yao['symbol'])
        return '\n'.join(lines)
    
    def display_jie_gua(self):
        if not self.current_result:
            return
        
        result = self.current_result
        ben_gua_name = result['ben_gua']['name']
        bian_gua_name = result['bian_gua']['name']
        dong_yao = result['dong_yao']
        
        text = f"[b]【本卦：{ben_gua_name}】[/b]\n"
        text += f"上卦：{result['ben_gua']['upper_name']} {GuaData.BAGUA_SYMBOLS.get(result['ben_gua']['upper_name'], '')}\n"
        text += f"下卦：{result['ben_gua']['lower_name']} {GuaData.BAGUA_SYMBOLS.get(result['ben_gua']['lower_name'], '')}\n\n"
        
        text += "[b]提示：[/b]点击卦名或🔍按钮可跳转到百度搜索\n\n"
        
        if dong_yao:
            text += f"[b]【变卦：{bian_gua_name}】[/b]\n"
            text += f"上卦：{result['bian_gua']['upper_name']} {GuaData.BAGUA_SYMBOLS.get(result['bian_gua']['upper_name'], '')}\n"
            text += f"下卦：{result['bian_gua']['lower_name']} {GuaData.BAGUA_SYMBOLS.get(result['bian_gua']['lower_name'], '')}\n\n"
        
        self.ids['jie_gua_display'].text = text


# ==================== 应用 ====================
class WoAiBaGuaTestApp(App):
    """测试应用"""
    
    def build(self):
        self.title = '我爱八卦 - 测试版（网络搜索）'
        Builder.load_string(KV)
        return MainLayout()


if __name__ == '__main__':
    WoAiBaGuaTestApp().run()
