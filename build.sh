#!/bin/bash
# Linux 构建脚本 - 打包为完全独立的可执行文件

echo "================================"
echo "浏览器启动器 - Linux 构建"
echo "================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3"
    exit 1
fi

# 安装 Python 依赖（仅构建时需要）
echo "安装构建依赖..."
pip3 install pyinstaller customtkinter requests qrcode Pillow

# 构建
echo "开始构建..."
python3 build.py

# 添加执行权限
if [ -f "dist/BrowserLauncher" ]; then
    chmod +x dist/BrowserLauncher
    echo ""
    echo "================================"
    echo "✅ 构建成功!"
    echo "================================"
    echo ""
    echo "输出文件: dist/BrowserLauncher"
    echo ""
    echo "此可执行文件完全独立，无需安装任何依赖。"
    echo "可直接复制到其他 Linux 系统运行。"
    echo ""
    echo "运行方式: ./dist/BrowserLauncher"
    echo ""
fi

