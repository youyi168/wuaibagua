# 我爱八卦 v1.0.4

一款简洁的金钱卦算卦软件，支持 Windows 和 Android 平台。

![GitHub release](https://img.shields.io/github/v/release/youyi168/wuaibagua)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/youyi168/wuaibagua/build-android.yml)
![License](https://img.shields.io/github/license/youyi168/wuaibagua)

---

## ✨ v1.0.4 新特性

- 📱 **响应式 UI** - 自动适配手机/桌面屏幕
- 🎨 **动态布局** - 支持 320x480 ~ 2560x1440+ 分辨率
- 🔄 **自动调整** - 窗口大小变化时自动优化布局
- 🔍 **网络搜索** - 点击按钮跳转百度搜索卦象详解

---

## 🎯 功能特点

- 🎲 **电脑起卦** - 自动投掷三枚铜钱起卦
- 📖 **本卦变卦** - 显示本卦、变卦及动爻信息
- 🔍 **网络搜索** - 点击按钮跳转百度搜索详解
- 🎨 **八卦符号** - 显示传统八卦符号（☰☱☲☳☴☵☶☷）
- 📱 **响应式设计** - 完美适配各种屏幕尺寸
- 📜 **本地释义** - 64 卦完整卦辞爻辞，符合《图解周易》

---

## 📱 适配设备

| 设备类型 | 分辨率 | 适配效果 |
|---------|--------|---------|
| iPhone 13/14/15 | 390x844 | ✅ 完美适配 ✨ |
| iPhone Pro Max | 428x926 | ✅ 适度放大 |
| Android 旗舰 | 360-412 x 800+ | ✅ 自动适配 |
| 小屏手机 | 320x480 | ✅ 缩小显示 |
| 平板 (竖屏) | 768x1024 | ✅ 适度放大 |
| 桌面 (1080p) | 1920x1080 | ✅ 按高度缩放 |
| 桌面 (2K/4K) | 2560x1440+ | ✅ 限制最大 2 倍 |

---

## 📥 下载安装

### Windows

从 [Releases](https://github.com/youyi168/wuaibagua/releases) 页面下载 `我爱八卦.exe`，双击运行即可。

### Android

从 [Releases](https://github.com/youyi168/wuaibagua/releases) 页面下载 APK 文件安装。

---

## 📖 使用说明

1. 点击「电脑起卦」按钮
2. 查看本卦、变卦和动爻信息
3. 点击「🔍 百度搜索」查看卦象详解
4. 点击「清空」重新开始

### 断卦规则

遵循《图解周易》传统规则：
- **六爻皆静** - 以本卦卦辞断之
- **一爻动** - 以动爻爻辞断之
- **两爻动** - 阴爻为主/上爻为主
- **三爻动** - 取中间爻断之
- **六爻皆动** - 乾用九/坤用六/他卦看变卦

---

## 🛠️ 构建

### Windows EXE

```bash
pip install -r requirements-win.txt
pyinstaller wuaibagua.spec
```

### Android APK

```bash
pip install buildozer
buildozer android debug
```

---

## 📋 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

### v1.0.4 (2026-03-22)
- ✨ 响应式 UI，自动适配手机/桌面
- 🎨 动态字体和布局系统
- 🔍 添加百度搜索功能
- 🐛 修复小屏幕显示问题

---

## 📚 技术栈

- **Python 3.10+** - 编程语言
- **Kivy** - 跨平台 GUI 框架
- **PyInstaller** - Windows 打包
- **Buildozer** - Android 打包

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- 《图解周易》- 传统断卦规则
- Kivy 团队 - 优秀的跨平台框架
- GitHub Actions - 自动编译服务

---

## 📞 反馈

如有问题或建议，请：
1. 提交 [Issue](https://github.com/youyi168/wuaibagua/issues)
2. 联系开发者

---

**版本**: v1.0.4  
**更新日期**: 2026-03-22  
**开发者**: 吾爱八卦团队
