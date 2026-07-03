"""
浏览器启动器打包脚本
支持 Windows / Linux / macOS
完全独立打包，无需安装任何依赖
"""
import PyInstaller.__main__
import os
import sys
import platform
import shutil

# 应用名称
APP_NAME = "BrowserLauncher"
# 主脚本
MAIN_SCRIPT = "browser_launcher.py"

# 基础参数
base_args = [
    MAIN_SCRIPT,
    "--name", APP_NAME,
    "--onefile",           # 打包成单个可执行文件
    "--noconfirm",         # 覆盖输出目录
    "--clean",             # 清理临时文件
    # 核心依赖
    "--hidden-import", "customtkinter",
    "--hidden-import", "customtkinter.widgets",
    "--hidden-import", "customtkinter.windows",
    "--hidden-import", "requests",
    "--hidden-import", "qrcode",
    "--hidden-import", "PIL",
    "--hidden-import", "PIL._tkinter_finder",
    # tkinter 相关
    "--hidden-import", "tkinter",
    "--hidden-import", "tkinter.filedialog",
    "--hidden-import", "tkinter.messagebox",
    "--hidden-import", "tkinter.scrolledtext",
    # collections 相关（customtkinter 依赖）
    "--hidden-import", "collections",
    "--hidden-import", "collections.abc",
    # 打包所有数据文件
    "--collect-all", "customtkinter",
    "--collect-all", "qrcode",
]

# 根据平台添加特定参数
if sys.platform == 'win32':
    base_args.extend([
        "--windowed",          # 不显示控制台窗口
        # Windows 特定的 tkinter hidden imports
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "_tkinter",
    ])
elif sys.platform == 'darwin':
    # macOS
    base_args.extend([
        "--windowed",
        "--osx-bundle-identifier", "com.sgcc.browserlauncher",
        # macOS 特定
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "_tkinter",
    ])
else:
    # Linux
    base_args.extend([
        "--windowed",          # 也不显示控制台
        # Linux tkinter
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "_tkinter",
    ])

PyInstaller.__main__.run(base_args)

# 输出构建结果
system = platform.system()
if system == 'Windows':
    print(f"\n✅ 打包完成! 输出文件: dist/{APP_NAME}.exe")
    print("   可直接运行，无需安装任何依赖")
elif system == 'Darwin':
    print(f"\n✅ 打包完成! 输出文件: dist/{APP_NAME}")
    print("   可直接运行，无需安装任何依赖")
else:
    print(f"\n✅ 打包完成! 输出文件: dist/{APP_NAME}")
    print("   首次运行请执行: chmod +x dist/BrowserLauncher")
    print("   可直接运行，无需安装任何依赖")

# 显示文件大小
output_file = os.path.join("dist", APP_NAME + (".exe" if system == 'Windows' else ""))
if os.path.exists(output_file):
    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"   文件大小: {size_mb:.1f} MB")

