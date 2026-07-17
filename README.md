# 国网管理工具 (SGCC Management Tool)

一个基于 Wails 框架开发的跨平台浏览器启动器，用于国网系统账号管理。

## 功能特性

- 浏览器检测与管理（支持 Chrome、Edge、Firefox、360、搜狗等主流浏览器）
- 账号验证与登录
- 验证码二维码显示
- 跨平台支持（Windows、Linux、macOS）
- 深色主题界面

## 技术栈

- **后端**: Go (Wails v2)
- **前端**: HTML + CSS + JavaScript (Vanilla)
- **GUI**: WebView (系统原生)

## 环境要求

- Go 1.18+
- Node.js 16+ (仅开发时需要)
- Wails CLI (`go install github.com/wailsapp/wails/v2/cmd/wails@latest`)

## 开发

```bash
# 安装依赖
cd frontend
npm install

# 开发模式运行
wails dev
```

## 构建

```bash
# 构建生产版本
wails build
```

构建完成后，可执行文件位于 `build/bin/` 目录。

## 项目结构

```
.
├── app.go                 # Wails 应用主逻辑
├── main.go               # 程序入口
├── internal/
│   ├── browser/          # 浏览器检测模块
│   ├── network/          # 网络模块
│   └── verify/           # 验证模块
├── frontend/             # 前端代码
│   ├── index.html
│   └── src/
│       ├── main.js
│       └── style.css
└── wails.json           # Wails 配置
```

## 支持的浏览器

### Windows
- Google Chrome
- Microsoft Edge
- Mozilla Firefox
- 360 安全/极速浏览器
- 搜狗浏览器
- QQ 浏览器
- 遨游浏览器

### Linux
- Google Chrome
- Mozilla Firefox
- Chromium
- 麒麟浏览器
- 优麒麟浏览器

### macOS
- Google Chrome
- Safari
- Mozilla Firefox

## License

MIT
