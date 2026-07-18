package network

import (
	"context"
	"crypto/tls"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

// RedirectResult 重定向结果
type RedirectResult struct {
	Location   string
	StatusCode int
	Error      string
}

// 初始化日志
var logger = log.New(os.Stdout, "[NETWORK] ", log.LstdFlags|log.Lshortfile)

// GetRedirectURL 获取重定向链接
func GetRedirectURL(url, ip string) RedirectResult {
	// 确保 URL 有协议
	if !strings.HasPrefix(url, "http://") && !strings.HasPrefix(url, "https://") {
		url = "https://" + url
	}

	// 解析 host
	host := ""
	if parts := strings.Split(url, "/"); len(parts) >= 3 {
		host = parts[2]
	}

	logger.Printf("开始请求: URL=%s, IP=%s, Host=%s", url, ip, host)

	// 创建自定义 Transport
	transport := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
		},
		DisableKeepAlives: true,
	}

	// 创建客户端，不自动跟随重定向
	client := &http.Client{
		Timeout:   25 * time.Second,
		Transport: transport,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse // 不跟随重定向
		},
	}

	// 创建请求
	ctx, cancel := context.WithTimeout(context.Background(), 25*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		logger.Printf("创建请求失败: %v", err)
		return RedirectResult{Error: fmt.Sprintf("创建请求失败: %v", err)}
	}

	// 设置请求头
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
	req.Header.Set("Connection", "keep-alive")
	req.Header.Set("Host", host)
	req.Header.Set("Client-Ip", ip)
	req.Header.Set("X-Forwarded-For", ip)
	req.Header.Set("Remote_Addr", ip)

	logger.Printf("请求头: Host=%s, Client-Ip=%s, X-Forwarded-For=%s", host, ip, ip)

	// 发送请求
	resp, err := client.Do(req)
	if err != nil {
		logger.Printf("请求失败: %v", err)
		return RedirectResult{Error: fmt.Sprintf("请求失败: %v", err)}
	}
	defer resp.Body.Close()

	// 获取重定向地址
	location := resp.Header.Get("Location")
	statusCode := resp.StatusCode

	logger.Printf("响应状态码: %d, Location: %s", statusCode, location)

	return RedirectResult{
		Location:   location,
		StatusCode: statusCode,
	}
}

// IsRedirect 检查是否为重定向状态码
func IsRedirect(statusCode int) bool {
	return statusCode == 301 || statusCode == 302 || statusCode == 303 || statusCode == 307 || statusCode == 308
}
