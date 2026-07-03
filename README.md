# sgcc-management

账号管理工具

## 功能

- 多平台账号管理客户端
- 支持多种认证方式（密码/短信/UKey/人脸/二维码）
- 浏览器启动器

## 下载

从 [Releases](../../releases) 页面下载对应平台的可执行文件：

| 平台 | 文件 |
|------|------|
| Windows | `BrowserLauncher-Windows.exe` |
| Linux | `BrowserLauncher-Linux` |
| macOS | `BrowserLauncher-macOS` |

所有版本均为独立可执行文件，**无需安装任何依赖**，直接运行即可。

## 本地构建

### 前置要求

- Python 3.8+
- pip

### Windows

```bash
pip install -r requirements.txt
python build.py
```

### Linux

```bash
pip install -r requirements.txt
chmod +x build.sh
./build.sh
```

### macOS

```bash
pip install -r requirements.txt
python3 build.py
```

## GitHub 自动构建

项目使用 GitHub Actions 自动构建：

1. 创建 tag 触发构建：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. 自动构建 Windows/Linux/macOS 三个平台

3. 自动发布到 Releases 页面

也可以在 Actions 页面手动触发构建。

## 支持的浏览器

| 浏览器 | Windows | Linux | macOS |
|--------|---------|-------|-------|
| Google Chrome | ✅ | ✅ | ✅ |
| Mozilla Firefox | ✅ | ✅ | ✅ |
| Microsoft Edge | ✅ | ✅ | ✅ |
| Chromium | ✅ | ✅ | ✅ |
| Brave | ✅ | ✅ | ✅ |
| Vivaldi | ✅ | ✅ | ✅ |
| Opera | ✅ | ✅ | ✅ |
| Safari | - | - | ✅ |

## 项目结构

```
sgcc-management/
├── browser_launcher.py       # 主程序
├── login.js                  # 登录页面逻辑
├── aostaritEncrypt.js        # 国密加密 (SM2/SM3)
├── accounts.json             # 账号数据
├── build.py                  # 构建脚本
├── build.bat                 # Windows 构建批处理
├── build.sh                  # Linux/macOS 构建脚本
├── requirements.txt          # Python 依赖
├── .github/workflows/build.yml  # GitHub Actions 构建配置
└── dist/                     # 构建产物
```
