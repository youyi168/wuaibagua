#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分享功能模块
支持分享卦象结果到多个平台
"""

import os
from datetime import datetime
from config import Config


class ShareManager:
    """分享管理器"""
    
    def __init__(self):
        self.app_name = Config.APP_NAME
    
    def generate_share_text(self, result, include_detail=True, topic=''):
        """生成分享文本
        
        Args:
            result: 起卦结果字典
            include_detail: 是否包含详细信息
            topic: 占卜事项
            
        Returns:
            分享文本字符串
        """
        if not result:
            return ""
        
        ben_gua = result.get('ben_gua', {})
        bian_gua = result.get('bian_gua')
        dong_yao = result.get('dong_yao', [])
        
        # 基础信息
        text = f"【{self.app_name】起卦结果\n\n"
        text += f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        # 占卜事项
        if topic:
            text += f"📝 事项：{topic}\n"
        
        text += "\n"
        
        # 本卦
        text += f"🔮 本卦：{ben_gua.get('name', '未知')}\n"
        if ben_gua.get('upper_name') and ben_gua.get('lower_name'):
            text += f"   上{ben_gua['upper_name']}下{ben_gua['lower_name']}\n"
        
        # 变卦
        if bian_gua:
            text += f"🔄 变卦：{bian_gua.get('name', '未知')}\n"
        else:
            text += f"🔄 变卦：无（六爻皆静）\n"
        
        # 动爻
        if dong_yao:
            yao_names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
            dong_text = '、'.join([yao_names[i-1] for i in dong_yao])
            text += f"⚡ 动爻：{dong_text}\n"
        else:
            text += f"⚡ 动爻：无\n"
        
        # 详细信息
        if include_detail:
            text += "\n" + "=" * 30 + "\n"
            text += "断卦规则：一爻动，以动爻爻辞断之\n"
            text += "来源：《图解周易》传统金钱卦\n"
        
        # 应用信息
        text += f"\n—— {self.app_name} v{Config.VERSION}"
        
        return text
    
    def share_to_clipboard(self, result, include_detail=True):
        """分享到剪贴板
        
        Args:
            result: 起卦结果字典
            include_detail: 是否包含详细信息
            
        Returns:
            是否成功
        """
        text = self.generate_share_text(result, include_detail)
        
        try:
            # 尝试使用 pyperclip（桌面端）
            import pyperclip
            pyperclip.copy(text)
            print(f'[SHARE] 已复制到剪贴板')
            return True
        except ImportError:
            # Android 端使用 jnius
            try:
                from jnius import autoclass
                Clipboard = autoclass('android.content.ClipboardManager')
                ClipData = autoclass('android.content.ClipData')
                
                clipboard = Config.get_activity().getSystemService(
                    Config.get_activity().CLIPBOARD_SERVICE
                )
                clip = ClipData.newPlainText('share', text)
                clipboard.setPrimaryClip(clip)
                
                print(f'[SHARE] 已复制到剪贴板')
                return True
            except Exception as e:
                print(f'[SHARE] 复制到剪贴板失败：{e}')
                return False
    
    def share_to_wechat(self, result):
        """分享到微信（需要安装微信）"""
        text = self.generate_share_text(result)
        
        try:
            # Android 端使用 Intent 分享
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            intent = Intent(Intent.ACTION_SEND)
            intent.setType('text/plain')
            intent.putExtra(Intent.EXTRA_TEXT, text)
            intent.setPackage('com.tencent.mm')  # 微信包名
            
            PythonActivity.mActivity.startActivity(intent)
            print(f'[SHARE] 已打开微信分享')
            return True
        except Exception as e:
            print(f'[SHARE] 微信分享失败：{e}')
            return False
    
    def share_to_qq(self, result):
        """分享到 QQ"""
        text = self.generate_share_text(result)
        
        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            intent = Intent(Intent.ACTION_SEND)
            intent.setType('text/plain')
            intent.putExtra(Intent.EXTRA_TEXT, text)
            intent.setPackage('com.tencent.mobileqq')  # QQ 包名
            
            PythonActivity.mActivity.startActivity(intent)
            print(f'[SHARE] 已打开 QQ 分享')
            return True
        except Exception as e:
            print(f'[SHARE] QQ 分享失败：{e}')
            return False
    
    def share_system(self, result):
        """使用系统分享菜单"""
        text = self.generate_share_text(result)
        
        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            intent = Intent(Intent.ACTION_SEND)
            intent.setType('text/plain')
            intent.putExtra(Intent.EXTRA_TEXT, text)
            
            # 创建 chooser（系统分享菜单）
            chooser = Intent.createChooser(intent, '分享到...')
            PythonActivity.mActivity.startActivity(chooser)
            
            print(f'[SHARE] 已打开系统分享菜单')
            return True
        except Exception as e:
            print(f'[SHARE] 系统分享失败：{e}')
            # 回退到剪贴板
            return self.share_to_clipboard(result)
    
    def share_to_image(self, result, output_path=None):
        """生成分享图片（待实现）
        
        Args:
            result: 起卦结果字典
            output_path: 输出路径
            
        Returns:
            图片路径
        """
        # TODO: 使用 PIL 或 Kivy 截图生成精美图片
        print(f'[SHARE] 图片分享功能开发中...')
        return None
    
    def get_share_platforms(self):
        """获取可用分享平台"""
        platforms = []
        
        # 剪贴板（总是可用）
        platforms.append({
            'id': 'clipboard',
            'name': '复制文本',
            'icon': '📋'
        })
        
        # Android 平台检测
        try:
            from jnius import autoclass
            PackageManager = autoclass('android.content.pm.PackageManager')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            pm = PythonActivity.mActivity.getPackageManager()
            
            # 微信
            try:
                pm.getPackageInfo('com.tencent.mm', 0)
                platforms.append({
                    'id': 'wechat',
                    'name': '微信',
                    'icon': '💚'
                })
            except:
                pass
            
            # QQ
            try:
                pm.getPackageInfo('com.tencent.mobileqq', 0)
                platforms.append({
                    'id': 'qq',
                    'name': 'QQ',
                    'icon': '🐧'
                })
            except:
                pass
            
            # 系统分享
            platforms.append({
                'id': 'system',
                'name': '更多...',
                'icon': '📤'
            })
            
        except:
            # 桌面端
            try:
                import pyperclip
                pass
            except:
                pass
        
        return platforms


# 全局单例
_share_manager = None

def get_share_manager():
    """获取分享管理器单例"""
    global _share_manager
    if _share_manager is None:
        _share_manager = ShareManager()
    return _share_manager
