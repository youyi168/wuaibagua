[app]
title = 我爱八卦
package.name = woaibagua
package.domain = org.woaibagua
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json,ttf,svg,db
version = 1.1.2
icon.filename = icon.png
# 启动图配置（拉伸覆盖全屏）
presplash.filename = splash.jpg
android.windowLayout = fill_parent
android.launchscreen = true
# 【关键修复】升级 Kivy 到 2.3.0 修复 hwui 线程 Bug
# Kivy 2.1.0 在 Android 13+ 有 hwuiTask mutex 竞争问题导致闪退
requirements = python3,kivy==2.3.0,pyjnius
p4a.requirements = kivy==2.3.0

# 使用清华镜像下载 Python 源码
hostpython3.url = https://mirrors.tuna.tsinghua.edu.cn/python/3.11.5/Python-3.11.5.tgz
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE,INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# 包含数据目录和字体目录（封装到 APK 内）
source.include_dirs = data,fonts,resources

[buildozer]
log_level = 2
warn_on_root = 1

# 使用国内镜像源加速下载
# Python for Android 源码镜像（清华源）
p4a.source_url = https://mirrors.tuna.tsinghua.edu.cn/git/python-for-android.git

# 【关键修复】使用自定义 AndroidManifest.xml 强制禁用 Vulkan
# 解决 Adreno Vulkan 驱动 0800.60 在 Android 13+ 上的崩溃问题
# OPPO/一加/真我设备必配
p4a.android-manifest.template = templates/android/AndroidManifest.xml
p4a.android-manifest.overrides = android:renderengine="opengl",android:graphics.opengl="es20"
# 备用镜像（阿里云）
# p4a.source_url = https://code.aliyun.com/python-for-android/python-for-android.git

# pip 国内镜像（清华源）
pip.index-url = https://pypi.tuna.tsinghua.edu.cn/simple
pip.extra-index-url = https://pypi.mirrors.ustc.edu.cn/simple/

# Gradle 镜像（阿里云）
gradle.repository-url = https://maven.aliyun.com/repository/public
