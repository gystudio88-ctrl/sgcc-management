@echo off
chcp 65001 >nul
echo 正在打包浏览器启动器...

pyinstaller browser_launcher.py --name BrowserLauncher --onefile --windowed --noconfirm --clean --hidden-import customtkinter --hidden-import requests

echo.
echo 打包完成! 输出文件: dist\BrowserLauncher.exe
pause
