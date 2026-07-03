"""
浏览器启动器 - 检测系统浏览器并使用指定浏览器打开链接
"""
import subprocess
import os
import sys
import hashlib
import random
import string
import io
import customtkinter as ctk
import requests
import qrcode
from PIL import Image, ImageTk

# 跨平台兼容
if sys.platform == 'win32':
    import winreg


# 软件配置：标识 -> { salt, algorithm }
APP_CONFIGS = {
    '88': {
        'salt': 'browser_launcher_2024',
        'algorithm': 'sha256_digits'
    },
}

def calculate_password(random_code):
    """根据随机码计算验证码，前两位软件标识不参与运算"""
    # 提取软件标识（前两位）
    app_id = random_code[:2] if len(random_code) >= 2 else '88'
    
    # 提取实际随机码（去掉前两位）
    actual_code = random_code[2:] if len(random_code) > 2 else random_code
    
    # 获取配置
    config = APP_CONFIGS.get(app_id, {'salt': 'default_salt', 'algorithm': 'sha256_digits'})
    salt = config['salt']
    
    # 加盐后计算
    hash_result = hashlib.sha256((actual_code + salt).encode()).hexdigest()
    
    code = ''
    for char in hash_result:
        if len(code) >= 8:
            break
        if char.isdigit():
            code += char
    while len(code) < 8:
        code += '0'
    return code


class VerifyDialog(ctk.CTkToplevel):
    """验证对话框"""
    def __init__(self, parent):
        super().__init__(parent)
        self.verified = False
        
        self.title("验证")
        self.geometry("400x350")
        self.resizable(False, False)
        
        # 模态窗口
        self.grab_set()
        
        # 居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 350) // 2
        self.geometry(f"+{x}+{y}")
        
        # 生成随机码
        self.random_code = self.generate_random_code()
        
        self.setup_ui()
        
        self.wait_window()
    
    def get_device_info(self):
        """获取设备信息"""
        import uuid
        import platform
        
        # 获取 MAC 地址
        mac = uuid.getnode()
        mac_str = ':'.join(['{:02x}'.format((mac >> elements) & 0xff) for elements in range(0, 8*6, 8)][::-1])
        
        # 获取机器名
        hostname = platform.node()
        
        # 获取系统信息
        system = platform.system()
        
        return f"{mac_str}-{hostname}-{system}"
    
    def generate_random_code(self):
        """根据设备信息和随机数生成16位随机码，前两位固定为88"""
        import uuid
        
        # 设备信息 + 随机数
        device_info = self.get_device_info()
        random_part = str(uuid.uuid4())
        combined = f"{device_info}-{random_part}"
        
        # SHA256 哈希
        hash_result = hashlib.sha256(combined.encode()).hexdigest()
        
        # 转换为大写字母和数字
        code = ''
        for char in hash_result:
            if len(code) >= 14:  # 只需要14位，前两位固定
                break
            if char.isdigit():
                code += char
            elif char.isalpha():
                code += char.upper()
        
        while len(code) < 14:
            code += random.choice(string.ascii_uppercase + string.digits)
        
        return '88' + code[:14]
    
    def generate_qr_code(self, data):
        """生成二维码图片"""
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为CTkImage
        img = img.resize((150, 150))
        return ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))
        
    def setup_ui(self):
        ctk.CTkLabel(self, text="请扫描二维码获取验证码", font=("", 16)).pack(pady=10)
        
        # 显示二维码
        self.qr_image = self.generate_qr_code(self.random_code)
        ctk.CTkLabel(self, image=self.qr_image, text="").pack(pady=5)
        
        # 显示随机码
        ctk.CTkLabel(self, text=f"随机码: {self.random_code}", font=("", 14, "bold"), text_color="black").pack(pady=5)
        
        # 验证码输入
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(frame, text="验证码:").pack(side="left", padx=5)
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="8位验证码", width=150)
        self.password_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # 确认按钮
        ctk.CTkButton(self, text="验证", width=100, command=self.verify).pack(pady=10)
        
        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.pack()
    
    def verify(self):
        password = self.password_entry.get().strip()
        
        if not password:
            self.status_label.configure(text="请输入验证码")
            return
        
        correct_password = calculate_password(self.random_code)
        if password == correct_password:
            self.verified = True
            self.destroy()
        else:
            self.status_label.configure(text="验证码错误")


def detect_browsers():
    """检测系统已安装的浏览器"""
    browsers = {}
    
    if sys.platform == 'win32':
        # Windows 系统
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Clients\StartMenuInternet"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Clients\StartMenuInternet"),
        ]
        
        for hkey, path in reg_paths:
            try:
                with winreg.OpenKey(hkey, path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    name, _ = winreg.QueryValueEx(subkey, None)
                                except:
                                    name = subkey_name
                                
                                try:
                                    cmd_key = winreg.OpenKey(subkey, r"shell\open\command")
                                    cmd, _ = winreg.QueryValueEx(cmd_key, None)
                                    exe_path = cmd.strip('"').split('"')[0] if '"' in cmd else cmd.split()[0]
                                    if os.path.exists(exe_path):
                                        browsers[name] = exe_path
                                except:
                                    pass
                            i += 1
                        except OSError:
                            break
            except OSError:
                pass
        
        common_paths = {
            "Google Chrome": [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ],
            "Mozilla Firefox": [
                os.path.expandvars(r"%ProgramFiles%\Mozilla Firefox\firefox.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"),
            ],
            "Microsoft Edge": [
                os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            ],
            "Brave": [
                os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            ],
        }
        
        for name, paths in common_paths.items():
            if name not in browsers:
                for p in paths:
                    if os.path.exists(p):
                        browsers[name] = p
                        break
    elif sys.platform == 'linux':
        # Linux 系统
        common_browsers = {
            "Google Chrome": [
                "google-chrome", "google-chrome-stable",
                "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                "/opt/google/chrome/google-chrome",
                os.path.expanduser("~/.local/share/flatpak/exports/bin/com.google.Chrome"),
            ],
            "Mozilla Firefox": [
                "firefox", "/usr/bin/firefox", "/snap/bin/firefox",
                "/usr/lib/firefox/firefox",
                os.path.expanduser("~/.local/share/flatpak/exports/bin/org.mozilla.firefox"),
            ],
            "Microsoft Edge": [
                "microsoft-edge", "microsoft-edge-stable",
                "/usr/bin/microsoft-edge", "/opt/microsoft/msedge/microsoft-edge",
            ],
            "Chromium": [
                "chromium", "chromium-browser",
                "/usr/bin/chromium", "/usr/bin/chromium-browser",
                "/snap/bin/chromium",
                os.path.expanduser("~/.local/share/flatpak/exports/bin/org.chromium.Chromium"),
            ],
            "Brave": [
                "brave", "brave-browser",
                "/usr/bin/brave-browser", "/opt/brave.com/brave/brave-browser",
                "/snap/bin/brave",
            ],
            "Vivaldi": [
                "vivaldi", "/usr/bin/vivaldi", "/opt/vivaldi/vivaldi",
            ],
            "Opera": [
                "opera", "/usr/bin/opera", "/snap/bin/opera",
            ],
        }
        
        for name, cmds in common_browsers.items():
            for cmd in cmds:
                # 检查是否是绝对路径
                if cmd.startswith('/') or cmd.startswith('~'):
                    expanded = os.path.expanduser(cmd)
                    if os.path.exists(expanded):
                        browsers[name] = expanded
                        break
                else:
                    # 检查是否在 PATH 中
                    result = subprocess.run(['which', cmd], capture_output=True, text=True)
                    if result.returncode == 0:
                        browsers[name] = result.stdout.strip()
                        break
        
        # 尝试通过 xdg-mime 获取默认浏览器
        try:
            result = subprocess.run(
                ['xdg-mime', 'query', 'default', 'x-scheme-handler/http'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                default_browser = result.stdout.strip()
                if default_browser and 'Default Browser' not in browsers:
                    # 尝试找到对应的可执行文件
                    desktop_files = [
                        f'/usr/share/applications/{default_browser}',
                        os.path.expanduser(f'~/.local/share/applications/{default_browser}'),
                    ]
                    for desktop_file in desktop_files:
                        if os.path.exists(desktop_file):
                            # 解析 .desktop 文件获取 Exec
                            with open(desktop_file, 'r') as f:
                                for line in f:
                                    if line.startswith('Exec='):
                                        exec_cmd = line.split('=', 1)[1].strip()
                                        # 移除参数占位符
                                        exec_cmd = exec_cmd.split('%')[0].strip()
                                        if exec_cmd:
                                            browsers['Default Browser'] = exec_cmd
                                            break
                            break
        except:
            pass
    
    elif sys.platform == 'darwin':
        # macOS 系统
        common_browsers = {
            "Safari": "/Applications/Safari.app/Contents/MacOS/Safari",
            "Google Chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "Mozilla Firefox": "/Applications/Firefox.app/Contents/MacOS/firefox",
            "Microsoft Edge": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "Brave": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "Chromium": "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "Opera": "/Applications/Opera.app/Contents/MacOS/Opera",
            "Vivaldi": "/Applications/Vivaldi.app/Contents/MacOS/Vivaldi",
        }
        
        for name, path in common_browsers.items():
            if os.path.exists(path):
                browsers[name] = path
    
    return browsers


def get_redirect_url(url, ip):
    """获取重定向链接"""
    headers = {
        "Host": url.split("/")[2] if "/" in url else url,
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Client-Ip": ip,
        "X-Forwarded-For": ip,
        "Remote_Addr": ip,
    }
    
    try:
        response = requests.get(url, headers=headers, allow_redirects=False, timeout=10)
        location = response.headers.get("Location", "")
        return location, response.status_code
    except Exception as e:
        return "", str(e)


class BrowserLauncherApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("登录")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 居中显示
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 500) // 2
        y = (self.root.winfo_screenheight() - 400) // 2
        self.root.geometry(f"+{x}+{y}")
        
        self.browsers = detect_browsers()
        
        self.setup_ui()
        
    def setup_ui(self):
        # 标题
        title = ctk.CTkLabel(self.root, text="", font=("", 20, "bold"))
        title.pack(pady=5)
        
        # URL 输入
        url_frame = ctk.CTkFrame(self.root)
        url_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(url_frame, text="URL:", width=60).pack(side="left", padx=5)
        self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="输入链接...")
        self.url_entry.pack(side="left", padx=5, pady=10, fill="x", expand=True)
        
        # IP 输入
        ip_frame = ctk.CTkFrame(self.root)
        ip_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(ip_frame, text="IP:", width=60).pack(side="left", padx=5)
        self.ip_entry = ctk.CTkEntry(ip_frame, placeholder_text="输入 IP 地址...")
        self.ip_entry.pack(side="left", padx=5, pady=10, fill="x", expand=True)
        
        # 浏览器选择
        browser_frame = ctk.CTkFrame(self.root)
        browser_frame.pack(fill="both", padx=20, pady=10, expand=True)
        
        ctk.CTkLabel(browser_frame, text="选择浏览器打开:", font=("", 14)).pack(pady=10)
        
        self.browser_btns_frame = ctk.CTkScrollableFrame(browser_frame, height=180)
        self.browser_btns_frame.pack(fill="both", padx=10, pady=5, expand=True)
        
        if self.browsers:
            for name, path in self.browsers.items():
                btn = ctk.CTkButton(
                    self.browser_btns_frame, 
                    text=f"🌐 {name}",
                    command=lambda p=path, n=name: self.fetch_and_open(p, n)
                )
                btn.pack(pady=5, fill="x")
        else:
            ctk.CTkLabel(self.browser_btns_frame, text="未检测到浏览器", text_color="gray").pack(pady=20)
        
        # 状态栏
        self.status_label = ctk.CTkLabel(self.root, text=f"已检测到 {len(self.browsers)} 个浏览器", text_color="gray")
        self.status_label.pack(pady=10)
        
    def fetch_and_open(self, browser_path, browser_name):
        """获取链接并用指定浏览器打开"""
        url = self.url_entry.get().strip()
        ip = self.ip_entry.get().strip()
        
        if not url:
            self.status_label.configure(text="请输入 URL", text_color="red")
            return
        
        if not ip:
            self.status_label.configure(text="请输入 IP", text_color="red")
            return
        
        self.status_label.configure(text="正在获取链接...", text_color="gray")
        self.root.update()
        
        location, status = get_redirect_url(url, ip)
        
        if location:
            try:
                # 跨平台启动浏览器
                if sys.platform == 'win32':
                    subprocess.Popen([browser_path, location])
                elif sys.platform == 'darwin':
                    # macOS 使用 open 命令
                    subprocess.Popen(['open', '-a', browser_path, location])
                else:
                    # Linux 直接执行
                    subprocess.Popen([browser_path, location], start_new_session=True)
                self.status_label.configure(text=f"已在 {browser_name} 中打开", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"打开失败: {e}", text_color="red")
        else:
            self.status_label.configure(text=f"获取链接失败: {status}", text_color="red")
    
    def run(self):
        # 先验证
        verify = VerifyDialog(self.root)
        if not verify.verified:
            self.root.destroy()
            return
        
        # 验证通过，显示主窗口
        self.root.mainloop()


if __name__ == "__main__":
    app = BrowserLauncherApp()
    app.run()
