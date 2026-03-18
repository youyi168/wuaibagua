# 原生 Android 开发环境配置指南

## ✅ 环境已安装完成

### 已安装的组件

| 组件 | 版本 | 说明 |
|------|------|------|
| **JDK** | 17.0.18 | OpenJDK（Java 开发环境） |
| **Android SDK** | API 34 | Android 14 (Upside Down Cake) |
| **Build-Tools** | 34.0.0 | Android 构建工具 |
| **Platform-Tools** | 37.0.0 | ADB 和 Fastboot |
| **Command Line Tools** | 20.0 | SDK 管理工具 |
| **Gradle** | 8.5 | 构建自动化工具 |

### 安装位置

```bash
# Android SDK
~/Android/Sdk/

# SDK 目录结构
~/Android/Sdk/
├── cmdline-tools/latest/    # 命令行工具
├── platform-tools/          # ADB, Fastboot
├── platforms/android-34/    # Android 14 平台
├── build-tools/34.0.0/      # 构建工具
└── licenses/                # SDK 许可证

# Gradle
/opt/gradle-8.5/
```

### 环境变量

已添加到 `~/.bashrc`：

```bash
# Java
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Android SDK
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/build-tools/34.0.0

# Gradle
export PATH=/opt/gradle-8.5/bin:$PATH
```

**应用环境变量**：
```bash
source ~/.bashrc
```

## 🚀 快速开始

### 1. 验证环境

```bash
# 检查 Java
java -version

# 检查 ADB
adb --version

# 检查 Gradle
gradle --version

# 检查 SDK
sdkmanager --version
```

### 2. 创建第一个 Android 项目

#### 方法 A：使用命令行

```bash
# 创建项目目录
mkdir ~/Android/MyFirstApp
cd ~/Android/MyFirstApp

# 创建基本项目结构
mkdir -p app/src/main/java/com/example/myfirstapp
mkdir -p app/src/main/res/layout
mkdir -p app/src/main/res/values

# 创建 settings.gradle
cat > settings.gradle << 'EOF'
rootProject.name = "MyFirstApp"
include ':app'
EOF

# 创建项目级 build.gradle
cat > build.gradle << 'EOF'
plugins {
    id 'com.android.application' version '8.1.0' apply false
}
EOF

# 创建 app/build.gradle
cat > app/build.gradle << 'EOF'
plugins {
    id 'com.android.application'
}

android {
    namespace 'com.example.myfirstapp'
    compileSdk 34

    defaultConfig {
        applicationId "com.example.myfirstapp"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
        }
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
}
EOF

# 创建 gradle.properties
cat > gradle.properties << 'EOF'
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
EOF

# 创建简单布局
cat > app/src/main/res/layout/activity_main.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center"
    android:orientation="vertical">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello, Android!"
        android:textSize="24sp" />
</LinearLayout>
EOF

# 使用 Gradle Wrapper（推荐）
gradle wrapper

# 构建项目
./gradlew assembleDebug
```

#### 方法 B：使用 Android Studio（推荐）

1. **下载 Android Studio**
   ```bash
   # 如果还没安装 Android Studio
   wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.2.1.12/android-studio-2024.2.1.12-linux.tar.gz
   sudo tar -xzf android-studio*.tar.gz -C /opt/
   ```

2. **启动 Android Studio**
   ```bash
   /opt/android-studio/bin/studio.sh
   ```

3. **创建新项目**
   - File → New → New Project
   - 选择 "Empty Activity"
   - 填写项目名称、包名
   - 选择语言：Kotlin 或 Java
   - Minimum SDK: API 21 (Android 5.0)
   - 点击 Finish

### 3. 连接设备调试

```bash
# 启用手机开发者选项
# 设置 → 关于手机 → 连续点击"版本号"7 次
# 设置 → 开发者选项 → 启用"USB 调试"

# 连接 USB，检查设备
adb devices

# 如果看不到设备
adb kill-server
adb start-server
adb devices

# 安装 APK
adb install app/build/outputs/apk/debug/app-debug.apk

# 查看日志
adb logcat

# 无线调试（Android 11+）
adb pair <IP:端口>
adb connect <IP:端口>
```

## 📦 常用命令

### SDK 管理

```bash
# 列出已安装的组件
sdkmanager --list_installed

# 列出可安装的组件
sdkmanager --list

# 安装组件
sdkmanager "platforms;android-35"
sdkmanager "build-tools;35.0.0"
sdkmanager "system-images;android-34;google_apis;x86_64"

# 更新组件
sdkmanager --update

# 卸载组件
sdkmanager --uninstall "build-tools;33.0.0"

# 接受所有许可证
sdkmanager --licenses
```

### ADB 命令

```bash
# 设备管理
adb devices                    # 列出设备
adb reboot                     # 重启设备
adb reboot bootloader          # 重启到 bootloader
adb shell                      # 进入设备 shell

# 应用管理
adb install app.apk            # 安装 APK
adb uninstall com.example.app  # 卸载应用
adb shell pm list packages     # 列出已安装应用

# 文件传输
adb push file.txt /sdcard/     # 上传文件
adb pull /sdcard/photo.jpg .   # 下载文件

# 日志
adb logcat                     # 查看日志
adb logcat -c                  # 清除日志
adb logcat *:E                 # 只看错误
```

### Gradle 命令

```bash
# 构建
gradle assembleDebug           # 编译调试版
gradle assembleRelease         # 编译发布版
gradle clean                   # 清理构建

# 测试
gradle test                    # 运行单元测试
gradle connectedCheck          # 运行仪器测试

# 依赖
gradle dependencies            # 查看依赖树
gradle app:dependencies        # 查看 app 模块依赖

# 任务
gradle tasks                   # 列出所有任务
gradle tasks --all             # 列出所有任务（包括隐藏）
```

## 🛠️ 推荐的 IDE

### 1. Android Studio（官方推荐）

**优点**：
- 官方 IDE，功能最完整
- 内置布局编辑器
- 内置模拟器管理
- 智能代码补全
- 强大的调试工具

**安装**：
```bash
# 下载
wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.2.1.12/android-studio-2024.2.1.12-linux.tar.gz

# 解压
sudo tar -xzf android-studio*.tar.gz -C /opt/

# 创建快捷方式
sudo ln -s /opt/android-studio/bin/studio.sh /usr/local/bin/android-studio

# 启动
android-studio
```

### 2. VS Code + 插件

**优点**：
- 轻量级
- 启动快
- 丰富的插件生态

**安装插件**：
- Android iOS Emulator
- Gradle Language Support
- Java Extension Pack

### 3. IntelliJ IDEA

**优点**：
- 强大的 Java/Kotlin 支持
- 比 Android Studio 更轻量
- 可以安装 Android 插件

## 📱 创建模拟器

```bash
# 列出可用的系统镜像
sdkmanager --list | grep system-images

# 安装系统镜像
sdkmanager "system-images;android-34;google_apis;x86_64"

# 创建 AVD（Android Virtual Device）
avdmanager create avd \
    -n Pixel_7_API_34 \
    -k "system-images;android-34;google_apis;x86_64" \
    -d pixel_7

# 列出模拟器
emulator -list-avds

# 启动模拟器
emulator -avd Pixel_7_API_34

# 使用 Android Studio 的 AVD Manager（推荐）
# Tools → Device Manager → Create Device
```

## ⚠️ 常见问题

### 1. ADB 找不到设备

**解决**：
```bash
# 重启 ADB 服务器
adb kill-server
adb start-server

# 检查 USB 权限
ls -l /dev/bus/usb

# 添加 udev 规则
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="****", MODE="0666", GROUP="plugdev"' | \
    sudo tee /etc/udev/rules.d/51-android.rules
sudo udevadm control --reload-rules
```

### 2. SDK 许可证未接受

**解决**：
```bash
sdkmanager --licenses
```

### 3. Gradle 构建慢

**解决**：
```bash
# 编辑 gradle.properties
cat >> gradle.properties << 'EOF'
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.jvmargs=-Xmx4096m
EOF

# 使用国内镜像
# 编辑 ~/.gradle/init.gradle
cat > ~/.gradle/init.gradle << 'EOF'
allprojects {
    repositories {
        maven { url 'https://maven.aliyun.com/repository/google' }
        maven { url 'https://maven.aliyun.com/repository/public' }
        google()
        mavenCentral()
    }
}
EOF
```

### 4. 磁盘空间不足

**清理**：
```bash
# 清理 Gradle 缓存
rm -rf ~/.gradle/caches/

# 清理未使用的 SDK 组件
sdkmanager --uninstall <package>

# 清理旧版本构建工具
rm -rf ~/Android/Sdk/build-tools/3*
```

### 5. Java 版本冲突

**解决**：
```bash
# 检查 Java 版本
java -version

# 应该是 OpenJDK 17
# 如果不是，重新加载环境变量
source ~/.bashrc

# 或者手动设置
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

## 🔗 相关资源

- [Android 开发者文档](https://developer.android.com/)
- [Android Studio 下载](https://developer.android.com/studio)
- [Gradle 用户指南](https://docs.gradle.org/)
- [Kotlin 文档](https://kotlinlang.org/)
- [Material Design](https://material.io/)

## 📊 项目结构示例

```
MyFirstApp/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/example/myfirstapp/
│   │       │   └── MainActivity.kt
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   │   └── activity_main.xml
│   │       │   ├── values/
│   │       │   │   ├── strings.xml
│   │       │   │   └── colors.xml
│   │       │   └── drawable/
│   │       └── AndroidManifest.xml
│   └── build.gradle
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── build.gradle
├── settings.gradle
├── gradle.properties
└── local.properties
```

---

**最后更新**: 2026-03-18  
**环境版本**: JDK 17, SDK 34, Gradle 8.5
