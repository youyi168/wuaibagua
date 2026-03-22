#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧凑卦象显示组件
使用 64 卦 Unicode 符号，优化空间占用
版本：v1.2.5
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.metrics import dp, sp


# ========== 64 卦 Unicode 符号表 ==========
# Unicode 编码：U+4DC0 到 U+4DFF (䷀ 到 ䷿)
HEXAGRAM_SYMBOLS = {
    '乾为天': '䷀', '坤为地': '䷁', '水雷屯': '䷂', '山水蒙': '䷃',
    '水天需': '䷄', '天水讼': '䷅', '地水师': '䷆', '水地比': '䷇',
    '风天小畜': '䷈', '天泽履': '䷉', '地天泰': '䷊', '天地否': '䷋',
    '天火同人': '䷌', '火天大有': '䷍', '地山谦': '䷎', '雷地豫': '䷏',
    '泽雷随': '䷐', '山风蛊': '䷑', '地泽临': '䷒', '风地观': '䷓',
    '火雷噬嗑': '䷔', '山火贲': '䷕', '山地剥': '䷖', '地雷复': '䷗',
    '天雷无妄': '䷘', '山天大畜': '䷙', '山雷颐': '䷚', '泽风大过': '䷛',
    '坎为水': '䷜', '离为火': '䷝', '泽山咸': '䷞', '雷风恒': '䷟',
    '天山遁': '䷠', '雷天大壮': '䷡', '火地晋': '䷢', '地火明夷': '䷣',
    '风火家人': '䷤', '火泽睽': '䷥', '水山蹇': '䷦', '雷水解': '䷧',
    '山泽损': '䷨', '风雷益': '䷩', '泽天夬': '䷪', '天风姤': '䷫',
    '泽地萃': '䷬', '地风升': '䷭', '泽水困': '䷮', '水风井': '䷯',
    '泽火革': '䷰', '火风鼎': '䷱', '震为雷': '䷲', '艮为山': '䷳',
    '风山渐': '䷴', '雷泽归妹': '䷵', '雷火丰': '䷶', '火山旅': '䷷',
    '巽为风': '䷸', '兑为泽': '䷹', '风水涣': '䷺', '水泽节': '䷻',
    '风泽中孚': '䷼', '雷山小过': '䷽', '水火既济': '䷾', '火水未济': '䷿'
}

# 八卦符号
TRIGRAM_SYMBOLS = {
    '乾': '☰', '兑': '☱', '离': '☲', '震': '☳',
    '巽': '☴', '坎': '☵', '艮': '☶', '坤': '☷'
}

# 爻符号
YAO_SYMBOLS = {
    '阳': '⚊',      # 阳爻
    '阴': '⚋',      # 阴爻
    '阳动': '⚊ ○',  # 老阳（带圈）
    '阴动': '⚋ ×',  # 老阴（带叉）
}


class CompactGuaDisplay(BoxLayout):
    """紧凑卦象显示组件 - 方案 C"""
    
    def __init__(self, responsive=None, **kwargs):
        super().__init__(**kwargs)
        self.responsive = responsive
        self.orientation = 'vertical'
        self.spacing = dp(5)
        self.size_hint_y = None
        
        # 计算总高度
        self.height = (
            dp(35) +   # 卦名行
            dp(60) +   # 卦符号行
            dp(80) +   # 六爻网格（3 行 x 25dp + 间距）
            dp(30)     # 动爻行
        )
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        # 1. 卦名行
        self.gua_name_label = Label(
            text="本卦：未起卦 → 变卦：无",
            font_size=self._get_font_size(16),
            size_hint_y=None,
            height=dp(35),
            bold=True,
            color=(0.5, 0.2, 0, 1)
        )
        self.add_widget(self.gua_name_label)
        
        # 2. 卦符号行
        self.gua_symbol_label = Label(
            text="䷀ 乾 ☰ 上 ☰ 下",
            font_size=self._get_font_size(22),
            size_hint_y=None,
            height=dp(60),
            color=(0.6, 0.3, 0.1, 1)
        )
        self.add_widget(self.gua_symbol_label)
        
        # 3. 六爻网格（3 行 2 列）
        self.yao_grid = GridLayout(
            cols=2,
            rows=3,
            spacing=dp(5),
            size_hint_y=None,
            height=dp(80)
        )
        
        self.yao_labels = []
        for i in range(6):
            label = Label(
                text="",
                font_size=self._get_font_size(15),
                halign='left',
                valign='middle',
                markup=True
            )
            self.yao_labels.append(label)
            self.yao_grid.add_widget(label)
        
        self.add_widget(self.yao_grid)
        
        # 4. 动爻信息行
        self.dong_yao_label = Label(
            text="动爻：无",
            font_size=self._get_font_size(15),
            size_hint_y=None,
            height=dp(30),
            color=(0.8, 0.2, 0.2, 1),
            bold=True
        )
        self.add_widget(self.dong_yao_label)
    
    def _get_font_size(self, base_size):
        """获取字体大小（支持响应式）"""
        if self.responsive:
            return self.responsive.get_font_size(base_size)
        return sp(base_size)
    
    def update_display(self, result):
        """更新卦象显示
        
        Args:
            result: 起卦结果字典
        """
        if not result:
            self._clear_display()
            return
        
        ben_gua = result.get('ben_gua', {})
        bian_gua = result.get('bian_gua')
        yao_list = result.get('yao_list', [])
        dong_yao = result.get('dong_yao', [])
        
        # 1. 更新卦名
        ben_name = ben_gua.get('name', '未知')
        bian_name = bian_gua.get('name') if bian_gua else '无'
        self.gua_name_label.text = f"本卦：{ben_name} → 变卦：{bian_name}"
        
        # 2. 更新卦符号
        ben_symbol = HEXAGRAM_SYMBOLS.get(ben_name, '')
        upper_name = ben_gua.get('upper_name', '')
        lower_name = ben_gua.get('lower_name', '')
        upper_symbol = TRIGRAM_SYMBOLS.get(upper_name, '')
        lower_symbol = TRIGRAM_SYMBOLS.get(lower_name, '')
        
        self.gua_symbol_label.text = f"{ben_symbol} {upper_name}{upper_symbol} 上 {lower_name}{lower_symbol} 下"
        
        # 3. 更新六爻（从下到上，分 3 行显示）
        # 第 1 行：初爻、二爻
        # 第 2 行：三爻、四爻
        # 第 3 行：五爻、上爻
        yao_pairs = [
            (0, 1),  # 初爻、二爻
            (2, 3),  # 三爻、四爻
            (4, 5),  # 五爻、上爻
        ]
        
        for row_idx, (yao1_idx, yao2_idx) in enumerate(yao_pairs):
            if yao1_idx < len(yao_list):
                yao1 = yao_list[yao1_idx]
                text1 = self._format_yao_text(yao1, yao1_idx)
                self.yao_labels[row_idx * 2].text = text1
            
            if yao2_idx < len(yao_list):
                yao2 = yao_list[yao2_idx]
                text2 = self._format_yao_text(yao2, yao2_idx)
                self.yao_labels[row_idx * 2 + 1].text = text2
        
        # 4. 更新动爻信息
        if dong_yao:
            yao_names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
            dong_names = [yao_names[i-1] for i in dong_yao]
            self.dong_yao_label.text = f"动爻：{', '.join(dong_names)}"
        else:
            self.dong_yao_label.text = "动爻：无"
    
    def _format_yao_text(self, yao, index):
        """格式化爻文本
        
        Args:
            yao: 爻数据字典
            index: 爻索引（0-5）
            
        Returns:
            格式化后的文本
        """
        yao_names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
        yao_name = yao_names[index]
        
        # 获取爻符号
        yin_yang = yao.get('yin_yang', '阳')
        is_dong = yao.get('is_dong', False)
        
        if is_dong:
            key = '阳动' if '阳' in yin_yang else '阴动'
        else:
            key = '阳' if '阳' in yin_yang else '阴'
        
        symbol = YAO_SYMBOLS.get(key, '⚊')
        
        # 格式化：初九 ⚊ ○
        return f"{yao_name} {symbol}"
    
    def _clear_display(self):
        """清空显示"""
        self.gua_name_label.text = "本卦：未起卦 → 变卦：无"
        self.gua_symbol_label.text = "䷀ 乾 ☰ 上 ☰ 下"
        
        for label in self.yao_labels:
            label.text = ""
        
        self.dong_yao_label.text = "动爻：无"


class GuaInfoDisplay(BoxLayout):
    """卦象详细信息显示（可选，用于弹窗或详情页）"""
    
    def __init__(self, responsive=None, **kwargs):
        super().__init__(**kwargs)
        self.responsive = responsive
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        # 卦名
        self.title_label = Label(
            text="乾为天",
            font_size=self._get_font_size(24),
            size_hint_y=None,
            height=dp(50),
            bold=True
        )
        self.add_widget(self.title_label)
        
        # 卦符号
        self.symbol_label = Label(
            text="䷀",
            font_size=self._get_font_size(48),
            size_hint_y=None,
            height=dp(80),
            halign='center'
        )
        self.add_widget(self.symbol_label)
        
        # 卦象结构
        self.structure_label = Label(
            text="上乾 ☰ 下乾 ☰",
            font_size=self._get_font_size(16),
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(self.structure_label)
    
    def _get_font_size(self, base_size):
        """获取字体大小"""
        if self.responsive:
            return self.responsive.get_font_size(base_size)
        return sp(base_size)
    
    def update_display(self, gua_name, upper_name, lower_name):
        """更新显示"""
        symbol = HEXAGRAM_SYMBOLS.get(gua_name, '')
        upper_symbol = TRIGRAM_SYMBOLS.get(upper_name, '')
        lower_symbol = TRIGRAM_SYMBOLS.get(lower_name, '')
        
        self.title_label.text = gua_name
        self.symbol_label.text = symbol
        self.structure_label.text = f"上{upper_name} {upper_symbol} 下{lower_name} {lower_symbol}"


# ========== Unicode 符号测试工具 ==========

def test_unicode_display():
    """测试 Unicode 符号显示"""
    print("=" * 50)
    print("64 卦 Unicode 符号测试")
    print("=" * 50)
    
    # 测试 64 卦符号
    print("\n64 卦符号:")
    for i, (name, symbol) in enumerate(HEXAGRAM_SYMBOLS.items()):
        print(f"{symbol} {name}", end="  ")
        if (i + 1) % 4 == 0:
            print()
    
    print("\n\n八卦符号:")
    for name, symbol in TRIGRAM_SYMBOLS.items():
        print(f"{name}: {symbol}", end="  ")
    
    print("\n\n爻符号:")
    for name, symbol in YAO_SYMBOLS.items():
        print(f"{name}: {symbol}", end="  ")
    
    print("\n" + "=" * 50)
    print("如果符号显示正常，说明 Unicode 支持良好 ✅")
    print("如果显示为方框或问号，需要安装字体 ⚠️")
    print("=" * 50)


if __name__ == '__main__':
    test_unicode_display()
