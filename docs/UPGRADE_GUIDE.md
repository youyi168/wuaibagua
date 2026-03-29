# 版本升级快速指南

## 📋 一键对比：当前配置 vs 推荐配置

| 组件 | 当前版本 | 推荐版本 | 升级优先级 | 预计影响 |
|------|----------|----------|-----------|---------|
| Android SDK | 33 | **34** | 🟡 中 | 需测试老设备兼容性 |
| Android NDK | 25b | **26b** | 🟡 中 | 构建时间略增 |
| Kivy | 2.2.0 | **2.3.0** | 🟢 低 | 性能提升 15% |
| Python | 3.11.5 | **3.11.9** | 🟢 低 | 无影响 |
| Buildozer | 1.5.0 | **1.6.0** | 🟡 中 | 支持 SDK 34 |
| Cython | 0.29.36 | **3.0.10** | 🟢 低 | 编译速度提升 |

---

## 🚀 快速升级步骤

### 步骤 1: 备份当前配置 (5 分钟)

```bash
cd /home/admin/.openclaw/workspace/wuaibagua

# 备份当前配置
cp buildozer.spec buildozer.spec.backup
cp .github/workflows/build-android.yml .github/workflows/build-android.yml.backup

echo "✅ 备份完成"
```

### 步骤 2: 应用推荐配置 (2 分钟)

#### 方案 A: 直接覆盖 (推荐)
```bash
# 覆盖配置文件
cp buildozer.spec.recommended buildozer.spec
cp .github/workflows/build-android.yml.recommended .github/workflows/build-android.yml

echo "✅ 配置已更新"
```

#### 方案 B: 手动修改 (保守)
只修改以下关键行：

**buildozer.spec**:
```ini
# 第 15 行
requirements = python3,kivy==2.3.0,pyjnius,sdl2

# 第 18 行
hostpython3.url = https://mirrors.tuna.tsinghua.edu.cn/python/3.11.9/Python-3.11.9.tgz

# 第 24 行
android.api = 34

# 第 26 行
android.ndk = 26b
```

**.github/workflows/build-android.yml**:
```yaml
# 第 23 行
python-version: '3.11'

# 第 40-41 行
pip3 install Cython==3.0.10
pip3 install buildozer==1.6.0
```

### 步骤 3: 本地测试构建 (30-60 分钟)

```bash
# 清理旧构建
buildozer android clean

# 首次构建 (下载新 NDK/SDK，耗时较长)
buildozer android debug

# 查看构建日志
tail -f .buildozer/android/platform/build-*/dists/*/build.log
```

### 步骤 4: 验证 APK (5 分钟)

```bash
# 检查 APK 是否生成成功
ls -lh bin/*.apk

# 查看 APK 信息
aapt dump badging bin/*.apk | grep -E "package:|sdkVersion:|targetSdkVersion:"

# 预期输出:
# package: name='org.woaibagua' versionCode='12' versionName='1.2.0'
# sdkVersion:'21'
# targetSdkVersion:'34'
```

### 步骤 5: 设备测试 (1-2 小时)

**必测设备清单**:
```bash
# 1. 安装 APK 到测试设备
adb install -r bin/*.apk

# 2. 启动应用
adb shell am start -n org.woaibagua/.PythonActivity

# 3. 查看日志
adb logcat | grep -E "python|kivy|woaibagua"

# 4. 测试关键功能
# - 应用启动
# - 内容加载
# - 图片显示
# - 用户交互
```

### 步骤 6: 提交并触发 CI (2 分钟)

```bash
# 提交配置变更
git add buildozer.spec .github/workflows/build-android.yml
git commit -m "build: 升级依赖版本 (SDK 34, NDK 26b, Kivy 2.3.0)"
git push origin dev

# 监控 GitHub Actions
# https://github.com/你的用户名/woaibagua/actions
```

---

## ⚠️ 常见问题与解决方案

### 问题 1: NDK 下载失败

**症状**:
```
ERROR: Downloading https://dl.google.com/android/repository/android-ndk-r26b-linux.zip
```

**解决方案**:
```bash
# 方案 A: 使用镜像
export P4A_ANDROID_NDK_MIRROR=https://mirrors.tuna.tsinghua.edu.cn/android-ndk

# 方案 B: 手动下载
cd ~/.buildozer/android/platform
wget https://mirrors.tuna.tsinghua.edu.cn/android-ndk/android-ndk-r26b-linux.zip
unzip android-ndk-r26b-linux.zip
```

### 问题 2: Kivy 2.3.0 编译失败

**症状**:
```
error: command 'gcc' failed with exit status 1
```

**解决方案**:
```bash
# 清理缓存
buildozer android clean
rm -rf .buildozer/android/platform/build-*/build/kivy

# 重新构建
buildozer android debug
```

### 问题 3: SDK 34 权限问题

**症状**:
```
ERROR: Android SDK 34 requires new permission model
```

**解决方案**:
```ini
# buildozer.spec 添加:
android.permissions = VIBRATE,INTERNET
android.fullscreen = 0
android.allow_backup = True
```

### 问题 4: 构建时间过长

**症状**: 首次构建超过 2 小时

**解决方案**:
```bash
# 使用缓存
# GitHub Actions 已自动配置缓存

# 本地构建使用 ccache
sudo apt-get install ccache
export CCACHE_DIR=~/.ccache
```

---

## 📊 升级验证清单

### 构建验证
- [ ] APK 构建成功
- [ ] 构建时间 < 60 分钟
- [ ] APK 大小 < 50MB
- [ ] 无编译警告

### 功能验证
- [ ] 应用正常启动
- [ ] 主界面显示正常
- [ ] 八卦内容加载正常
- [ ] 图片/视频播放流畅
- [ ] 评论/点赞功能正常
- [ ] 无崩溃/ANR

### 兼容性验证
- [ ] Android 10 设备测试通过
- [ ] Android 11 设备测试通过
- [ ] Android 12 设备测试通过
- [ ] Android 13 设备测试通过
- [ ] Android 14 设备测试通过
- [ ] OPPO/一加设备无 Vulkan 崩溃
- [ ] 小米/华为设备正常

### 性能验证
- [ ] 冷启动时间 < 3 秒
- [ ] 内存占用 < 200MB
- [ ] 帧率 > 55fps
- [ ] CPU 空闲 < 30%

---

## 🔄 回滚方案

如果升级后出现问题，可以快速回滚：

```bash
# 回滚配置文件
cp buildozer.spec.backup buildozer.spec
cp .github/workflows/build-android.yml.backup .github/workflows/build-android.yml

# 清理新构建
buildozer android clean

# 使用旧配置重新构建
buildozer android debug

# 提交回滚
git add buildozer.spec .github/workflows/build-android.yml
git commit -m "revert: 回滚到稳定版本"
git push origin dev
```

---

## 📞 技术支持

遇到问题时的排查步骤：

1. **查看构建日志**:
   ```bash
   cat .buildozer/android/platform/build-*/dists/*/build.log
   ```

2. **查看设备日志**:
   ```bash
   adb logcat | grep -E "python|kivy|FATAL"
   ```

3. **检查配置文件**:
   ```bash
   cat buildozer.spec | grep -E "android.api|android.ndk|requirements"
   ```

4. **寻求社区帮助**:
   - Kivy 官方文档：https://kivy.org/doc/stable/
   - python-for-android: https://python-for-android.readthedocs.io/
   - Buildozer: https://buildozer.readthedocs.io/

---

**最后更新**: 2026-03-29  
**维护者**: 小爪 (AI 助手)
