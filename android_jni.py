#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android JNI 封装模块
延迟初始化，安全获取 Context
"""

import logging

logger = logging.getLogger('wuaibagua')

ANDROID_AVAILABLE = False
autoclass = None
ANDROID_CLIPBOARD_AVAILABLE = False


def init_android_jni():
    """延迟初始化 Android JNI"""
    global ANDROID_AVAILABLE, autoclass
    if ANDROID_AVAILABLE:
        return
    try:
        from jnius import autoclass as jni_autoclass
        autoclass = jni_autoclass
        ANDROID_AVAILABLE = True
        logger.info('[JNI] Android JNI 初始化成功')
    except ImportError as e:
        autoclass = None
        ANDROID_AVAILABLE = False
        logger.warning(f'[JNI] jnius not available (desktop): {e}')
    except Exception as e:
        autoclass = None
        ANDROID_AVAILABLE = False
        logger.error(f'[JNI] Android JNI 初始化失败：{e}')


def init_android_clipboard():
    """延迟初始化 Android 剪贴板"""
    global ANDROID_CLIPBOARD_AVAILABLE
    init_android_jni()
    ANDROID_CLIPBOARD_AVAILABLE = ANDROID_AVAILABLE


def get_android_context(app):
    """安全获取 Android Context"""
    try:
        if hasattr(app, 'getApplicationContext'):
            return app.getApplicationContext()
        if hasattr(app, 'mActivity') and app.mActivity:
            return app.mActivity.getApplicationContext()
        if autoclass:
            Activity = autoclass('android.app.Activity')
            if hasattr(Activity, 'mActivity') and Activity.mActivity:
                return Activity.mActivity.getApplicationContext()
    except Exception:
        pass
    return None


def copy_to_clipboard(text):
    """复制文本到剪贴板"""
    try:
        if not ANDROID_CLIPBOARD_AVAILABLE:
            init_android_clipboard()
        if ANDROID_CLIPBOARD_AVAILABLE and autoclass:
            Context = autoclass('android.content.Context')
            ClipboardManager = autoclass('android.content.ClipboardManager')
            ClipData = autoclass('android.content.ClipData')
            from kivy.app import App
            app = App.get_running_app()
            context = None
            if app:
                context = get_android_context(app)
            if not context:
                try:
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    context = PythonActivity.mActivity
                except Exception:
                    pass
            if context:
                clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE)
                clip = ClipData.newPlainText('wuaibagua', text)
                clipboard.setPrimaryClip(clip)
                logger.info(f'[Copy] {text[:50]}...')
            else:
                logger.warning('[Copy] 无法获取 Android Context')
        else:
            logger.info(f'[Copy] {text[:50]}...')
    except Exception as e:
        logger.error(f'[Copy] Failed: {e}')


def show_toast(message):
    """显示 Toast 提示"""
    try:
        if not ANDROID_CLIPBOARD_AVAILABLE:
            init_android_clipboard()
        if ANDROID_CLIPBOARD_AVAILABLE and autoclass:
            Toast = autoclass('android.widget.Toast')
            from kivy.app import App
            app = App.get_running_app()
            if app:
                context = get_android_context(app)
                if context:
                    toast = Toast.makeText(context, message, Toast.LENGTH_SHORT)
                    toast.show()
                    return
        logger.info(f'[Toast] {message}')
    except Exception as e:
        logger.error(f'[Toast] Failed: {e}')


def get_device_id():
    """获取设备识别码（Android）"""
    try:
        if not ANDROID_CLIPBOARD_AVAILABLE:
            init_android_clipboard()
        if ANDROID_CLIPBOARD_AVAILABLE and autoclass:
            Settings = autoclass('android.provider.Settings$Secure')
            from kivy.app import App
            app = App.get_running_app()
            if app:
                context = get_android_context(app)
                if context:
                    resolver = context.getContentResolver()
                    android_id = Settings.Secure.getString(resolver, 'android_id')
                    return android_id if android_id else 'default'
        return 'default'
    except Exception as e:
        logger.error(f'[DeviceID] Error: {e}')
        return 'default'
