package main

import (
	"context"
	"fmt"
	"time"
	"browser-launcher/internal/browser"
	"browser-launcher/internal/network"
	"browser-launcher/internal/verify"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// App application struct
type App struct {
	ctx        context.Context
	randomCode string
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{}
}

// startup is called when the app starts
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	
	// 启动 24 小时自动关闭定时器
	go a.autoCloseTimer()
}

// autoCloseTimer 24 小时自动关闭定时器
func (a *App) autoCloseTimer() {
	// TODO: 测试时使用 1 分钟，正式环境改为 24 * time.Hour
	//time.Sleep(1 * time.Minute)
	time.Sleep(24 * time.Hour)
	runtime.Quit(a.ctx)
}

// GetRandomCode 获取随机码
func (a *App) GetRandomCode() string {
	a.randomCode = verify.GenerateRandomCode()
	return a.randomCode
}

// VerifyCode 验证验证码
func (a *App) VerifyCode(code string) map[string]interface{} {
	if code == "" {
		return map[string]interface{}{
			"success": false,
			"message": "请输入验证码",
		}
	}

	correctCode := verify.CalculatePassword(a.randomCode)
	if code == correctCode {
		return map[string]interface{}{
			"success": true,
			"message": "验证成功",
		}
	}
	return map[string]interface{}{
		"success": false,
		"message": "验证码错误",
	}
}

// GetBrowsers 获取浏览器列表
func (a *App) GetBrowsers() []map[string]string {
	browsers := browser.Detect()
	result := make([]map[string]string, len(browsers))
	for i, b := range browsers {
		result[i] = map[string]string{
			"name": b.Name,
			"path": b.Path,
			"icon": browser.GetIconName(b.Name),
		}
	}
	return result
}

// OpenBrowser 打开浏览器
func (a *App) OpenBrowser(browserIndex int, url, ip string) map[string]interface{} {
	browsers := browser.Detect()
	
	if browserIndex < 0 || browserIndex >= len(browsers) {
		return map[string]interface{}{
			"success": false,
			"message": "浏览器选择无效",
		}
	}

	if url == "" {
		return map[string]interface{}{
			"success": false,
			"message": "请输入 URL",
		}
	}

	if ip == "" {
		return map[string]interface{}{
			"success": false,
			"message": "请输入 IP",
		}
	}

	// 获取重定向链接
	result := network.GetRedirectURL(url, ip)
	if result.Error != "" {
		return map[string]interface{}{
			"success": false,
			"message": "获取链接失败: " + result.Error,
		}
	}

	if result.Location == "" {
		return map[string]interface{}{
			"success": false,
			"message": fmt.Sprintf("未获取到重定向链接 (状态码: %d)", result.StatusCode),
		}
	}

	// 打开浏览器
	b := browsers[browserIndex]
	if err := browser.OpenWithURL(b, result.Location); err != nil {
		return map[string]interface{}{
			"success": false,
			"message": "打开失败: " + err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"message": fmt.Sprintf("已在 %s 中打开", b.Name),
	}
}

// WindowMinimise 最小化窗口
func (a *App) WindowMinimise() {
	runtime.WindowMinimise(a.ctx)
}

// WindowMaximise 最大化窗口
func (a *App) WindowMaximise() {
	runtime.WindowMaximise(a.ctx)
}

// WindowToggleMaximise 切换最大化状态
func (a *App) WindowToggleMaximise() {
	runtime.WindowToggleMaximise(a.ctx)
}

// WindowClose 关闭窗口
func (a *App) WindowClose() {
	runtime.Quit(a.ctx)
}
