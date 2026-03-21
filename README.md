# 我爱八卦

一款简洁的金钱卦算卦软件，支持 Windows 和 Android 平台。

## 功能特点

- 🎲 **电脑起卦** - 自动投掷三枚铜钱起卦
- ✋ **手动起卦** - 自行选择每次投掷结果
- 📖 **本卦变卦** - 显示本卦、变卦及动爻信息
- 🔍 **网络搜索** - 点击卦名跳转百度搜索详解
- 🎨 **八卦符号** - 显示传统八卦符号（☰☱☲☳☴☵☶☷）

## 下载安装

### Windows

从 [Releases](https://github.com/youyi168/wuaibagua/releases) 页面下载 `我爱八卦.exe`，双击运行即可。

### Android

从 [Releases](https://github.com/youyi168/wuaibagua/releases) 页面下载 APK 文件安装。

## 使用说明

1. 选择起卦方式（电脑起卦/手动起卦）
2. 点击"开始起卦"
3. 查看本卦、变卦和动爻信息
4. 点击卦名或🔍按钮可搜索详解

## 构建

### Windows EXE

```bash
pip install pyinstaller kivy
pyinstaller wuaibagua.spec
```

### Android APK

```bash
pip install buildozer
buildozer android debug
```

## 技术栈

- Python 3.10+
- Kivy - 跨平台 GUI 框架
- PyInstaller - Windows 打包
- Buildozer - Android 打包

## 许可证

MIT License
