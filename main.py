#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我爱八卦 - 金钱卦算卦软件 (Android 版)
功能：电脑起卦、手动起卦、今日运势、本地卦象解释、分享功能

【重要】OPPO 设备 Vulkan 禁用
必须在 import kivy 之前设置环境变量！
"""

# ==================== OPPO 设备 Vulkan 禁用（关键！） ====================
# 必须在 import kivy 之前设置
import os
os.environ['KIVY_GL_BACKEND'] = 'gl'      # 强制使用 OpenGL
os.environ['KIVY_NO_VULKAN'] = '1'         # 禁用 Vulkan
os.environ['KIVY_VIDEO_OPTS'] = 'gl'       # 视频也使用 OpenGL

# ==================== 标准导入 ====================
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

# 现在才能导入 Kivy
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
from kivy.graphics import Instruction

# ==================== OPPO 设备 Vulkan 检测与禁用 ====================
def disable_vulkan_if_needed():
    """
    检测 OPPO 设备并禁用 Vulkan 渲染
    解决 Adreno Vulkan 驱动 Bug 导致的闪退
    """
    try:
        if ANDROID_CLIPBOARD_AVAILABLE:
            Build = autoclass('android.os.Build')
            manufacturer = Build.MANUFACTURER.lower()
            model = Build.MODEL.lower()
            android_version = Build.VERSION.RELEASE
            
            # OPPO/一加/真我设备检测
            oppo_brands = ['oppo', 'oneplus', 'realme', '一加', '欧珀']
            is_oppo = any(brand in manufacturer or brand in model for brand in oppo_brands)
            
            if is_oppo and int(android_version.split('.')[0]) >= 13:
                print(f'[WARN] 检测到 OPPO 设备 Android {android_version}，禁用 Vulkan')
                print(f'[WARN] 设备：{manufacturer} {model}')
                
                # 强制使用 OpenGL ES 2.0
                from kivy.config import Config
                Config.set('graphics', 'backend', 'gl')
                Config.set('graphics', 'gl_backend', 'gl')
                Config.write()
                
                # 禁用硬件加速的某些特性
                Window.clearcolor = (0, 0, 0, 1)
                
                return True
    except Exception as e:
        print(f'[ERROR] disable_vulkan_if_needed: {e}')
    
    return False

# 在应用启动前检测
disable_vulkan_if_needed()

# ==================== 注册字体 ====================
def register_fonts():
    """注册中文字体和易卦专用字体"""
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    
    # 注册中文字体
    font_path = os.path.join(font_dir, 'NotoSansSC-Regular.ttf')
    if os.path.exists(font_path) and os.path.getsize(font_path) > 0:
        LabelBase.register(name='NotoSansSC', fn_regular=font_path)
        print(f'[INFO] 中文字体已注册')
    else:
        print(f'[WARN] 中文字体文件不存在或损坏')
    
    # 注册易卦专用字体（使用已有且有效的字体）
    yijing_fonts = [
        'NotoSansSymbols-Regular.ttf',  # 258KB，已有 ✅
        'seguisym.ttf',                  # 2.5MB，已有 ✅
    ]
    
    for font_name in yijing_fonts:
        font_path = os.path.join(font_dir, font_name)
        if os.path.exists(font_path) and os.path.getsize(font_path) > 0:
            LabelBase.register(name='Yijing', fn_regular=font_path)
            print(f'[INFO] 易卦字体已注册：{font_name}')
            return
    
    # fallback 到中文字体
    print(f'[WARN] 易卦专用字体未找到，使用中文字体')

# 在应用启动前注册字体
register_fonts()

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
            if app and hasattr(app, 'getApplicationContext'):
                context = app.getApplicationContext()
                toast = Toast.makeText(context, message, Toast.LENGTH_SHORT)
                toast.show()
            else:
                # Fallback: 使用 mActivity
                if app and hasattr(app, 'mActivity'):
                    context = app.mActivity.getApplicationContext()
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
        
        # 弹窗（调整位置，避免太靠下）
        popup = Popup(
            title='手动起卦',
            content=layout,
            size_hint=(0.9, 0.7),
            auto_dismiss=False
        )
        
        # 居中显示
        from kivy.core.window import Window
        popup.pos = (Window.width - popup.width) / 2, (Window.height - popup.height) / 2
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

def show_liuyao_popup(panduan_text):
    """六爻排盘弹窗（使用 ASCII，避免字体问题）"""
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # 标题
        title = Label(
            text='六爻排盘',
            size_hint_y=None,
            height=dp(45),
            font_size=dp(18),
            bold=True
        )
        layout.add_widget(title)
        
        # 滚动区域
        scroll = ScrollView()
        
        # 排盘内容（使用 ASCII，确保显示）
        content = Label(
            text=panduan_text,
            markup=False,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=dp(14),
            padding=(10, 10)
        )
        content.bind(size=content.setter('text_size'))
        scroll.add_widget(content)
        
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(text='关闭', size_hint_y=None, height=dp(45), font_size=dp(15))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup = Popup(
            title='六爻排盘',
            content=layout,
            size_hint=(0.95, 0.85),
            auto_dismiss=False
        )
        
        popup.open()
    except Exception as e:
        print(f'[ERROR] show_liuyao_popup failed: {e}')
        import traceback
        traceback.print_exc()
        show_toast('❌ 排盘失败')


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

def show_gua_explanation_with_duangua(gua_name, detail_data, yao_list, changing_gua_name=None, duangua_result=None):
    """
    显示卦象解释和断卦结果（完整版）
    
    包含：
    - 卦名、卦辞、大象
    - 爻辞（带变爻标记）
    - 断卦方法
    - 变卦信息
    """
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # 标题
        title = Label(
            text=f'【{gua_name}】详解',
            size_hint_y=None,
            height=dp(45),
            font_size=dp(18),
            bold=True
        )
        layout.add_widget(title)
        
        # 滚动区域
        scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # 卦辞
        if detail_data and detail_data.get('gua_ci'):
            section = Label(
                text='【卦辞】',
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            content_layout.add_widget(section)
            
            text = Label(
                text=detail_data['gua_ci'],
                size_hint_y=None,
                halign='left',
                valign='top',
                font_size=dp(15),
                padding=(10, 5)
            )
            text.bind(size=text.setter('text_size'))
            content_layout.add_widget(text)
        
        # 大象
        if detail_data and detail_data.get('da_xiang'):
            section = Label(
                text='【大象】',
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            content_layout.add_widget(section)
            
            text = Label(
                text=detail_data['da_xiang'],
                size_hint_y=None,
                halign='left',
                valign='top',
                font_size=dp(15),
                padding=(10, 5)
            )
            text.bind(size=text.setter('text_size'))
            content_layout.add_widget(text)
        
        # 断卦方法
        if duangua_result:
            section = Label(
                text='【断卦方法】',
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            content_layout.add_widget(section)
            
            text = Label(
                text=duangua_result['duan_gua_method'],
                size_hint_y=None,
                halign='left',
                valign='top',
                font_size=dp(15),
                padding=(10, 5)
            )
            text.bind(size=text.setter('text_size'))
            content_layout.add_widget(text)
            
            # 动爻数
            text = Label(
                text=f'动爻数：{duangua_result["dong_yao_count"]}',
                size_hint_y=None,
                halign='left',
                font_size=dp(14),
                padding=(10, 3)
            )
            content_layout.add_widget(text)
            
            # 变卦
            if duangua_result['zhi_gua']:
                text = Label(
                    text=f'变卦：{duangua_result["zhi_gua"]}',
                    size_hint_y=None,
                    halign='left',
                    font_size=dp(14),
                    padding=(10, 3)
                )
                content_layout.add_widget(text)
        
        # 爻辞
        if detail_data and detail_data.get('yao_ci'):
            section = Label(
                text='【爻辞】',
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            content_layout.add_widget(section)
            
            for yao in detail_data['yao_ci']:
                yao_name = yao.get('name', '')
                yao_text = yao.get('text', '')
                xiang = yao.get('xiang', '')
                
                # 标记变爻
                yao_type = 9 if '九' in yao_name else 6
                is_changing = yao_type in [6, 9]
                mark = ' ⭕' if yao_type == 9 else ' ✕' if yao_type == 6 else ''
                
                yao_label = Label(
                    text=f'{yao_name}{mark}: {yao_text}',
                    size_hint_y=None,
                    halign='left',
                    valign='top',
                    font_size=dp(14),
                    padding=(10, 3)
                )
                yao_label.bind(size=yao_label.setter('text_size'))
                content_layout.add_widget(yao_label)
                
                if xiang:
                    xiang_label = Label(
                        text=f'  象曰：{xiang}',
                        size_hint_y=None,
                        halign='left',
                        font_size=dp(13),
                        text_color=(0.6, 0.6, 0.6, 1),
                        padding=(10, 0)
                    )
                    xiang_label.bind(size=xiang_label.setter('text_size'))
                    content_layout.add_widget(xiang_label)
        
        scroll.add_widget(content_layout)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(text='关闭', size_hint_y=None, height=dp(50), font_size=dp(16))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup = Popup(
            title='卦象详解',
            content=layout,
            size_hint=(0.95, 0.9),
            auto_dismiss=False
        )
        
        popup.open()
    except Exception as e:
        print(f'[ERROR] show_gua_explanation_with_duangua failed: {e}')
        show_toast('❌ 显示失败')


def show_gua_explanation_detail(gua_name, detail_data, yao_list, changing_gua_name=None):
    """
    显示详细卦象解释（含变卦）
    包含：卦辞、大象、爻辞、白话、变卦
    """
    try:
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # 标题
        title = Label(
            text=f'【{gua_name}】',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(20),
            bold=True
        )
        layout.add_widget(title)
        
        # 滚动区域
        scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # 卦辞
        if detail_data.get('gua_ci'):
            section_title = Label(
                text='【卦辞】',
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            content_layout.add_widget(section_title)
            
            gua_ci_label = Label(
                text=detail_data['gua_ci'],
                size_hint_y=None,
                halign='left',
                valign='top',
                font_size=dp(15),
                padding=(10, 5)
            )
            gua_ci_label.bind(size=gua_ci_label.setter('text_size'))
            content_layout.add_widget(gua_ci_label)
        
        # 大象
        if detail_data.get('da_xiang'):
            section_title = Label(
                text='【大象】',
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            content_layout.add_widget(section_title)
            
            da_xiang_label = Label(
                text=detail_data['da_xiang'],
                size_hint_y=None,
                halign='left',
                valign='top',
                font_size=dp(15),
                padding=(10, 5)
            )
            da_xiang_label.bind(size=da_xiang_label.setter('text_size'))
            content_layout.add_widget(da_xiang_label)
        
        # 爻辞
        yao_ci_list = detail_data.get('yao_ci', [])
        if yao_ci_list:
            section_title = Label(
                text='【爻辞】',
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            content_layout.add_widget(section_title)
            
            for i, yao_data in enumerate(yao_ci_list):
                yao_name = yao_data.get('name', '')
                yao_text = yao_data.get('text', '')
                yao_xiang = yao_data.get('xiang', '')
                
                # 标记当前爻（变爻）
                current_yao = yao_list[i] if i < len(yao_list) else 7
                is_changing = current_yao in [6, 9]
                mark = '★ ' if is_changing else '  '
                
                yao_label = Label(
                    text=f'{mark}{yao_name}: {yao_text}',
                    size_hint_y=None,
                    halign='left',
                    valign='top',
                    font_size=dp(14),
                    padding=(10, 3)
                )
                yao_label.bind(size=yao_label.setter('text_size'))
                content_layout.add_widget(yao_label)
                
                # 象曰
                if yao_xiang:
                    xiang_label = Label(
                        text=f'  象曰：{yao_xiang}',
                        size_hint_y=None,
                        halign='left',
                        valign='top',
                        font_size=dp(13),
                        text_color=(0.6, 0.6, 0.6, 1),
                        padding=(10, 0)
                    )
                    xiang_label.bind(size=xiang_label.setter('text_size'))
                    content_layout.add_widget(xiang_label)
        
        # 变卦
        if changing_gua_name:
            section_title = Label(
                text='【变卦】',
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            content_layout.add_widget(section_title)
            
            changing_label = Label(
                text=f'变卦：{changing_gua_name}',
                size_hint_y=None,
                halign='left',
                valign='top',
                font_size=dp(15),
                padding=(10, 5)
            )
            changing_label.bind(size=changing_label.setter('text_size'))
            content_layout.add_widget(changing_label)
        
        # 白话解释
        if detail_data.get('bai_hua'):
            section_title = Label(
                text='【白话解释】',
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            content_layout.add_widget(section_title)
            
            bai_hua_label = Label(
                text=detail_data['bai_hua'],
                size_hint_y=None,
                halign='left',
                valign='top',
                font_size=dp(14),
                padding=(10, 5)
            )
            bai_hua_label.bind(size=bai_hua_label.setter('text_size'))
            content_layout.add_widget(bai_hua_label)
        
        scroll.add_widget(content_layout)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(text='关闭', size_hint_y=None, height=dp(50), font_size=dp(16))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup = Popup(
            title='卦象详解',
            content=layout,
            size_hint=(0.95, 0.9),
            auto_dismiss=False
        )
        
        popup.open()
    except Exception as e:
        print(f'[ERROR] show_gua_explanation_detail failed: {e}')
        show_toast('❌ 显示失败')


# ==================== 主应用 ====================

class WuaibaguaApp(App):
    """我爱八卦应用主类"""
    
    def build(self):
        """构建应用界面"""
        self.title = '我爱八卦'
        
        # 设置窗口背景色（半透明，不遮挡背景）
        from kivy.core.window import Window
        Window.clearcolor = (0.95, 0.95, 0.95, 1)  # 浅灰色背景
        
        # 设置全局字体
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        Label.font_name = 'NotoSansSC'
        Button.font_name = 'NotoSansSC'
        
        # 主布局（使用 ScrollView 防止遮挡）
        from kivy.uix.scrollview import ScrollView
        main_scroll = ScrollView()
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # 标题
        title = Label(
            text='[b]我爱八卦[/b]',
            markup=True,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24),
            bold=True,
            halign='center'
        )
        main_layout.add_widget(title)
        
        # 卦象显示区域（图片和爻位信息一一对应）
        from kivy.uix.image import Image
        
        gua_display_layout = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=dp(15))
        
        # 左侧：64 卦图片（固定尺寸）
        self.hexagram_image = Image(
            source='',
            size_hint=(None, None),
            size=(120, 260),
            allow_stretch=False,
            keep_ratio=True
        )
        gua_display_layout.add_widget(self.hexagram_image)
        
        # 右侧：卦名和爻位信息（垂直排列）
        yao_info_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        
        # 卦名
        self.gua_name_label = Label(
            text='点击按钮开始起卦',
            markup=True,
            size_hint_y=None,
            height=dp(35),
            font_size=dp(18),
            bold=True,
            halign='center'
        )
        yao_info_layout.add_widget(self.gua_name_label)
        
        # 6 个爻位信息（从上爻到初爻）
        self.yao_labels = []
        yao_names = ['上爻', '五爻', '四爻', '三爻', '二爻', '初爻']
        for i in range(6):
            yao_label = Label(
                text=f'{yao_names[i]}: ',
                markup=True,
                size_hint_y=None,
                height=dp(35),
                font_size=dp(14),
                halign='left',
                valign='middle'
            )
            yao_info_layout.add_widget(yao_label)
            self.yao_labels.append(yao_label)
        
        gua_display_layout.add_widget(yao_info_layout)
        main_layout.add_widget(gua_display_layout)
        
        # 保留引用
        self.gua_result_label = self.gua_name_label
        
        # 起卦按钮（两行布局，防止混乱）
        method_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        
        # 第一行：电脑起卦、手动起卦
        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        self.btn_auto = Button(text='电脑起卦', font_size=dp(14))
        self.btn_auto.bind(on_press=self.auto_gua)
        row1.add_widget(self.btn_auto)
        self.btn_manual = Button(text='手动起卦', font_size=dp(14))
        self.btn_manual.bind(on_press=self.manual_gua)
        row1.add_widget(self.btn_manual)
        method_layout.add_widget(row1)
        
        # 第二行：金钱起卦、时间起卦
        row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        self.btn_jinqian = Button(text='金钱起卦', font_size=dp(14))
        self.btn_jinqian.bind(on_press=self.jinqian_gua)
        row2.add_widget(self.btn_jinqian)
        self.btn_time = Button(text='时间起卦', font_size=dp(14))
        self.btn_time.bind(on_press=self.time_gua)
        row2.add_widget(self.btn_time)
        method_layout.add_widget(row2)
        
        # 第三行：蓍草起卦、今日运势
        row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        self.btn_shicao = Button(text='蓍草起卦', font_size=dp(14))
        self.btn_shicao.bind(on_press=self.shicao_gua)
        row3.add_widget(self.btn_shicao)
        self.btn_daily = Button(text='今日运势', font_size=dp(14))
        self.btn_daily.bind(on_press=self.daily_gua)
        row3.add_widget(self.btn_daily)
        method_layout.add_widget(row3)
        
        main_layout.add_widget(method_layout)
        
        # 功能按钮（解释、分享、六爻、设置）
        func_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        self.btn_explain = Button(text='解释', font_size=dp(14))
        self.btn_explain.bind(on_press=self.show_explanation)
        func_layout.add_widget(self.btn_explain)
        self.btn_share = Button(text='分享', font_size=dp(14))
        self.btn_share.bind(on_press=self.share_gua)
        func_layout.add_widget(self.btn_share)
        self.btn_liuyao = Button(text='六爻', font_size=dp(14))
        self.btn_liuyao.bind(on_press=self.show_liuyao)
        func_layout.add_widget(self.btn_liuyao)
        self.btn_settings = Button(text='设置', font_size=dp(14))
        self.btn_settings.bind(on_press=lambda x: show_settings_popup())
        func_layout.add_widget(self.btn_settings)
        
        main_layout.add_widget(func_layout)
        
        # 添加到 ScrollView
        main_layout.bind(minimum_height=main_layout.setter('height'))
        main_scroll.add_widget(main_layout)
        
        return main_scroll
        
        # 功能按钮（最底部）
        func_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        
        self.btn_explain = Button(text='解释', font_size=dp(14))
        self.btn_explain.bind(on_press=self.show_explanation)
        func_layout.add_widget(self.btn_explain)
        
        self.btn_liuyao = Button(text='六爻', font_size=dp(14))
        self.btn_liuyao.bind(on_press=self.show_liuyao)
        func_layout.add_widget(self.btn_liuyao)
        
        self.btn_share = Button(text='分享', font_size=dp(14))
        self.btn_share.bind(on_press=self.share_gua)
        func_layout.add_widget(self.btn_share)
        
        self.btn_settings = Button(text='设置', font_size=dp(14))
        self.btn_settings.bind(on_press=lambda x: show_settings_popup())
        func_layout.add_widget(self.btn_settings)
        
        main_layout.add_widget(func_layout)
        
        # 状态
        self.current_gua = None
        self.current_yao_list = None
        self.current_gua_detail = None
        self.current_changing_gua = None
        
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
    
    def jinqian_gua(self, instance):
        """金钱起卦（三枚铜钱摇六次）"""
        yao_list = gua_calculator.jinqian_qigua()
        self.display_gua(yao_list, '金钱起卦')
    
    def time_gua(self, instance):
        """时间起卦（梅花易数）"""
        now = datetime.now()
        yao_list = gua_calculator.time_qigua(now.year, now.month, now.day, now.hour, now.minute)
        self.display_gua(yao_list, '时间起卦')
    
    def shicao_gua(self, instance):
        """蓍草起卦（周易传统）"""
        yao_list = gua_calculator.shicao_qigua()
        self.display_gua(yao_list, '蓍草起卦')
    
    def display_gua(self, yao_list, method):
        """显示卦象（修复版）"""
        try:
            if GUA_CALC_AVAILABLE:
                # 使用图片显示函数
                text, gua_name, changing_gua_name, image_info = gua_calculator.format_gua_display(yao_list, method)
                
                # 保存变卦信息
                self.current_changing_gua = changing_gua_name
                # 保存图片路径信息
                self.current_image_info = image_info
            else:
                text = f'{method}\n\n卦名：未知卦'
                gua_name = '未知卦'
                self.current_changing_gua = None
            
            # 显示卦象图片
            if hasattr(self, 'hexagram_image') and image_info:
                # 设置 64 卦图片
                hex_image_path = image_info.get('hexagram', '')
                if hex_image_path and os.path.exists(hex_image_path):
                    self.hexagram_image.source = hex_image_path
                    self.hexagram_image.reload()
                
                # 设置卦名
                if hasattr(self, 'gua_name_label'):
                    self.gua_name_label.text = f'[b]{gua_name}[/b]'
                
                # 设置 6 个爻位信息（从上爻到初爻，与图片一一对应）
                if hasattr(self, 'yao_labels'):
                    yao_names = ['上', '五', '四', '三', '二', '初']
                    for i in range(6):
                        yao = yao_list[5 - i]  # 从下往上数
                        yao_type = '阳' if yao in [7, 9] else '阴'
                        mark = ' ⭕' if yao == 9 else ' ✕' if yao == 6 else ''
                        self.yao_labels[i].text = f'{yao_names[i]}{yao_type}{mark}'
                
                # 保留旧代码兼容性
                if hasattr(self, 'gua_info_label'):
                    yao_lines = []
                    yao_names = ['初', '二', '三', '四', '五', '上']
                    for i in range(5, -1, -1):
                        yao = yao_list[i]
                        yao_name = yao_names[i]
                        yao_type = '阳' if yao in [7, 9] else '阴'
                        mark = ' ⭕' if yao == 9 else ' ✕' if yao == 6 else ''
                        yao_lines.append(f'{yao_name}{yao_type}{mark}')
                    self.gua_info_label.text = f'[b]{gua_name}[/b]\n\n' + '\n'.join(yao_lines)
            else:
                # Fallback: 使用文本显示
                self.gua_result_label.text = text
            
            self.current_gua = gua_name
            self.current_yao_list = yao_list
            
            # 读取详细数据
            self.current_gua_detail = None
            self.current_duangua_result = None
            if GUA_CALC_AVAILABLE:
                print(f'[DEBUG] 读取卦象数据：{gua_name}')
                self.current_gua_detail = gua_calculator.get_gua_detail(gua_name)
                # 断卦逻辑
                self.current_duangua_result = gua_calculator.duangua_logic(yao_list)
                if self.current_gua_detail:
                    print(f'[DEBUG] ✅ 读取成功：卦辞={self.current_gua_detail.get("gua_ci", "")[:20]}...')
                    print(f'[DEBUG] 断卦：{self.current_duangua_result["duan_gua_method"]}')
                else:
                    print(f'[DEBUG] ❌ 读取失败：{gua_name}')
            
            show_toast(f'✅ {gua_name}')
        except Exception as e:
            print(f'[ERROR] display_gua failed: {e}')
            show_toast('❌ 显示失败')
    
    def show_explanation(self, instance):
        """显示解释（详细版，含断卦结果）"""
        try:
            if not self.current_gua:
                show_toast('❌ 请先起卦')
                return
            
            # 显示详细解释和断卦结果
            show_gua_explanation_with_duangua(
                self.current_gua,
                self.current_gua_detail,
                self.current_yao_list,
                self.current_changing_gua,
                self.current_duangua_result
            )
        except Exception as e:
            print(f'[ERROR] show_explanation failed: {e}')
            show_toast('❌ 打开失败')
    
    def show_liuyao(self, instance):
        """显示六爻排盘（完整版：六亲 + 六神 + 世应）"""
        try:
            if not self.current_gua:
                show_toast('❌ 请先起卦')
                return
            
            # 使用完整版六爻排盘
            from liuyao_paipan import format_liuyao_full
            pandan_text = format_liuyao_full(
                self.current_yao_list,
                self.current_gua
            )
            show_liuyao_popup(pandan_text)
        except Exception as e:
            print(f'[ERROR] show_liuyao failed: {e}')
            show_toast('❌ 排盘失败')
    
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
