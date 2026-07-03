HTTP/1.1 200 OK
Cache-Control: no-cache, no-store, must-revalidate
Connection: keep-alive
Content-Type: application/javascript
Date: Mon, 11 May 2026 05:27:37 GMT
ETag: W/"68c81105-4605"
Expires: 0
Last-Modified: Mon, 15 Sep 2025 13:13:41 GMT
Pragma: no-cache
Vary: Accept-Encoding

$(function(){
    // if(sslClient) {
    //     clearCookies();
    // }
    //如果当前窗口不是最顶层的窗口
    if (window.top !== window.self){
        //那么就让最顶层的href 为当前页面的href
        window.top.location = window.self.location;
    }
});

// 操作认证方式tab
var loginModes = ['login-password','login-message','login-ukey','login-face'];
function loginModeChange(clickMode) {
    // 认证方式切换 显隐控制
    for (var i = 0; i <loginModes.length; i++) {
        var v = loginModes[i];
        $("."+v).removeClass("opp");
        $("#"+v).removeClass("on a-hover");
    }
    $("."+clickMode).addClass("opp");
    $("#"+clickMode).addClass("on a-hover");

    // 点击pki按钮时懒加载pnxclient.js,并且初始化pki控件
    if('login-ukey' === clickMode && !vctkInited){
        var script = document.createElement("script");
        script.type = "text/javascript";
        script.src = "themes/js/csg/pnxclient.js";
        document.body.appendChild(script);
        loadPlugShow();
        clearCookies();
    }

    // 切换到人脸认证时,加载人脸登录组件
    if ('login-face' === clickMode){
        displayFaceLogin();
    }

    // 根据当前登录采用的认证方式展示提示信息
    var theAuthMode = $("#theAuthMode").val();
    switch (theAuthMode) {
        case 'ACCOUNT_PASSWORD':
            $('#getSmsVerifyCodeMsg').hide();
            $('#getUkeyVerifyCodeMsg').hide();
            $('#getFaceVerifyCodeMsg').hide();
            $('#getQrcodeVerifyCodeMsg').hide();
            break;
        case 'SMS':
            $('#getApVerifyCodeMsg').hide();
            $('#getUkeyVerifyCodeMsg').hide();
            $('#getFaceVerifyCodeMsg').hide();
            $('#getQrcodeVerifyCodeMsg').hide();
            break;
        case 'UKEY':
            $('#getApVerifyCodeMsg').hide();
            $('#getSmsVerifyCodeMsg').hide();
            $('#getFaceVerifyCodeMsg').hide();
            $('#getQrcodeVerifyCodeMsg').hide();
            break;
        case 'FACE':
            $('#getApVerifyCodeMsg').hide();
            $('#getSmsVerifyCodeMsg').hide();
            $('#getUkeyVerifyCodeMsg').hide();
            $('#getQrcodeVerifyCodeMsg').hide();
            break;
        case 'QR_CODE':
            $('#getApVerifyCodeMsg').hide();
            $('#getSmsVerifyCodeMsg').hide();
            $('#getUkeyVerifyCodeMsg').hide();
            $('#getFaceVerifyCodeMsg').hide();
            break;
        default:
    }

}

// 二维码
var qrImg=document.querySelector('.login-qr');
var qr=document.querySelector('.qr');
var msg=document.querySelector('.msg');
var cup=document.querySelector('.login-cup');
if (qrImg != null){
    qrImg.onclick=(function(){
        $('#getQrcodeVerifyCodeMsg').html("");
        msg.style.display="none";
        qr.style.display="block";
        getQid();
    })
}

if (cup != null){
    cup.onclick=(function(){
        $('#getQrcodeVerifyCodeMsg').html("");
        var loginMode = $('#login-mode-a:first .fl.on.a-hover').attr('id');
        if(loginMode == "" || loginMode == null || loginMode==undefined){
            loginMode = "login-password";
        }
        loginModeChange(loginMode);
        msg.style.display="block";
        qr.style.display="none";
        QRCode.qid = "";
    })
}

// 注意以下兼容了各种前端页面逻辑
var eye=document.querySelector('.login-eyes');
if (eye != null){
    var flag = true;
    eye.onclick=function(){
        var placeholder = $('#user_pd').attr('placeholder')
        var val = $('#user_pd').val()
        if(flag){
            var url = $('.login-eyes').css('background-image').replace('eyes.png', 'eyeson.png');
            var appType = $('#app-type').val();
            if (appType == 'jg') {
                url = $('.login-eyes').css('background-image').replace('eyes.png','eyess.png');
            }
            $('.login-eyes').css('background-image', url);
            $('#pd').html('<input id="user_pd" type="text" maxlength="50" class="login-pwd" placeholder="'+placeholder+'" value="'+val+'" onkeydown="if(event.keyCode==13){submitApLogin()}">')
            // $(".login-pwd").get(0).setAttribute("type","text");
            flag=false;
        }else{
            var url = $('.login-eyes').css('background-image').replace('eyeson.png', 'eyes.png');
            var appType = $('#app-type').val();
            if (appType == 'jg') {
                url = $('.login-eyes').css('background-image').replace('eyess.png', 'eyes.png');
            }
            $('.login-eyes').css('background-image', url);
            $('#pd').html('<input id="user_pd" type="password" maxlength="50" class="login-pwd" placeholder="'+placeholder+'" value="'+val+'" onkeydown="if(event.keyCode==13){submitApLogin()}">')
            // $(".login-pwd").get(0).setAttribute("type","password");
            flag=true;
        }
    }
}
// 如果非军工认为是蒙西，则根据配置的内容调整样式
var appTypeVal = document.getElementById("app-type");
if (appTypeVal != null) {
    // if (appTypeVal.getAttribute("value") != 'jg') {
    //     var brower = getBrowser();
    //     if ("IE" == brower) {
    //         var ieurl = $('#main-css').attr('href').replace('login-mx', 'login-mx-ie');
    //         $('#main-css').attr("href", ieurl);
    //     }
    // }
}


// 图形验证码刷新
function refreshPicture() {
    $('#img_display_verify_code_pic').attr("src","getPictureCheckCodeImage?" + replayAttackParam());
}

var intervalDisable = function(id,time,htmltext){
    var si = time / 1000 ;
    var interID = window.setInterval(function(){
        si -- ;
        $('#'+id).html("重新获取("+si+")");
        $('#'+id).css({"cursor":"not-allowed"});
    },1000);
    var timeID = window.setTimeout(function(){
        clearInterval(interID);
        $('#'+id).removeAttr("disabled");
        $('#'+id).html(htmltext);
        $('#'+id).css({"cursor":"pointer"});
    },time);
}

//发送短信验证码
var sendPhoneCode=document.querySelector('#btn_send_phone_code');
if (sendPhoneCode != null){
    sendPhoneCode.onclick=function(){
        if($('#send_phone').length>0){
            var tagNumber = $('#send_phone').val();
            var tagName   = $('#send_phone').attr('placeholder').substring(5);
            if (tagNumber == null || tagNumber == '' || tagNumber == undefined || tagNumber == 'undefined' || tagNumber.trim() == '') {
                $('#getSmsVerifyCodeMsg').html(tagName+"不能为空");
                $('#getSmsVerifyCodeMsg').show();
                return;
            }
        }

        var appId = $('#smsAppId').val();
        if (appId == null || appId == '' || appId == undefined || appId == 'undefined' || appId.trim() == '') {
            $('#getSmsVerifyCodeMsg').html("系统标识不能为空");
            $('#getSmsVerifyCodeMsg').show();
            return;
        }
        var authMode = $('#smsAuthMode').val();
        if (authMode == null || authMode == '' || authMode == undefined || authMode == 'undefined' || authMode.trim() == '') {
            $('#getSmsVerifyCodeMsg').html("认证方式不能为空");
            $('#getSmsVerifyCodeMsg').show();
            return;
        }

        if($('#smsProvinceId').length>0){
            var provinceId = $('#smsProvinceId').val();
            if (provinceId == null || provinceId == '' || provinceId == undefined || provinceId == 'undefined' || provinceId.trim() == '') {
                var provinceName   = $('#smsProvinceId').find("option:selected").text().substring(5);
                $('#getSmsVerifyCodeMsg').html(provinceName+"不能为空");
                $('#getSmsVerifyCodeMsg').show();
                return;
            }
        }

        var tagNumberEncrypt = aostaritEncryptUtils.string.encrypt(tagNumber);
        $("#btn_send_phone_code").attr("disabled", true);
        $("#btn_send_phone_code").html("请稍后...");
        $.ajax({
            url: "sendPhoneVerifyCode?"+replayAttackParam(),
            dataType: "json",
            data: {tel: tagNumberEncrypt,appId:appId,authMode:authMode,provinceId:provinceId},
            success:function(result){
                if(result && result.success){
                    $('#getSmsVerifyCodeMsg').html("验证码已发送成功！");
                    $('#getSmsVerifyCodeMsg').show();
                    intervalDisable('btn_send_phone_code',60 * 1000,"获取验证码");
                }else{
                    $('#getSmsVerifyCodeMsg').html(result.message);
                    $('#getSmsVerifyCodeMsg').show();
                    intervalDisable('btn_send_phone_code',1 * 1000,"获取验证码");
                }
            },
            error : function(e){
                $('#getSmsVerifyCodeMsg').html("系统出错，请联系管理员");
                $("#btn_send_phone_code").removeAttr("disabled");
                $("#btn_send_phone_code").html("获取验证码");
            }
        });
    }
}

// 账号注册跳转
var accountRegister=document.querySelector('#account-register');
if (accountRegister != null){
    accountRegister.onclick=function(){
        window.location.href = $('#account-register-url').val();
    }
}
// 账号转正跳转
var accountToOfficial=document.querySelector('#account-to-official');
if (accountToOfficial != null){
    accountToOfficial.onclick=function(){
        window.location.href = $('#account-to-official-url').val();
    }
}
// 账号续期跳转
var accountRenewal=document.querySelector('#account-renewal');
if (accountRenewal != null){
    accountRenewal.onclick=function(){
        window.location.href = $('#account-renewal-url').val();
    }
}
// 账号启用跳转
var accountActivation=document.querySelector('#account-activation');
if (accountActivation != null){
    accountActivation.onclick=function(){
        window.location.href = $('#account-activation-url').val();
    }
}

// 忘记密码跳转
var forgetPwd=document.querySelector('#forget-pwd');
if (forgetPwd != null){
    forgetPwd.onclick=function(){
        var forgetPwdUrl = $('#forget-pwd-url').val();
        window.location.href=forgetPwdUrl;
    }
}

// 修改密码跳转
var modifyPwd=document.querySelector('#modify-pwd');
if (modifyPwd != null){
    modifyPwd.onclick=function(){
        var modifyPwdUrl = $('#modify-pwd-url').val();
        window.location.href=modifyPwdUrl;
    }
}

// PKI插件下载
var ukPlug=document.querySelector('#uk-plug');
if (ukPlug != null){
    ukPlug.onclick=function(){
        var ukPlugUrl = $('#uk-plug-url').val();
        window.location.href=ukPlugUrl;
    }
}

// chome浏览器下载
var browserChome=document.querySelector('#browser-chome');
if (browserChome != null){
    browserChome.onclick=function(){
        var browserChomeUrl = $('#browser-chome-url').val();
        window.location.href=browserChomeUrl;
    }
}

// ie浏览器下载
var browserIe=document.querySelector('#browser-ie');
if (browserIe != null){
    browserIe.onclick=function(){
        var browserIeUrl = $('#browser-ie-url').val();
        window.location.href=browserIeUrl;
    }
}


// 账号密码登录
var submitApLogin = function () {
    if (apLoginCheck()){
        //console.log('apLoginCheck-over')
        formSubmit("fm1");
        //console.log('formSubmit-over')
    }
}
// 账号密码登录-参数校验
function apLoginCheck() {
    $('#getApVerifyCodeMsg').hide();
    if($('#user_tag').length>0){
        var userTag = $('#user_tag').val();
        var tagName   = $('#user_tag').attr('placeholder').substring(5);
        if (userTag == null || userTag == '' || userTag == undefined || userTag == 'undefined' || userTag.trim() == '') {
            $('#getApVerifyCodeMsg').html(tagName+"不能为空");
            $('#getApVerifyCodeMsg').show();
            return false;
        }
        if (!checkLoginAccount(userTag)){
            $('#getApVerifyCodeMsg').html(tagName+checkFailMsg);
            $('#getApVerifyCodeMsg').show();
            return false;
        }
        $('#user_tag_encrypt').val(aostaritEncryptUtils.string.encrypt(userTag));
    }

    if($('#user_pd').length>0){
        var userPwd = $('#user_pd').val();
        var pwdName   = $('#user_pd').attr('placeholder').substring(5);
        if (userPwd == null || userPwd == '' || userPwd == undefined || userPwd == 'undefined' || userPwd.trim() == '') {
            $('#getApVerifyCodeMsg').html(pwdName+"不能为空");
            $('#getApVerifyCodeMsg').show();
            return false;
        }
        $('#user_pd_encrypt').val(aostaritEncryptUtils.string.encrypt(userPwd,true));
    }

    if($('#acProvinceId').length>0){
        var provinceId = $('#acProvinceId').val();
        if (provinceId == null || provinceId == '' || provinceId == undefined || provinceId == 'undefined' || provinceId.trim() == '') {
            var provinceName   = $('#acProvinceId').find("option:selected").text().substring(5);
            $('#getApVerifyCodeMsg').html(provinceName+"不能为空");
            $('#getApVerifyCodeMsg').show();
            return false;
        }
        $('#province_encrypt').val(aostaritEncryptUtils.string.encrypt(provinceId));
    }

    if($('#picture_code').length>0){
        var pictureCode = $('#picture_code').val();
        var picName   = $('#picture_code').attr('placeholder').substring(5);
        if (pictureCode == null || pictureCode == '' || pictureCode == undefined || pictureCode == 'undefined' || pictureCode.trim() == '') {
            $('#getApVerifyCodeMsg').html(picName+"不能为空");
            $('#getApVerifyCodeMsg').show();
            return false;
        }
        $('#captcha_encrypt').val(aostaritEncryptUtils.string.encrypt(pictureCode));
    }
    return true;
}

// 短信验证码登录
var submitSmsLogin = function () {
    $('#getSmsVerifyCodeMsg').hide();
    if($('#send_phone').length>0){
        var phoneNumber = $('#send_phone').val();
        var phoneName   = $('#send_phone').attr('placeholder').substring(5);
        if (phoneNumber == null || phoneNumber == '' || phoneNumber == undefined || phoneNumber == 'undefined' || phoneNumber.trim() == '') {
            $('#getSmsVerifyCodeMsg').html(phoneName+"不能为空");
            $('#getSmsVerifyCodeMsg').show();
            return;
        }
        if (!checkLoginAccount(phoneNumber)){
            $('#getSmsVerifyCodeMsg').html(phoneName+checkFailMsg);
            $('#getSmsVerifyCodeMsg').show();
            return;
        }

        $('#send_phone_encrypt').val(aostaritEncryptUtils.string.encrypt(phoneNumber));
    }

    if($('#smsProvinceId').length>0){
        var provinceId = $('#smsProvinceId').val();
        if (provinceId == null || provinceId == '' || provinceId == undefined || provinceId == 'undefined' || provinceId.trim() == '') {
            var provinceName   = $('#smsProvinceId').find("option:selected").text().substring(5);
            $('#getSmsVerifyCodeMsg').html(provinceName+"不能为空")
            $('#getSmsVerifyCodeMsg').show();
            return;
        }
        $('#sms_province_encrypt').val(aostaritEncryptUtils.string.encrypt(provinceId));
    }

    if($('#send_phone_code').length>0){
        var phoneCode = $('#send_phone_code').val();
        var codeName  = $('#send_phone_code').attr('placeholder').substring(5);
        if (phoneCode == null || phoneCode == '' || phoneCode == undefined || phoneCode == 'undefined' || phoneCode.trim() == '') {
            $('#getSmsVerifyCodeMsg').html(codeName+"不能为空");
            $('#getSmsVerifyCodeMsg').show();
            return;
        }
        $('#sms_captcha_encrypt').val(aostaritEncryptUtils.string.encrypt(phoneCode));
    }
    formSubmit("fm2");
}

function replayAttackParam() {
    var requestTime = new Date().getTime();
    var nonce = getUID();
    var sign = aostaritEncryptUtils.string.sign(requestTime + "," + nonce);
    var resStr = "requestTime=" + requestTime + "&nonce=" + nonce + "&sign=" + sign;
    return resStr;
}

function formSubmit(formId) {
    var requestTime = new Date().getTime();
    var nonce = getUID();
    $("#"+formId).append('<input type="hidden" name="requestTime" value="' + requestTime + '" />');
    $("#"+formId).append('<input type="hidden" name="nonce" value="' + nonce + '" />');
    $("#"+formId).append('<input type="hidden" name="sign" value="' + aostaritEncryptUtils.string.sign(requestTime + "," + nonce) + '" />');
    preventMissUrlParams();

    var isPreLoginCheck = $('#isPreLoginCheck').val();
    if ("true" == isPreLoginCheck){
        preLoginCheck(formId);
    }else {
        document.getElementById(formId).submit();
    }

}

function getUID () { // 获取唯一值
    return 'xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}

//防止表单提交参数丢失
var preventMissUrlParams = function () {
    var location = self.document.location;
    var hash = decodeURIComponent(location.hash);
    if (hash != undefined && hash != '' && hash.indexOf('#') === -1) {
        hash = '#' + hash;
    }
    $("form").each(function(){
        var action = $(this).attr("action")
        if (action == undefined) {
            action = location.href;
        } else {
            var containIndex = location.href.indexOf('?');
            if (containIndex != -1) {
                var queryParam = location.href.substring(containIndex);
                action += queryParam;
            }
        }
        action += hash;
        $(this).attr('action', action);
    })
}

var checkFailMsg = '格式只能包含中文、字母、数字、_-@.*·特殊字符!';

var  checkLoginAccount = function(str){
    if (/^$|^[\u4e00-\u9fa5a-zA-Z0-9_\-\*.\@·]*$/.test(str)){
        return true;
    }
    return false;
}




