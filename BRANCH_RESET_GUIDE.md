# 分支重置指南

## 当前状态

### 本地分支

```
* main (10da7c7) ← 正常版本，已本地重置
* dev  (9696ffa) ← 开发版本，包含所有修复
```

### 远程分支

```
origin/main (9696ffa) ← 需要重置
origin/dev  (9696ffa) ← 开发分支，已创建
```

---

## ⚠️ 需要手动操作

由于 GitHub 保护规则，无法自动强制推送 main 分支。

### 方案 A: 在 GitHub 上删除并重建 main（推荐）

1. **访问 GitHub 仓库**
   ```
   https://github.com/youyi168/wuaibagua
   ```

2. **删除远程 main 分支**
   - Settings → Branches
   - 或者使用 GitHub CLI:
   ```bash
   gh api -X DELETE repos/youyi168/wuaibagua/git/refs/heads/main
   ```

3. **重新推送本地 main**
   ```bash
   cd /home/admin/.openclaw/workspace/wuaibagua
   git checkout main
   git push -u origin main
   ```

4. **重新添加分支保护**（可选）
   - Settings → Branches → Add branch protection rule
   - Branch name pattern: `main`

---

### 方案 B: 通过 Pull Request 合并

1. **创建 PR**
   ```
   https://github.com/youyi168/wuaibagua/pull/new/reset-main-force
   ```

2. **合并 PR**
   - 在 GitHub 上审查并合并

---

### 方案 C: 联系仓库管理员

如果以上方法都不可行，请联系仓库管理员手动重置。

---

## 分支策略（已建立）

```
main  ← 稳定版本（用户测试确认）
  ↑
  │ 合并请求
  │
dev   ← 开发调试分支（日常开发）
```

### 工作流程

1. **日常开发**: 在 `dev` 分支进行
2. **测试确认**: 用户在 `dev` 分支测试
3. **合并到 main**: 测试通过后合并到 `main`

---

## 当前分支状态

| 分支 | 提交 | 状态 | 说明 |
|------|------|------|------|
| **main (本地)** | 10da7c7 | ✅ 正常 | 已本地重置 |
| **main (远程)** | 9696ffa | ⚠️ 待重置 | 需要手动操作 |
| **dev** | 9696ffa | ✅ 正常 | 开发分支，已创建 |

---

## 下一步操作

1. ✅ **dev 分支已创建** - 包含所有新功能和修复
2. ⏳ **等待用户操作** - 在 GitHub 上重置 main 分支
3. 🔄 **用户在 dev 测试** - 确认功能正常
4. ✅ **合并到 main** - 测试通过后合并

---

## 快速命令参考

```bash
# 切换到 dev 分支进行开发
git checkout dev

# 查看分支状态
git branch -a

# 推送 dev 分支
git push origin dev

# 查看提交历史
git log --oneline --graph --all
```
