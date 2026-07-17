package verify

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"hash/fnv"
	"math/rand"
	"net"
	"os"
	"runtime"
	"strings"
	"time"
)

// AppConfig 软件配置
type AppConfig struct {
	Salt      string
	Algorithm string
}

// 软件配置映射
var appConfigs = map[string]AppConfig{
	"88": {
		Salt:      "browser_launcher_2024",
		Algorithm: "sha256_digits",
	},
}

// CalculatePassword 根据随机码计算验证码
func CalculatePassword(randomCode string) string {
	// 提取软件标识（前两位）
	appID := "88"
	if len(randomCode) >= 2 {
		appID = randomCode[:2]
	}

	// 提取实际随机码（去掉前两位）
	actualCode := randomCode
	if len(randomCode) > 2 {
		actualCode = randomCode[2:]
	}

	// 获取配置
	config, ok := appConfigs[appID]
	if !ok {
		config = AppConfig{Salt: "default_salt", Algorithm: "sha256_digits"}
	}

	// 加盐后计算
	combined := actualCode + config.Salt
	hash := sha256.Sum256([]byte(combined))
	hashStr := hex.EncodeToString(hash[:])

	// 提取数字，组成8位验证码
	code := ""
	for _, char := range hashStr {
		if len(code) >= 8 {
			break
		}
		if char >= '0' && char <= '9' {
			code += string(char)
		}
	}

	// 补齐8位
	for len(code) < 8 {
		code += "0"
	}

	return code
}

// GetDeviceInfo 获取设备信息
func GetDeviceInfo() string {
	// 获取 MAC 地址
	var macAddr string
	interfaces, err := net.Interfaces()
	if err == nil {
		for _, iface := range interfaces {
			if len(iface.HardwareAddr) > 0 && iface.Flags&net.FlagUp != 0 {
				macAddr = iface.HardwareAddr.String()
				break
			}
		}
	}

	// 获取机器名
	hostname, _ := os.Hostname()

	// 获取系统信息
	system := runtime.GOOS

	return fmt.Sprintf("%s-%s-%s", macAddr, hostname, system)
}

// GenerateRandomCode 根据设备信息和随机数生成16位随机码
func GenerateRandomCode() string {
	rand.Seed(time.Now().UnixNano())

	// 设备信息 + 随机数
	deviceInfo := GetDeviceInfo()
	randomPart := rand.Int63()

	// 组合并计算哈希
	combined := fmt.Sprintf("%s-%d-%d", deviceInfo, randomPart, time.Now().UnixNano())
	hash := sha256.Sum256([]byte(combined))
	hashStr := hex.EncodeToString(hash[:])

	// 转换为大写字母和数字
	code := ""
	for _, char := range hashStr {
		if len(code) >= 14 {
			break
		}
		if (char >= '0' && char <= '9') || (char >= 'a' && char <= 'z') {
			if char >= 'a' && char <= 'z' {
				code += strings.ToUpper(string(char))
			} else {
				code += string(char)
			}
		}
	}

	// 补齐14位
	for len(code) < 14 {
		chars := "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
		code += string(chars[rand.Intn(len(chars))])
	}

	return "88" + code[:14]
}

// HashString 计算字符串哈希值（用于设备指纹）
func HashString(s string) uint32 {
	h := fnv.New32a()
	h.Write([]byte(s))
	return h.Sum32()
}
