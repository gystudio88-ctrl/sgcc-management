import './style.css';
import QRCode from 'qrcode';
import { GetRandomCode, VerifyCode, GetBrowsers, OpenBrowser, WindowMinimise, WindowToggleMaximise, WindowClose } from '../wailsjs/go/main/App';

let browsers = [];

// 窗口控制函数
window.maximizeApp = function() {
    WindowToggleMaximise();
};

window.minimizeApp = function() {
    WindowMinimise();
};

window.closeApp = function() {
    WindowClose();
};

// 初始化
async function init() {
    try {
        // 获取随机码
        const randomCode = await GetRandomCode();
        document.getElementById('random-code').textContent = '随机码: ' + randomCode;
        
        // 生成二维码 - 使用本地库
        const canvas = document.getElementById('qrcode');
        await QRCode.toCanvas(canvas, randomCode, {
            width: 180,
            margin: 1,
            color: { dark: '#000000', light: '#ffffff' }
        });
        
        console.log('QR Code generated successfully');
    } catch (err) {
        console.error('Failed to generate QR code:', err);
        document.getElementById('random-code').textContent = '二维码生成失败: ' + err.message;
    }
}

// 验证
window.doVerify = async function() {
    const input = document.getElementById('verify-input').value;
    const errorEl = document.getElementById('verify-error');
    
    if (!input) {
        errorEl.textContent = '请输入验证码';
        return;
    }
    
    try {
        const result = await VerifyCode(input);
        if (result.success) {
            document.getElementById('verify-page').classList.add('hidden');
            document.getElementById('main-page').classList.remove('hidden');
            document.getElementById('titlebar-text').textContent = '浏览器启动器';
            loadBrowsers();
        } else {
            errorEl.textContent = result.message;
        }
    } catch (err) {
        errorEl.textContent = '验证失败';
        console.error(err);
    }
};

// 加载浏览器列表
async function loadBrowsers() {
    try {
        browsers = await GetBrowsers();
        const listEl = document.getElementById('browser-list');
        const statusEl = document.getElementById('status-bar');
        
        if (!browsers || browsers.length === 0) {
            listEl.innerHTML = '<div class="browser-item"><span class="browser-name">未检测到浏览器</span></div>';
            return;
        }
        
        statusEl.textContent = '已检测到 ' + browsers.length + ' 个浏览器';
        
        listEl.innerHTML = browsers.map((b, i) => 
            '<div class="browser-item" onclick="openBrowserAt(' + i + ')">' +
            '<span class="browser-icon">' + b.icon + '</span>' +
            '<span class="browser-name">' + b.name + '</span>' +
            '</div>'
        ).join('');
    } catch (err) {
        console.error(err);
    }
}

// 打开浏览器
window.openBrowserAt = async function(index) {
    const url = document.getElementById('url-input').value;
    const ip = document.getElementById('ip-input').value;
    const statusEl = document.getElementById('status-bar');
    
    statusEl.className = 'status-bar';
    statusEl.textContent = '正在获取链接...';
    
    try {
        const result = await OpenBrowser(index, url, ip);
        
        if (result.success) {
            statusEl.className = 'status-bar success';
        } else {
            statusEl.className = 'status-bar error';
        }
        statusEl.textContent = result.message;
    } catch (err) {
        statusEl.className = 'status-bar error';
        statusEl.textContent = '操作失败';
        console.error(err);
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', init);
