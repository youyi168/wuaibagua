#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
起卦动画模块
提供投掷铜钱、显示结果等动画效果
"""

from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
import random
from logger import info, debug


class CoinAnimation(Label):
    """铜钱投掷动画"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = sp(48)
        self.text = '🪙'
        self.size_hint = (None, None)
        self.size = (dp(80), dp(80))
        self.halign = 'center'
        self.valign = 'middle'
        
        # 绑定纹理更新
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # 绘制背景
        with self.canvas.before:
            Color(1, 1, 1, 0.9)
            self.rect = Rectangle(size=self.size, pos=self.pos)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def animate_toss(self, on_complete=None):
        """投掷动画
        
        Args:
            on_complete: 动画完成回调
        """
        # 1. 向上飞起
        anim_up = Animation(y=self.y + dp(200), duration=0.3)
        
        # 2. 旋转
        anim_rotate = Animation(rotation=720, duration=0.5)
        
        # 3. 落下
        anim_down = Animation(y=self.y, duration=0.3)
        
        # 组合动画
        anim = anim_up + anim_rotate + anim_down
        
        # 完成后回调
        if on_complete:
            anim.bind(on_complete=on_complete)
        
        anim.start(self)


class YaoRevealAnimation(BoxLayout):
    """爻显示动画"""
    
    def __init__(self, yao_symbol, yao_name, is_dong=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.padding = dp(5)
        self.size_hint_y = None
        self.height = dp(40)
        self.opacity = 0
        
        # 爻符号
        self.symbol_label = Label(
            text=yao_symbol,
            font_size=sp(24),
            size_hint_x=None,
            width=dp(80),
            halign='center'
        )
        
        # 爻位名称
        self.name_label = Label(
            text=yao_name,
            font_size=sp(16),
            halign='left'
        )
        
        self.add_widget(self.symbol_label)
        self.add_widget(self.name_label)
        
        # 动爻标记
        if is_dong:
            dong_label = Label(
                text='○',
                font_size=sp(20),
                color=(1, 0, 0, 1),
                size_hint_x=None,
                width=dp(30)
            )
            self.add_widget(dong_label)
    
    def reveal(self, delay=0):
        """显示动画
        
        Args:
            delay: 延迟时间（秒）
        """
        def do_reveal(dt):
            # 淡入
            anim = Animation(opacity=1, duration=0.3)
            anim.start(self)
            
            # 轻微放大
            anim_scale = Animation(scale_x=1.05, duration=0.15)
            anim_scale += Animation(scale_x=1.0, duration=0.15)
            anim_scale.start(self)
        
        if delay > 0:
            Clock.schedule_once(do_reveal, delay)
        else:
            do_reveal(0)


class DivinationAnimation:
    """起卦动画控制器"""
    
    def __init__(self, container, on_complete=None):
        """
        Args:
            container: 容器组件（用于添加动画元素）
            on_complete: 动画完成回调，参数为 results 列表
        """
        self.container = container
        self.on_complete = on_complete
        self.results = []
        self.coin = None
    
    def start(self):
        """开始起卦动画"""
        info('开始起卦动画')
        
        # 创建铜钱
        self.coin = CoinAnimation()
        self.container.add_widget(self.coin)
        
        # 投掷 6 次
        self._toss_coin(0)
    
    def _toss_coin(self, index):
        """投掷第 index 次铜钱
        
        Args:
            index: 投掷次数（0-5）
        """
        if index >= 6:
            # 完成
            self.container.remove_widget(self.coin)
            if self.on_complete:
                self.on_complete(self.results)
            return
        
        # 投掷动画
        def on_toss_complete(anim, coin):
            # 生成结果
            coins = [random.randint(0, 1) for _ in range(3)]
            sum_coins = sum(coins)
            
            # 铜钱结果映射
            COIN_RESULTS = {
                0: ('老阴', '━ ━×', '阴动', 6),
                1: ('少阳', '━━━', '阳', 7),
                2: ('少阴', '━ ━', '阴', 8),
                3: ('老阳', '━━━○', '阳动', 9)
            }
            
            name, symbol, yin_yang, number = COIN_RESULTS[sum_coins]
            self.results.append(sum_coins)
            
            # 显示结果动画
            self._show_yao_result(index, symbol, name, yin_yang)
            
            # 下一次投掷
            Clock.schedule_once(lambda dt: self._toss_coin(index + 1), 0.5)
        
        self.coin.animate_toss(on_toss_complete)
    
    def _show_yao_result(self, index, symbol, name, yin_yang):
        """显示爻结果动画
        
        Args:
            index: 爻索引（0-5，从初爻开始）
            symbol: 爻符号
            name: 爻名称
            yin_yang: 阴阳
        """
        yao_names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
        yao_name = yao_names[index]
        
        is_dong = '动' in yin_yang
        
        # 创建爻显示
        yao_anim = YaoRevealAnimation(symbol, f"{yao_name}: {name}", is_dong)
        
        # 添加到容器（从下往上）
        self.container.add_widget(yao_anim)
        
        # 显示动画（延迟，形成从下往上的效果）
        delay = index * 0.2
        yao_anim.reveal(delay)


class GuaSymbolAnimation(Label):
    """卦象符号动画"""
    
    def __init__(self, gua_symbol, gua_name, **kwargs):
        super().__init__(**kwargs)
        self.text = gua_symbol
        self.font_size = sp(48)
        self.halign = 'center'
        self.valign = 'middle'
        self.size_hint = (None, None)
        self.size = (dp(100), dp(100))
        self.opacity = 0
        
        # 绑定更新
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # 背景
        with self.canvas.before:
            Color(0.8, 0.6, 0.4, 0.3)
            self.rect = Rectangle(size=self.size, pos=self.pos)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def animate_appear(self, delay=0):
        """出现动画
        
        Args:
            delay: 延迟时间
        """
        def do_animate(dt):
            # 淡入 + 放大
            anim = Animation(opacity=1, duration=0.5)
            anim += Animation(font_size=sp(60), duration=0.3)
            anim += Animation(font_size=sp(48), duration=0.2)
            anim.start(self)
        
        if delay > 0:
            Clock.schedule_once(do_animate, delay)
        else:
            do_animate(0)


def animate_divination(container, on_complete):
    """便捷函数：开始起卦动画
    
    Args:
        container: 容器组件
        on_complete: 完成回调(results)
    
    Returns:
        DivinationAnimation 实例
    """
    anim = DivinationAnimation(container, on_complete)
    anim.start()
    return anim


def animate_gua_symbol(container, gua_symbol, gua_name, delay=0):
    """便捷函数：卦象符号出现动画
    
    Args:
        container: 容器
        gua_symbol: 卦象符号（如 ䷀）
        gua_name: 卦名
        delay: 延迟
    
    Returns:
        GuaSymbolAnimation 实例
    """
    symbol_anim = GuaSymbolAnimation(gua_symbol, gua_name)
    container.add_widget(symbol_anim)
    symbol_anim.animate_appear(delay)
    return symbol_anim
