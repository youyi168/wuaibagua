#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 金钱卦算卦软件 (Kivy版本)
适用于打包成安卓APK
"""

import random
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, ListProperty


class GuaData:
    """64卦数据管理"""
    
    # 八卦名称
    BAGUA_NAMES = ['乾', '坤', '震', '坎', '艮', '离', '兑', '巽']
    
    # 八卦符号
    BAGUA_SYMBOLS = {
        '乾': '☰', '坤': '☷', '震': '☳', '坎': '☵',
        '艮': '☶', '离': '☲', '兑': '☱', '巽': '☴'
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
    
    # 六十四卦（上卦+下卦）
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
    
    # 卦名到文件名的映射
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
    
    # 六爻名称
    YAO_NAMES = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
    
    def __init__(self):
        # 获取数据目录
        if hasattr(App, 'get_running_app') and App.get_running_app():
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        else:
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        self.gua_data = {}
        self.load_all_gua()
    
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
    
    def get_gua_by_index(self, upper, lower):
        """根据上下卦索引获取卦名"""
        return self.LIUSHI_GUA[upper][lower]
    
    def get_gua_info(self, gua_name):
        """获取卦象详细信息"""
        return self.gua_data.get(gua_name, "数据未找到")


class DivinationEngine:
    """算卦引擎"""
    
    # 铜钱结果映射
    COIN_RESULTS = {
        0: ('老阴', '━ ━×', '阴动', 6),   # 三个反面
        1: ('少阳', '━━━', '阳', 7),      # 两反一正
        2: ('少阴', '━ ━', '阴', 8),      # 两正一反
        3: ('老阳', '━━━○', '阳动', 9)    # 三个正面
    }
    
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


class GuaDisplay(GridLayout):
    """卦象显示组件"""
    
    def __init__(self, title="", **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = 2
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        # 标题
        self.title_label = Label(
            text=title,
            font_size='18sp',
            size_hint_y=None,
            height='30dp',
            color=(0.6, 0.3, 0.1, 1)
        )
        self.add_widget(self.title_label)
        
        # 卦名
        self.gua_name_label = Label(
            text="未起卦",
            font_size='24sp',
            size_hint_y=None,
            height='40dp',
            bold=True,
            color=(0.5, 0.2, 0, 1)
        )
        self.add_widget(self.gua_name_label)
        
        # 六爻显示
        self.yao_labels = []
        for i in range(6):
            label = Label(
                text="",
                font_size='20sp',
                size_hint_y=None,
                height='35dp',
                font_name='DroidSansFallback'
            )
            self.yao_labels.append(label)
            self.add_widget(label)
        
        self.height = 280
    
    def update_display(self, gua_info, yao_list, is_ben_gua=True):
        """更新显示"""
        if gua_info:
            self.gua_name_label.text = gua_info['name']
        
        if yao_list:
            for i, label in enumerate(self.yao_labels):
                yao = yao_list[5 - i]  # 从上爻到初爻
                yao_text = f"{yao['symbol']}  {GuaData.YAO_NAMES[5-i]}"
                if is_ben_gua and yao.get('is_dong'):
                    label.text = f"[color=ff0000]{yao_text} ○[/color]"
                    label.markup = True
                else:
                    label.text = yao_text


class MainScreen(BoxLayout):
    """主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.engine = DivinationEngine()
        self.current_result = None
        
        # 标题
        title = Label(
            text="我爱八卦",
            font_size='32sp',
            size_hint_y=None,
            height='50dp',
            bold=True,
            color=(0.6, 0.3, 0.1, 1)
        )
        self.add_widget(title)
        
        # 起卦按钮区域
        btn_layout = BoxLayout(size_hint_y=None, height='60dp', spacing=10)
        
        self.btn_auto = Button(
            text="电脑起卦",
            font_size='18sp',
            background_color=(0.55, 0.27, 0.07, 1)
        )
        self.btn_auto.bind(on_press=self.on_auto_cast)
        btn_layout.add_widget(self.btn_auto)
        
        self.btn_clear = Button(
            text="清空",
            font_size='18sp',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        self.btn_clear.bind(on_press=self.on_clear)
        btn_layout.add_widget(self.btn_clear)
        
        self.add_widget(btn_layout)
        
        # 卦象显示区域
        gua_layout = BoxLayout(size_hint_y=0.35, spacing=10)
        
        # 本卦
        self.ben_gua_display = GuaDisplay(title="本卦")
        gua_layout.add_widget(self.ben_gua_display)
        
        # 变卦
        self.bian_gua_display = GuaDisplay(title="变卦")
        gua_layout.add_widget(self.bian_gua_display)
        
        self.add_widget(gua_layout)
        
        # 动爻信息
        self.dong_info = Label(
            text="动爻：无",
            font_size='16sp',
            size_hint_y=None,
            height='30dp',
            color=(0.8, 0.2, 0.2, 1)
        )
        self.add_widget(self.dong_info)
        
        # 解卦区域（滚动）
        scroll = ScrollView(size_hint_y=0.4)
        self.result_label = Label(
            text="点击「电脑起卦」开始",
            font_size='14sp',
            size_hint_y=None,
            padding=(10, 10),
            markup=True,
            valign='top'
        )
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        self.result_label.bind(width=lambda *args: self.result_label.setter('text_size')(self.result_label, (self.result_label.width, None)))
        scroll.add_widget(self.result_label)
        self.add_widget(scroll)
    
    def on_auto_cast(self, instance):
        """自动起卦"""
        results = self.engine.cast_by_computer()
        self.current_result = self.engine.analyze_gua(results)
        self.display_result()
    
    def on_clear(self, instance):
        """清空"""
        self.current_result = None
        self.ben_gua_display.update_display(None, None)
        self.ben_gua_display.gua_name_label.text = "未起卦"
        self.bian_gua_display.update_display(None, None)
        self.bian_gua_display.gua_name_label.text = "无变卦"
        self.dong_info.text = "动爻：无"
        self.result_label.text = "点击「电脑起卦」开始"
    
    def display_result(self):
        """显示结果"""
        if not self.current_result:
            return
        
        result = self.current_result
        
        # 显示本卦
        self.ben_gua_display.update_display(
            result['ben_gua'],
            result['yao_list'],
            True
        )
        
        # 显示变卦
        if result['bian_gua']:
            self.bian_gua_display.update_display(
                result['bian_gua'],
                result['bian_yao_list'],
                False
            )
        else:
            self.bian_gua_display.gua_name_label.text = "无变卦（六爻皆静）"
            for label in self.bian_gua_display.yao_labels:
                label.text = ""
        
        # 显示动爻
        if result['dong_yao']:
            dong_text = f"动爻：第{'、第'.join(map(str, result['dong_yao']))}爻"
        else:
            dong_text = "动爻：无"
        self.dong_info.text = dong_text
        
        # 显示解卦
        self.display_jie_gua()
    
    def display_jie_gua(self):
        """显示解卦"""
        result = self.current_result
        ben_gua_name = result['ben_gua']['name']
        dong_yao = result['dong_yao']
        yao_list = result['yao_list']
        
        gua_data = self.engine.gua_data.get_gua_info(ben_gua_name)
        
        text = f"[b]【{ben_gua_name}】[/b]\n"
        text += f"上卦：{result['ben_gua']['upper_name']} {GuaData.BAGUA_SYMBOLS.get(result['ben_gua']['upper_name'], '')}\n"
        text += f"下卦：{result['ben_gua']['lower_name']} {GuaData.BAGUA_SYMBOLS.get(result['ben_gua']['lower_name'], '')}\n\n"
        
        text += "[b]【断卦】[/b]\n"
        
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
                text += f"六爻皆动，看变卦（{result['bian_gua']['name']}）断之。\n"
        
        if result['bian_gua']:
            text += f"\n变卦：{result['bian_gua']['name']}\n"
        
        text += f"\n[b]【卦辞爻辞】[/b]\n{gua_data}"
        
        self.result_label.text = text


class WuaibaguaApp(App):
    """我爱八卦应用"""
    
    def build(self):
        return MainScreen()
    
    def get_application_config(self):
        return super().get_application_config('~/.wuaibagua')


if __name__ == '__main__':
    WuaibaguaApp().run()
