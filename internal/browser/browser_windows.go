//go:build windows

package browser

import (
	"os"
	"os/exec"
	"strings"
)

// detectWindows Windows 系统浏览器检测
func detectWindows() []Browser {
	browsers := make(map[string]string)

	// 使用 reg query 命令从注册表检测浏览器
	// 检查 HKLM 和 HKCU 的 StartMenuInternet
	detectFromRegistry("HKLM", &browsers)
	detectFromRegistry("HKCU", &browsers)

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

// detectFromRegistry 从注册表检测浏览器
func detectFromRegistry(hive string, browsers *map[string]string) {
	// 使用 reg query 命令查询注册表
	cmd := exec.Command("reg", "query", hive+`\SOFTWARE\Clients\StartMenuInternet`, "/s")
	output, err := cmd.Output()
	if err != nil {
		return
	}

	lines := strings.Split(string(output), "\n")
	var currentName string
	var currentPath string

	for _, line := range lines {
		line = strings.TrimSpace(line)
		
		// 检测浏览器名称 (注册表键名的默认值)
		if strings.HasPrefix(line, hive) {
			// 新的浏览器条目开始
			if currentName != "" && currentPath != "" {
				if _, exists := (*browsers)[currentName]; !exists {
					(*browsers)[currentName] = currentPath
				}
			}
			currentName = ""
			currentPath = ""
			
			// 提取键名作为默认名称
			parts := strings.Split(line, `\`)
			if len(parts) > 0 {
				lastPart := parts[len(parts)-1]
				if lastPart != "StartMenuInternet" {
					currentName = lastPart
				}
			}
		}

		// 检测命令路径
		if strings.Contains(line, "shell\\open\\command") {
			// 下一行应该是命令值
			continue
		}

		// 提取命令值
		if strings.HasPrefix(line, "(Default)") || strings.HasPrefix(line, "") && strings.Contains(line, "REG_SZ") {
			parts := strings.SplitN(line, "REG_SZ", 2)
			if len(parts) == 2 {
				cmd := strings.TrimSpace(parts[1])
				path := extractExePath(cmd)
				if path != "" && fileExists(path) {
					currentPath = path
				}
			}
		}
	}

	// 处理最后一个条目
	if currentName != "" && currentPath != "" {
		if _, exists := (*browsers)[currentName]; !exists {
			(*browsers)[currentName] = currentPath
		}
	}
}

// extractExePath 从命令字符串中提取 exe 路径
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
