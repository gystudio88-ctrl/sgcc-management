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
        # Linux 系统 - 使用 shutil.which 查找浏览器
        import shutil
        
        browser_commands = [
            ("Google Chrome", ["google-chrome", "google-chrome-stable"]),
            ("Mozilla Firefox", ["firefox"]),
            ("Microsoft Edge", ["microsoft-edge", "microsoft-edge-stable"]),
            ("Chromium", ["chromium", "chromium-browser"]),
            ("Brave", ["brave", "brave-browser"]),
            ("Vivaldi", ["vivaldi"]),
            ("Opera", ["opera"]),
        ]
        
        for name, cmds in browser_commands:
            for cmd in cmds:
                browser_path = shutil.which(cmd)
                if browser_path:
                    browsers[name] = browser_path
                    break
    
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
    import ssl
    import http.client
    import subprocess
    
    # 确保 URL 有协议
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    
    print(f"[DEBUG] get_redirect_url: url={url}")
    
    # 解析 URL
    parsed = url.split("/")
    protocol = parsed[0].replace(":", "")
    host = parsed[2].split(":")[0]
    port = 443 if protocol == "https" else 80
    path = "/" + "/".join(parsed[3:]) if len(parsed) > 3 else "/"
    
    print(f"[DEBUG] protocol={protocol}, host={host}, port={port}, path={path}")
    
    # 使用系统命令解析 DNS（兼容麒麟系统）
    try:
        result = subprocess.run(['getent', 'hosts', host], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            addr = result.stdout.strip().split()[0]
            print(f"[DEBUG] DNS 解析成功 (getent): {host} -> {addr}")
        else:
            # 备用：使用 host 命令
            result = subprocess.run(['host', host], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'has address' in result.stdout:
                addr = result.stdout.split('has address')[1].strip().split()[0]
                print(f"[DEBUG] DNS 解析成功 (host): {host} -> {addr}")
            else:
                print(f"[DEBUG] DNS 解析失败，直接使用域名")
                addr = host  # 直接使用域名，让系统解析
    except Exception as e:
        print(f"[DEBUG] DNS 解析异常: {e}，直接使用域名")
        addr = host
    
    # 使用原生 http.client 请求
    try:
        if protocol == "https":
            # 创建 SSL 上下文
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE  # 禁用证书验证
            
            conn = http.client.HTTPSConnection(host, port, timeout=20, context=context)
        else:
            conn = http.client.HTTPConnection(host, port, timeout=20)
        
        headers = {
            "Host": host,
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Client-Ip": ip,
            "X-Forwarded-For": ip,
        }
        
        print(f"[DEBUG] 发送请求...")
        conn.request("GET", path, headers=headers)
        response = conn.getresponse()
        
        print(f"[DEBUG] 响应状态: {response.status}")
        location = response.getheader("Location", "")
        print(f"[DEBUG] Location: {location}")
        
        conn.close()
        return location, response.status
        
    except Exception as e:
        print(f"[DEBUG] 请求错误: {type(e).__name__}: {e}")
        return "", str(e)[:100]


class BrowserLauncherApp:
    def __init__(self):
        self.root = None
        self.browsers = None
        
    def setup_ui(self):
        # 创建主窗口
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
        
        # 调试输出
        print(f"[DEBUG] URL: {url}")
        print(f"[DEBUG] IP: {ip}")
        print(f"[DEBUG] Browser: {browser_path}")
        print(f"[DEBUG] Platform: {sys.platform}")
        
        if not url:
            self.status_label.configure(text="请输入 URL", text_color="red")
            return
        
        if not ip:
            self.status_label.configure(text="请输入 IP", text_color="red")
            return
        
        self.status_label.configure(text="正在获取链接...", text_color="gray")
        self.root.update()
        
        print(f"[DEBUG] 正在请求 URL...")
        location, status = get_redirect_url(url, ip)
        print(f"[DEBUG] Location: {location}")
        print(f"[DEBUG] Status: {status}")
        
        if location:
            try:
                print(f"[DEBUG] 正在启动浏览器...")
                # 跨平台启动浏览器
                if sys.platform == 'win32':
                    subprocess.Popen([browser_path, location])
                elif sys.platform == 'darwin':
                    # macOS 使用 open 命令
                    subprocess.Popen(['open', '-a', browser_path, location])
                else:
                    # Linux 启动浏览器
                    print(f"[DEBUG] Linux: 执行 {browser_path} {location}")
                    try:
                        proc = subprocess.Popen(
                            [browser_path, location],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            start_new_session=True
                        )
                        print(f"[DEBUG] 浏览器进程 PID: {proc.pid}")
                    except Exception as ex:
                        print(f"[DEBUG] subprocess.Popen 失败: {ex}")
                        # 备用方案：使用 webbrowser 模块
                        import webbrowser
                        if not webbrowser.open(location):
                            raise Exception(f"无法打开浏览器: {ex}")
                self.status_label.configure(text=f"已在 {browser_name} 中打开", text_color="green")
                print(f"[DEBUG] 浏览器启动成功")
            except Exception as e:
                print(f"[DEBUG] 异常: {e}")
                self.status_label.configure(text=f"打开失败: {e}", text_color="red")
        else:
            self.status_label.configure(text=f"获取链接失败: {status}", text_color="red")
    
    def run(self):
        import time
        
        # 记录启动时间
        start_time = time.time()
        max_runtime = 24 * 60 * 60  # 24小时（秒）
        # 先验证（使用临时隐藏的根窗口）
        root = ctk.CTk()
        root.withdraw()  # 隐藏根窗口
        
        verify = VerifyDialog(root)
        if not verify.verified:
            root.destroy()
            return
        
        # 验证通过，销毁临时窗口，显示主窗口
        root.destroy()
        
        # 创建并显示主窗口
        self.setup_ui()
        
        # 设置定时检查，每分钟检查一次运行时间
        def check_timeout():
            if time.time() - start_time >= max_runtime:
                self.root.destroy()
                return
            self.root.after(60000, check_timeout)  # 60秒后再次检查
        
        self.root.after(60000, check_timeout)
        self.root.mainloop()


if __name__ == "__main__":
    app = BrowserLauncherApp()
    app.run()
