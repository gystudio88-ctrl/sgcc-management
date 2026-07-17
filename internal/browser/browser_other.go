//go:build !windows

package browser

// detectWindows 非 Windows 系统返回空
func detectWindows() []Browser {
	return nil
}
