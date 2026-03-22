# 音效文件说明

本目录存放应用音效文件。

## 所需音效

| 文件名 | 用途 | 时长 | 说明 |
|--------|------|------|------|
| `coin_toss.wav` | 投掷铜钱 | 0.5 秒 | 清脆的金属声 |
| `reveal.wav` | 显示结果 | 0.3 秒 | 轻柔的提示音 |
| `success.wav` | 成功操作 | 0.4 秒 | 愉悦的提示音 |
| `click.wav` | 按钮点击 | 0.1 秒 | 轻微的点击声 |
| `copy.wav` | 复制操作 | 0.2 秒 | 确认提示音 |

## 音效要求

- 格式：WAV 或 OGG
- 采样率：44.1kHz
- 位深度：16bit
- 声道：单声道或立体声
- 文件大小：每个 < 100KB

## 临时方案

如果暂时没有音效文件，应用会自动跳过音效播放，不影响正常使用。

可以在设置中开启/关闭音效。

## 推荐音效资源

- [Freesound](https://freesound.org/) - 免费音效库
- [OpenGameArt](https://opengameart.org/) - 开源游戏音效
- [ZapSplat](https://www.zapsplat.com/) - 免费音效

## 生成提示音（可选）

可以使用以下工具生成简单提示音：

```bash
# 使用 sox 生成简单提示音
sox -n -r 44100 coin_toss.wav synth 0.5 sine 800 fade 0.1 0.3 0.1
sox -n -r 44100 reveal.wav synth 0.3 sine 1200 fade 0.05 0.2 0.05
sox -n -r 44100 success.wav synth 0.4 sine 600 fade 0.1 0.2 0.1
```

---

**注意**: 音效文件为可选资源，应用没有音效文件也能正常运行。
