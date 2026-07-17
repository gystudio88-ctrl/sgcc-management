package browser

import (
	"os"
	"os/exec"
	"runtime"
	"strings"
)

// Browser 浏览器信息
type Browser struct {
	Name string
	Path string
}

// Detect 检测系统已安装的浏览器
func Detect() []Browser {
	switch runtime.GOOS {
	case "windows":
		return detectWindows()
	case "darwin":
		return detectMacOS()
	case "linux":
		return detectLinux()
	default:
		return nil
	}
}

// fileExists 检查文件是否存在
func fileExists(path string) bool {
	if path == "" {
		return false
	}
	_, err := os.Stat(path)
	return err == nil
}

// detectMacOS macOS 系统浏览器检测
func detectMacOS() []Browser {
	var browsers []Browser

	paths := map[string]string{
		"Safari":          "/Applications/Safari.app/Contents/MacOS/Safari",
		"Google Chrome":   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
		"Mozilla Firefox": "/Applications/Firefox.app/Contents/MacOS/firefox",
		"Microsoft Edge":  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
		"Brave":           "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
		"Opera":           "/Applications/Opera.app/Contents/MacOS/Opera",
		"Vivaldi":         "/Applications/Vivaldi.app/Contents/MacOS/Vivaldi",
	}

	for name, path := range paths {
		if _, err := os.Stat(path); err == nil {
			browsers = append(browsers, Browser{Name: name, Path: path})
		}
	}

	return browsers
}

// detectLinux Linux 系统浏览器检测
func detectLinux() []Browser {
	var browsers []Browser
	seen := make(map[string]bool)

	// 浏览器命令名映射
	commands := []struct {
		name string
		cmds []string
	}{
		// 主流浏览器
		{"Google Chrome", []string{"google-chrome", "google-chrome-stable", "google-chrome-beta"}},
		{"Mozilla Firefox", []string{"firefox", "firefox-esr"}},
		{"Microsoft Edge", []string{"microsoft-edge", "microsoft-edge-stable", "microsoft-edge-beta"}},
		{"Chromium", []string{"chromium", "chromium-browser", "chromium-bin"}},
		{"Brave", []string{"brave", "brave-browser"}},
		{"Vivaldi", []string{"vivaldi", "vivaldi-stable"}},
		{"Opera", []string{"opera", "opera-stable"}},
		// 麒麟系统浏览器
		{"麒麟浏览器", []string{"kylin-browser", "kybrowser", "kylin-browser-stable"}},
		{"优麒麟浏览器", []string{"ubuntukylin-browser"}},
		// 国产浏览器
		{"360 Browser", []string{"360browser", "360-browser"}},
		{"搜狗浏览器", []string{"sogou-browser", "sogou-explorer"}},
		// 其他常见浏览器
		{"Epiphany", []string{"epiphany", "gnome-browser"}},
		{"Konqueror", []string{"konqueror"}},
		{"Midori", []string{"midori"}},
		{"Tor Browser", []string{"tor-browser", "torbrowser-launcher"}},
	}

	for _, b := range commands {
		for _, cmd := range b.cmds {
			if path, err := exec.LookPath(cmd); err == nil {
				if !seen[b.name] {
					browsers = append(browsers, Browser{Name: b.name, Path: path})
					seen[b.name] = true
				}
				break
			}
		}
	}

	// 额外检查常见安装路径
	commonPaths := map[string]string{
		// 主流浏览器
		"Google Chrome":  "/opt/google/chrome/google-chrome",
		"Microsoft Edge": "/opt/microsoft/msedge/msedge",
		"Brave":          "/opt/brave.com/brave/brave",
		"Vivaldi":        "/opt/vivaldi/vivaldi",
		"Opera":          "/usr/lib/x86_64-linux-gnu/opera/opera",
		// 麒麟系统浏览器路径
		"麒麟浏览器":   "/opt/kylin/browser/kylin-browser",
		"优麒麟浏览器": "/opt/ubuntukylin/browser/ubuntukylin-browser",
		// 国产浏览器
		"360 Browser": "/opt/360browser/360browser",
		"搜狗浏览器":  "/opt/sogou-browser/sogou-browser",
	}

	for name, path := range commonPaths {
		if !seen[name] {
			if _, err := os.Stat(path); err == nil {
				browsers = append(browsers, Browser{Name: name, Path: path})
				seen[name] = true
			}
		}
	}

	// 使用 xdg-settings 获取默认浏览器作为后备
	if len(browsers) == 0 {
		if path, err := exec.LookPath("xdg-settings"); err == nil {
			out, err := exec.Command(path, "get", "default-web-browser").Output()
			if err == nil {
				defaultBrowser := strings.TrimSpace(string(out))
				if defaultBrowser != "" {
					// 尝试找到对应的可执行文件
					browserCmd := strings.TrimSuffix(defaultBrowser, ".desktop")
					if execPath, err := exec.LookPath(browserCmd); err == nil {
						browsers = append(browsers, Browser{
							Name: "默认浏览器 (" + defaultBrowser + ")",
							Path: execPath,
						})
					}
				}
			}
		}
	}

	return browsers
}

// OpenWithURL 用指定浏览器打开 URL
func OpenWithURL(b Browser, url string) error {
	switch runtime.GOOS {
	case "windows":
		return exec.Command(b.Path, url).Start()
	case "darwin":
		return exec.Command("open", "-a", b.Path, url).Start()
	default:
		cmd := exec.Command(b.Path, url)
		return cmd.Start()
	}
}

// GetIconName 获取浏览器图标名称
func GetIconName(name string) string {
	name = strings.ToLower(name)
	switch {
	case strings.Contains(name, "chrome") && !strings.Contains(name, "360") && !strings.Contains(name, "qq"):
		return "🌐"
	case strings.Contains(name, "edge"):
		return "🔷"
	case strings.Contains(name, "firefox"):
		return "🦊"
	case strings.Contains(name, "brave"):
		return "🦁"
	case strings.Contains(name, "opera"):
		return "⭕"
	case strings.Contains(name, "safari"):
		return "🧭"
	case strings.Contains(name, "vivaldi"):
		return "🔴"
	case strings.Contains(name, "360"):
		return "🟢"
	case strings.Contains(name, "qq"):
		return "🔵"
	case strings.Contains(name, "sogou"):
		return "🔷"
	default:
		return "🌐"
	}
}

// GetCleanName 获取简化的浏览器名称
func GetCleanName(name string) string {
	// 移除常见后缀
	name = strings.TrimSuffix(name, " Browser")
	name = strings.TrimSuffix(name, " Web Browser")
	return name
}
