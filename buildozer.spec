[app]
title = 吾爱八卦
package.name = wuaibagua
package.domain = org.wuaibagua
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json,ttf
version = 2.4.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE
android.api = 29
android.ndk_api = 21
android.minapi = 21
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# 包含字体目录
android.add_src = fonts/

[buildozer]
log_level = 2
warn_on_root = 1

# 国内镜像
p4a.source_url = https://gitee.com/mirrors/python-for-android.git
python.pip = 23.0.1
