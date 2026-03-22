[app]
title = 我爱八卦
package.name = woaibagua
package.domain = org.woaibagua
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json,ttf,svg,mp3,ogg,wav
source.include_dirs = data,fonts,sounds,resources
version = 1.6.0
icon.filename = icon.png
requirements = python3,kivy,pyjnius
# 使用清华镜像下载 Python 源码
hostpython3.url = https://mirrors.tuna.tsinghua.edu.cn/python/3.11.5/Python-3.11.5.tgz
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# 包含数据目录和字体目录
source.include_dirs = data,fonts

[buildozer]
log_level = 2
warn_on_root = 1

# 使用国内镜像源加速下载
# Python for Android 源码镜像（清华源）
p4a.source_url = https://mirrors.tuna.tsinghua.edu.cn/git/python-for-android.git
# 备用镜像（阿里云）
# p4a.source_url = https://code.aliyun.com/python-for-android/python-for-android.git

# pip 国内镜像（清华源）
pip.index-url = https://pypi.tuna.tsinghua.edu.cn/simple
pip.extra-index-url = https://pypi.mirrors.ustc.edu.cn/simple/

# Gradle 镜像（阿里云）
gradle.repository-url = https://maven.aliyun.com/repository/public
