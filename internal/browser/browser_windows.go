//go:build windows

package browser

import (
	"os"
	"os/exec"
	"strings"

	"golang.org/x/sys/windows/registry"
)

// detectWindows Windows 系统浏览器检测 - 使用注册表
func detectWindows() []Browser {
	browsers := make(map[string]string)

	// 从注册表检测浏览器
	regPaths := []registry.Key{
		registry.LOCAL_MACHINE,
		registry.CURRENT_USER,
	}

	for _, hkey := range regPaths {
		key, err := registry.OpenKey(hkey, `SOFTWARE\Clients\StartMenuInternet`, registry.READ)
		if err != nil {
			continue
		}

		subkeys, err := key.ReadSubKeyNames(-1)
		if err != nil {
			key.Close()
			continue
		}

		for _, subkeyName := range subkeys {
			subkey, err := registry.OpenKey(key, subkeyName, registry.READ)
			if err != nil {
				continue
			}

			// 获取浏览器名称
			name, _, err := subkey.GetStringValue("")
			if err != nil {
				name = subkeyName
			}

			// 获取可执行文件路径
			cmdKey, err := registry.OpenKey(subkey, `shell\open\command`, registry.READ)
			if err == nil {
				cmd, _, err := cmdKey.GetStringValue("")
				if err == nil {
					path := extractExePath(cmd)
					if path != "" && fileExists(path) {
						if _, exists := browsers[name]; !exists {
							browsers[name] = path
						}
					}
				}
				cmdKey.Close()
			}
			subkey.Close()
		}
		key.Close()
	}

	// 补充常见浏览器路径
	commonPaths := map[string][]string{
		"Google Chrome": {
			os.Getenv("ProgramFiles") + `\Google\Chrome\Application\chrome.exe`,
			os.Getenv("ProgramFiles(x86)") + `\Google\Chrome\Application\chrome.exe`,
			os.Getenv("LocalAppData") + `\Google\Chrome\Application\chrome.exe`,
		},
		"Microsoft Edge": {
			os.Getenv("ProgramFiles(x86)") + `\Microsoft\Edge\Application\msedge.exe`,
			os.Getenv("ProgramFiles") + `\Microsoft\Edge\Application\msedge.exe`,
		},
		"Mozilla Firefox": {
			os.Getenv("ProgramFiles") + `\Mozilla Firefox\firefox.exe`,
			os.Getenv("ProgramFiles(x86)") + `\Mozilla Firefox\firefox.exe`,
		},
		"Brave": {
			os.Getenv("LocalAppData") + `\BraveSoftware\Brave-Browser\Application\brave.exe`,
		},
		"Opera": {
			os.Getenv("LocalAppData") + `\Programs\Opera\launcher.exe`,
			os.Getenv("LocalAppData") + `\Programs\Opera\opera.exe`,
		},
		"Vivaldi": {
			os.Getenv("LocalAppData") + `\Vivaldi\Application\vivaldi.exe`,
		},
		"360 Browser": {
			os.Getenv("LocalAppData") + `\360Chrome\Chrome\Application\360chrome.exe`,
		},
		"QQ Browser": {
			os.Getenv("ProgramFiles") + `\QQBrowser\QQBrowser.exe`,
			os.Getenv("ProgramFiles(x86)") + `\QQBrowser\QQBrowser.exe`,
		},
		"Sogou Explorer": {
			os.Getenv("ProgramFiles") + `\SogouExplorer\SogouExplorer.exe`,
			os.Getenv("ProgramFiles(x86)") + `\SogouExplorer\SogouExplorer.exe`,
		},
	}

	for name, paths := range commonPaths {
		if _, exists := browsers[name]; !exists {
			for _, path := range paths {
				if fileExists(path) {
					browsers[name] = path
					break
				}
			}
		}
	}

	// 转换为切片
	var result []Browser
	for name, path := range browsers {
		result = append(result, Browser{Name: name, Path: path})
	}

	return result
}

// extractExePath 从注册表命令字符串中提取 exe 路径
func extractExePath(cmd string) string {
	cmd = strings.TrimSpace(cmd)
	if cmd == "" {
		return ""
	}

	// 处理带引号的路径
	if strings.HasPrefix(cmd, `"`) {
		end := strings.Index(cmd[1:], `"`)
		if end > 0 {
			return cmd[1 : end+1]
		}
	}

	// 处理不带引号的路径
	parts := strings.Fields(cmd)
	if len(parts) > 0 {
		path := parts[0]
		// 如果路径包含空格，尝试找到 .exe
		if !strings.HasSuffix(strings.ToLower(path), ".exe") {
			for i := 1; i < len(parts); i++ {
				path += " " + parts[i]
				if strings.HasSuffix(strings.ToLower(path), ".exe") {
					break
				}
			}
		}
		return path
	}

	return ""
}
