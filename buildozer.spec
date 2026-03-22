[app]
title = 我爱八卦
package.name = woaibagua
package.domain = org.woaibagua
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json,ttf,svg,mp3,ogg,wav
source.include_dirs = data,fonts,sounds
version = 1.6.0
icon.filename = icon.png

requirements = python3,kivy==2.3.0,pyjnius

# 使用清华镜像下载 Python 源码
hostpython3.url = https://mirrors.tuna.tsinghua.edu.cn/python/3.11.5/Python-3.11.5.tgz

orientation = portrait
fullscreen = 0
android.permissions = 
    VIBRATE,
    INTERNET,
    READ_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE,
    FOREGROUND_SERVICE,
    WAKE_LOCK

android.api = 36
android.minapi = 21
android.ndk_api = 21
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

# 入口文件
android.entry_point = main

[buildozer]
log_level = 2
warn_on_root = 1

# 使用国内镜像源加速下载
p4a.source_url = https://mirrors.tuna.tsinghua.edu.cn/git/python-for-android.git
pip.index-url = https://pypi.tuna.tsinghua.edu.cn/simple
pip.extra-index-url = https://pypi.mirrors.ustc.edu.cn/simple/
gradle.repository-url = https://maven.aliyun.com/repository/public
