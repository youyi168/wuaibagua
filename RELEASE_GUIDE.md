# v1.0.4 发布指南

## 🚀 推送到 GitHub

### 方式 1: 使用 Personal Access Token（推荐）

```bash
cd /home/admin/.openclaw/workspace/wuaibagua

# 替换 <你的 GitHub 用户名> 和 <你的 PAT>
git push https://<你的 GitHub 用户名>:<你的 PAT>@github.com/youyi168/wuaibagua.git main --tags
```

**获取 PAT**:
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选权限：`repo`, `workflow`, `write:packages`
4. 生成后复制 token

---

### 方式 2: 配置 SSH

```bash
# 1. 生成 SSH key（如果没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub

# 3. 添加到 GitHub: https://github.com/settings/keys

# 4. 测试连接
ssh -T git@github.com

# 5. 推送
git push origin main --tags
```

---

### 方式 3: 使用 Git Credential Manager

```bash
# Windows 已自动配置，直接推送
cd /home/admin/.openclaw/workspace/wuaibagua
git push origin main --tags

# 会弹出浏览器登录 GitHub
```

---

## 📦 自动编译流程

推送后 GitHub Actions 会自动触发：

### Android APK 编译
- **触发条件**: push tags (v*)
- **运行环境**: ubuntu-22.04
- **预计耗时**: 20-30 分钟
- **输出位置**: GitHub Releases

### Windows EXE 编译
- **触发条件**: push tags (v*)
- **运行环境**: windows-latest
- **预计耗时**: 10-15 分钟
- **输出位置**: GitHub Releases

---

## 📍 查看编译进度

1. 访问 https://github.com/youyi168/wuaibagua/actions
2. 查看 "Build Android APK" 和 "Build Windows EXE" 工作流
3. 等待编译完成（绿色 ✓）

---

## 📥 下载发布文件

编译完成后：

1. 访问 https://github.com/youyi168/wuaibagua/releases
2. 找到 v1.0.4 标签
3. 下载文件：
   - `woaibagua-1.0.4.apk` (Android)
   - `我爱八卦.exe` (Windows)

---

## ⚠️ 常见问题

### Q: 推送失败 "could not read Username"
**A**: 使用 Personal Access Token 方式推送

### Q: Android 编译失败
**A**: 检查 buildozer.spec 配置，查看 Actions 日志

### Q: Windows 编译失败
**A**: 检查 wuaibagua.spec 配置，查看 Actions 日志

### Q: Release 没有自动生成
**A**: 检查 tag 格式是否为 `v*`（如 v1.0.4）

---

## 🎯 快速命令汇总

```bash
# 1. 进入项目目录
cd /home/admin/.openclaw/workspace/wuaibagua

# 2. 查看当前状态
git status

# 3. 查看提交历史
git log --oneline -5

# 4. 查看 tag
git tag -l

# 5. 推送（选择一种方式）
git push https://username:token@github.com/youyi168/wuaibagua.git main --tags
# 或
git push origin main --tags
```

---

## 📱 测试建议

发布后请在以下设备测试：
- ✅ iPhone 13/14/15 (390x844)
- ✅ Android 手机 (360-412 x 800+)
- ✅ Windows 桌面 (1920x1080)

---

**发布时间**: 2026-03-22  
**版本**: v1.0.4  
**状态**: 准备就绪，等待推送 ✨
