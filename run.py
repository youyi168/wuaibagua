#!/bin/bash
# 启动脚本（开发环境使用）

cd "$(dirname "$0")"

# 添加 src 到 Python 路径
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# 运行主程序
python3 src/wuaibagua_kivy.py
