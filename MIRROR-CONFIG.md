# 国内镜像源配置说明

## 已配置的镜像源

### 1. Python/pip 镜像
- **主镜像**: 清华大学开源软件镜像站
  - URL: `https://pypi.tuna.tsinghua.edu.cn/simple`
  - 配置：`~/.pip/pip.conf`
- **备用镜像**: 中国科学技术大学镜像站
  - URL: `https://pypi.mirrors.ustc.edu.cn/simple/`

### 2. Python for Android 源码镜像
- **主镜像**: 清华大学 Git 镜像
  - URL: `https://mirrors.tuna.tsinghua.edu.cn/git/python-for-android.git`
- **备用镜像**: 阿里云 Code
  - URL: `https://code.aliyun.com/python-for-android/python-for-android.git`

### 3. Gradle/Maven 镜像
- **阿里云 Maven 公共库**: `https://maven.aliyun.com/repository/public`
- **阿里云 Maven Google 库**: `https://maven.aliyun.com/repository/google`
- **配置位置**: `~/.gradle/gradle.properties`

### 4. Android SDK 镜像
- **清华大学**: `https://mirrors.tuna.tsinghua.edu.cn/AndroidSDK`
- **华为云**: `https://mirrors.huaweicloud.com/android/repository/`
- **腾讯云**: `https://mirrors.cloud.tencent.com/android/repository/`
- **阿里云**: `https://mirrors.aliyun.com/android/repository/`
- **配置位置**: `~/.android/repositories.cfg`

### 5. Android NDK 镜像
- **清华大学**: `https://mirrors.tuna.tsinghua.edu.cn/AndroidNDK`

## 镜像源优先级

1. **国内镜像优先** - 所有依赖优先从国内镜像下载
2. **自动故障转移** - 国内镜像失败时自动切换到官方源
3. **多源备份** - 配置多个镜像源提高可靠性

## 国内镜像站列表

| 服务商 | 类型 | URL |
|--------|------|-----|
| 清华大学 | 综合 | https://mirrors.tuna.tsinghua.edu.cn/ |
| 北京大学 | 综合 | https://mirrors.pku.edu.cn/ |
| 浙江大学 | 综合 | https://mirrors.zju.edu.cn/ |
| 中国科大 | 综合 | https://mirrors.ustc.edu.cn/ |
| 阿里云 | 综合 | https://mirrors.aliyun.com/ |
| 华为云 | 综合 | https://mirrors.huaweicloud.com/ |
| 腾讯云 | 综合 | https://mirrors.cloud.tencent.com/ |

## 使用说明

编译时会自动使用配置的国内镜像源，无需额外操作。

```bash
# 正常编译即可
buildozer android debug
```

## 验证镜像源

```bash
# 检查 pip 镜像
pip config list

# 检查 Gradle 镜像
cat ~/.gradle/gradle.properties

# 检查 Android SDK 镜像
cat ~/.android/repositories.cfg
```
