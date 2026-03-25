#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 金钱卦算卦软件 (Android 版)
功能：电脑起卦、手动起卦、今日运势、本地卦象解释、分享功能
"""

import os
import sys
import random
import hashlib
from datetime import datetime

# 导入完整卦象计算模块（符合《图解周易》）
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
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.clock import Clock

# ==================== 注册中文字体 ====================
def register_chinese_font():
    """注册中文字体到 Kivy"""
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    font_path = os.path.join(font_dir, 'NotoSansSC-Regular.ttf')
    
    if os.path.exists(font_path):
        LabelBase.register(name='NotoSansSC', fn_regular=font_path)
        print(f'[INFO] 中文字体已注册：{font_path}')
    else:
        print(f'[WARN] 中文字体文件不存在，使用系统字体')

# 在应用启动前注册字体
register_chinese_font()

# Android 剪贴板
try:
    from jnius import autoclass
    ANDROID_CLIPBOARD_AVAILABLE = True
except ImportError:
    ANDROID_CLIPBOARD_AVAILABLE = False
    print('[WARN] jnius not available')


# ==================== 工具函数 ====================

def copy_to_clipboard(text):
    """复制文本到剪贴板"""
    try:
        if ANDROID_CLIPBOARD_AVAILABLE:
            Context = autoclass('android.content.Context')
            ClipboardManager = autoclass('android.content.ClipboardManager')
            ClipData = autoclass('android.content.ClipData')
            
            app = App.get_running_app()
            if app:
                context = app.getApplicationContext()
                clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE)
                clip = ClipData.newPlainText('wuaibagua', text)
                clipboard.setPrimaryClip(clip)
        else:
            print(f'[INFO] Copy: {text[:50]}...')
    except Exception as e:
        print(f'[ERROR] Copy failed: {e}')


def show_toast(message):
    """显示 Toast 提示"""
    try:
        if ANDROID_CLIPBOARD_AVAILABLE:
            Context = autoclass('android.content.Context')
            Toast = autoclass('android.widget.Toast')
            
            app = App.get_running_app()
            if app:
                context = app.getApplicationContext()
                toast = Toast.makeText(context, message, Toast.LENGTH_SHORT)
                toast.show()
        else:
            print(f'[TOAST] {message}')
    except Exception as e:
        print(f'[ERROR] Toast failed: {e}')


def get_device_id():
    """获取设备识别码（Android）"""
    try:
        if ANDROID_CLIPBOARD_AVAILABLE:
            Settings = autoclass('android.provider.Settings$Secure')
            app = App.get_running_app()
            if app:
                context = app.getApplicationContext()
                resolver = context.getContentResolver()
                android_id = Settings.Secure.getString(resolver, 'android_id')
                return android_id if android_id else 'default'
        return 'default'
    except Exception as e:
        print(f'[ERROR] get_device_id: {e}')
        return 'default'


def get_daily_gua():
    """
    今日运势算法
    根据日期 + 设备 ID 生成 deterministic 卦象
    """
    try:
        # 获取今日日期
        today = datetime.now().strftime('%Y%m%d')
        device_id = get_device_id()
        
        # 组合种子
        seed_str = f"{today}_{device_id}"
        seed_hash = hashlib.sha256(seed_str.encode()).hexdigest()
        
        # 用 hash 生成 6 爻（从下往上）
        yao_list = []
        for i in range(6):
            # 取 hash 的一部分转换为数字
            byte_val = int(seed_hash[i*4:(i+1)*4], 16)
            # 映射到 6/7/8/9（考虑老阴老阳）
            mod = byte_val % 100
            if mod < 10:
                yao = 6  # 老阴
            elif mod < 45:
                yao = 7  # 少阳
            elif mod < 55:
                yao = 8  # 少阴
            else:
                yao = 9  # 老阳
            yao_list.append(yao)
        
        return yao_list
    except Exception as e:
        print(f'[ERROR] get_daily_gua: {e}')
        # Fallback 到随机
        return [random.randint(6, 9) for _ in range(6)]


# ==================== 手动起卦弹窗 ====================

# 保存上次手动起卦的选择
manual_gua_last_selection = [7, 7, 7, 7, 7, 7]  # 默认全为少阳


def show_manual_gua_popup(app):
    """手动起卦弹窗（保存上次选择）"""
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # 标题
        title_label = Label(
            text='手动起卦\n请选择每一爻',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18)
        )
        layout.add_widget(title_label)
        
        # 存储选择器
        spinners = []
        yao_options = ['少阳 ---', '少阴 - -', '老阳 --- O', '老阴 - - X']
        yao_values = [7, 8, 9, 6]
        yao_names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
        
        # 创建 6 个选择器（使用上次保存的值）
        for i in range(6):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
            
            # 爻名
            name_label = Label(
                text=yao_names[i],
                size_hint_x=0.3,
                font_size=dp(15)
            )
            row.add_widget(name_label)
            
            # 选择器（使用上次的值）
            last_value = manual_gua_last_selection[i]
            default_index = yao_values.index(last_value) if last_value in yao_values else 0
            
            spinner = Spinner(
                text=yao_options[default_index],
                values=yao_options,
                size_hint_x=0.7
            )
            spinners.append(spinner)
            row.add_widget(spinner)
            
            layout.add_widget(row)
        
        # 按钮
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # 确定
        def on_confirm(instance):
            try:
                yao_list = []
                for spinner in spinners:
                    idx = spinner.values.index(spinner.text)
                    yao_list.append(yao_values[idx])
                
                # 保存选择
                global manual_gua_last_selection
                manual_gua_last_selection = yao_list[:]
                
                popup.dismiss()
                app.display_gua(yao_list, '手动起卦')
            except Exception as e:
                print(f'[ERROR] Confirm failed: {e}')
                show_toast('❌ 选择失败')
        
        confirm_btn = Button(text='确定', font_size=dp(16))
        confirm_btn.bind(on_press=on_confirm)
        btn_layout.add_widget(confirm_btn)
        
        # 取消
        cancel_btn = Button(text='取消', font_size=dp(16))
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        # 弹窗
        popup = Popup(
            title='手动起卦',
            content=layout,
            size_hint=(0.9, 0.75),
            auto_dismiss=False
        )
        
        popup.open()
    except Exception as e:
        print(f'[ERROR] show_manual_gua_popup failed: {e}')
        show_toast('❌ 弹窗失败')


# ==================== 分享弹窗 ====================

def show_share_popup(text):
    """分享弹窗"""
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        title = Label(
            text='选择分享方式',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18)
        )
        layout.add_widget(title)
        
        # 分享选项
        options = [
            ('复制文本', lambda: copy_and_close(text, popup)),
            ('分享到微信', lambda: share_wechat(text, popup)),
            ('分享到 QQ', lambda: share_qq(text, popup)),
        ]
        
        for name, callback in options:
            btn = Button(text=name, size_hint_y=None, height=dp(45), font_size=dp(16))
            btn.bind(on_press=lambda x, cb=callback: cb())
            layout.add_widget(btn)
        
        # 取消
        cancel_btn = Button(text='取消', size_hint_y=None, height=dp(45), font_size=dp(16))
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(cancel_btn)
        
        popup = Popup(
            title='分享',
            content=layout,
            size_hint=(0.85, 0.7),
            auto_dismiss=False
        )
        
        popup.open()
    except Exception as e:
        print(f'[ERROR] show_share_popup failed: {e}')


def copy_and_close(text, popup):
    """复制并关闭"""
    copy_to_clipboard(text)
    popup.dismiss()
    show_toast('✅ 已复制')


def share_wechat(text, popup):
    """分享到微信（简化版）"""
    # 先复制文本
    copy_to_clipboard(text)
    popup.dismiss()
    show_toast('✅ 已复制，请打开微信粘贴')


def share_qq(text, popup):
    """分享到 QQ（简化版）"""
    copy_to_clipboard(text)
    popup.dismiss()
    show_toast('✅ 已复制，请打开 QQ 粘贴')


# ==================== 设置弹窗 ====================

def show_settings_popup():
    """设置弹窗"""
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        title = Label(
            text='设置',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18)
        )
        layout.add_widget(title)
        
        # 版本信息
        version = Label(
            text='版本：v1.1.1\n作者：浩哥\n\n更多功能开发中...',
            size_hint_y=None,
            height=dp(100),
            font_size=dp(14)
        )
        layout.add_widget(version)
        
        # 关闭
        close_btn = Button(text='关闭', size_hint_y=None, height=dp(45), font_size=dp(16))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup = Popup(
            title='设置',
            content=layout,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        popup.open()
    except Exception as e:
        print(f'[ERROR] show_settings_popup failed: {e}')


# ==================== 卦象解释弹窗 ====================

def show_gua_explanation(gua_name, txt_content):
    """显示卦象解释"""
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        
        # 标题
        title = Label(
            text=gua_name,
            size_hint_y=None,
            height=dp(45),
            font_size=dp(18),
            bold=True
        )
        layout.add_widget(title)
        
        # 滚动区域
        scroll = ScrollView()
        
        # 完整 txt 内容
        content = Label(
            text=txt_content,
            markup=False,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=dp(13),
            padding=(8, 8)
        )
        content.bind(size=content.setter('text_size'))
        scroll.add_widget(content)
        
        layout.add_widget(scroll)
        
        # 关闭
        close_btn = Button(text='关闭', size_hint_y=None, height=dp(45), font_size=dp(15))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup = Popup(
            title='卦象详解',
            content=layout,
            size_hint=(0.92, 0.85),
            auto_dismiss=False
        )
        
        popup.open()
    except Exception as e:
        print(f'[ERROR] show_gua_explanation failed: {e}')
        show_toast('❌ 显示失败')


# ==================== 主应用 ====================

class WuaibaguaApp(App):
    """我爱八卦应用主类"""
    
    def build(self):
        """构建应用界面"""
        self.title = '我爱八卦'
        
        # 设置全局字体
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        Label.font_name = 'NotoSansSC'
        Button.font_name = 'NotoSansSC'
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # 标题（移除版本号）
        title = Label(
            text='我爱八卦',
            markup=True,
            size_hint_y=None,
            height=dp(60),
            font_size=dp(28),
            bold=True
        )
        main_layout.add_widget(title)
        
        # 卦象显示区域（移到上方）
        self.gua_result_label = Label(
            text='点击按钮开始起卦',
            markup=True,
            size_hint_y=1,
            font_size=dp(16),
            halign='center',
            valign='top'
        )
        self.gua_result_label.bind(size=self.gua_result_label.setter('text_size'))
        main_layout.add_widget(self.gua_result_label)
        
        # 起卦按钮（移到下方）
        method_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.btn_auto = Button(text='电脑起卦', font_size=dp(16))
        self.btn_auto.bind(on_press=self.auto_gua)
        method_layout.add_widget(self.btn_auto)
        
        self.btn_manual = Button(text='手动起卦', font_size=dp(16))
        self.btn_manual.bind(on_press=self.manual_gua)
        method_layout.add_widget(self.btn_manual)
        
        self.btn_daily = Button(text='今日运势', font_size=dp(16))
        self.btn_daily.bind(on_press=self.daily_gua)
        method_layout.add_widget(self.btn_daily)
        
        main_layout.add_widget(method_layout)
        
        # 功能按钮（最底部）
        func_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        
        self.btn_explain = Button(text='解释', font_size=dp(15))
        self.btn_explain.bind(on_press=self.show_explanation)
        func_layout.add_widget(self.btn_explain)
        
        self.btn_share = Button(text='分享', font_size=dp(15))
        self.btn_share.bind(on_press=self.share_gua)
        func_layout.add_widget(self.btn_share)
        
        self.btn_settings = Button(text='设置', font_size=dp(15))
        self.btn_settings.bind(on_press=lambda x: show_settings_popup())
        func_layout.add_widget(self.btn_settings)
        
        main_layout.add_widget(func_layout)
        
        # 状态
        self.current_gua = None
        self.current_yao_list = None
        self.current_gua_txt = None
        
        return main_layout
    
    def auto_gua(self, instance):
        """电脑起卦"""
        yao_list = [random.randint(6, 9) for _ in range(6)]
        self.display_gua(yao_list, '电脑起卦')
    
    def manual_gua(self, instance):
        """手动起卦"""
        show_manual_gua_popup(self)
    
    def daily_gua(self, instance):
        """今日运势（根据日期 + 设备 ID）"""
        yao_list = get_daily_gua()
        self.display_gua(yao_list, '今日运势')
    
    def display_gua(self, yao_list, method):
        """显示卦象"""
        try:
            if GUA_CALC_AVAILABLE:
                text, gua_name = gua_calculator.format_gua_display(yao_list, method)
            else:
                text = f'{method}\n\n卦名：未知卦'
                gua_name = '未知卦'
            
            self.gua_result_label.text = text
            self.current_gua = gua_name
            self.current_yao_list = yao_list
            
            # 读取 txt
            self.current_gua_txt = None
            if GUA_CALC_AVAILABLE:
                self.current_gua_txt = gua_calculator.get_gua_txt(gua_name)
            
            show_toast(f'✅ {gua_name}')
        except Exception as e:
            print(f'[ERROR] display_gua failed: {e}')
            show_toast('❌ 显示失败')
    
    def show_explanation(self, instance):
        """显示解释"""
        if not self.current_gua:
            show_toast('❌ 请先起卦')
            return
        
        if self.current_gua_txt:
            show_gua_explanation(self.current_gua, self.current_gua_txt)
        else:
            show_toast('❌ 无解释数据')
    
    def share_gua(self, instance):
        """分享卦象"""
        if not self.current_gua:
            show_toast('❌ 请先起卦')
            return
        
        # 构建分享文本
        share_text = f'【{self.current_gua}】\n\n'
        share_text += self.gua_result_label.text.replace('[b]', '').replace('[/b]', '').replace('[/font]', '')
        
        show_share_popup(share_text)
    
    def copy_result(self, instance):
        """复制卦象"""
        if not self.current_gua:
            show_toast('❌ 请先起卦')
            return
        
        text = f'【{self.current_gua}】\n{self.gua_result_label.text}'
        copy_to_clipboard(text)
        show_toast('✅ 已复制')


if __name__ == '__main__':
    WuaibaguaApp().run()
