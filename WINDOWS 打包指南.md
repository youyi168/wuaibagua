# 吾爱八卦 - Windows 打包指南

## 📦 快速打包（推荐）

### 方法一：一键打包脚本

1. **在 Windows 11 上双击运行** `build-windows.bat`
2. 等待打包完成（约 5-10 分钟）
3. 在 `dist/` 目录找到 `吾爱八卦.exe`

---

## 🔧 手动打包步骤

### 1. 环境准备

**系统要求：**
- Windows 10/11 (64 位)
- Python 3.10 或 3.11（推荐 3.10）
- 至少 2GB 可用磁盘空间

**安装 Python：**
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.10.x
3. 安装时勾选 **"Add Python to PATH"**

### 2. 克隆项目

```bash
git clone https://github.com/youyi168/wuaibagua.git
cd wuaibagua
```

### 3. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv win-venv

# 激活虚拟环境
win-venv\Scripts\activate
```

### 4. 安装依赖

```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装 Kivy 和依赖
pip install -r requirements-win.txt
```

### 5. 测试程序

```bash
# 确保程序能正常运行
python main.py
```

### 6. 打包为 EXE

```bash
# 安装 PyInstaller
pip install pyinstaller pyinstaller-hooks-contrib

# 执行打包
pyinstaller wuaibagua.spec --clean
```

### 7. 获取结果

打包完成后，在以下位置找到可执行文件：

```
wuaibagua/dist/吾爱八卦.exe
```

---

## 📊 打包选项说明

### 单文件模式（推荐）

生成的 `wuaibagua.spec` 默认配置：
- ✅ 单文件输出（所有依赖打包进一个 exe）
- ✅ 无控制台窗口（纯 GUI 应用）
- ✅ 包含所有数据文件和字体
- ✅ 使用 UPX 压缩（减小文件体积）

### 自定义配置

如果需要修改，编辑 `wuaibagua.spec`：

```python
# 添加程序图标
exe = EXE(
    ...
    icon='icon.ico',  # 添加你的图标文件
)

# 显示控制台窗口（调试用）
exe = EXE(
    ...
    console=True,  # 改为 True 显示控制台
)

# 禁用压缩（加快启动速度）
exe = EXE(
    ...
    upx=False,  # 禁用 UPX 压缩
)
```

---

## 🐛 常见问题

### 问题 1：找不到 Python

**错误：** `'python' 不是内部或外部命令`

**解决：**
1. 重新安装 Python
2. 安装时勾选 "Add Python to PATH"
3. 或手动添加：`C:\Users\你的用户名\AppData\Local\Programs\Python\Python310\` 到系统 PATH

### 问题 2：Kivy 安装失败

**错误：** `Could not find a version that satisfies the requirement kivy`

**解决：**
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple kivy
```

### 问题 3：打包后运行闪退

**调试方法：**
1. 打开命令行
2. 运行：`吾爱八卦.exe`
3. 查看错误信息

**常见原因：**
- 缺少数据文件（检查 `data/` 目录是否打包）
- 字体文件损坏（重新下载字体）
- 缺少 DLL（重新安装 kivy-deps.sdl2）

### 问题 4：杀毒软件误报

**原因：** PyInstaller 打包的程序可能被误报

**解决：**
1. 添加到杀毒软件白名单
2. 或使用数字签名（需要购买证书）

---

## 📦 文件体积优化

默认打包后约 **80-120 MB**，优化方法：

### 1. 使用 UPX 压缩（已启用）
```bash
pip install upx
# PyInstaller 会自动使用
```

### 2. 移除不必要的模块
编辑 `wuaibagua.spec`，在 `excludes` 中添加：
```python
excludes=[
    'matplotlib',
    'scipy',
    'numpy.testing',
    'tkinter',
]
```

### 3. 使用更小的字体
当前字体文件约 19MB，可以：
- 使用 Windows 系统自带中文字体（如 `msyh.ttc`）
- 或创建字体子集

---

## 🚀 分发建议

### 创建安装包

使用 **Inno Setup** 创建安装程序：

1. 下载 Inno Setup：https://jrsoftware.org/isdl.php
2. 创建脚本：

```iss
[Setup]
AppName=吾爱八卦
AppVersion=2.4.0
DefaultDirName={autopf}\吾爱八卦
DefaultGroupName=吾爱八卦
OutputDir=installer

[Files]
Source: "dist\吾爱八卦.exe"; DestDir: "{app}"
Source: "data\*"; DestDir: "{app}\data"; Flags: recursesubdirs
Source: "fonts\*"; DestDir: "{app}\fonts"

[Icons]
Name: "{group}\吾爱八卦"; Filename: "{app}\吾爱八卦.exe"
```

3. 编译生成 `setup.exe`

### 创建绿色版

直接分发 `dist/` 目录：
1. 压缩 `dist/吾爱八卦.exe`
2. 或创建包含以下文件的文件夹：
   - `吾爱八卦.exe`
   - `data/` （卦辞数据）
   - `fonts/` （字体文件）

---

## 📝 检查清单

打包前确认：

- [ ] Python 版本 3.10 或 3.11
- [ ] 已安装所有依赖
- [ ] 程序能正常运行 (`python main.py`)
- [ ] `data/` 目录包含 64 个卦辞文件
- [ ] `fonts/` 目录包含有效字体文件
- [ ] 测试过打包后的 exe

---

## 🔗 相关资源

- [Kivy 官方文档](https://kivy.org/doc/stable/)
- [PyInstaller 文档](https://pyinstaller.org/en/stable/)
- [Inno Setup 下载](https://jrsoftware.org/isinfo.php)
- [项目 GitHub](https://github.com/youyi168/wuaibagua)

---

## 💡 提示

- **首次打包**可能需要 10-15 分钟（下载依赖）
- **后续打包**只需 2-3 分钟
- 建议在 **干净的系统** 上打包，避免依赖冲突
- 打包后的 exe 可以在 **任何 Windows 10/11** 电脑上运行（无需 Python）
