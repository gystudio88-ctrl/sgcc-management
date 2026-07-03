HTTP/1.1 200 OK
Cache-Control: no-cache, no-store, must-revalidate
Connection: keep-alive
Content-Type: application/javascript
Date: Mon, 11 May 2026 05:27:37 GMT
ETag: W/"68c81105-886"
Expires: 0
Last-Modified: Mon, 15 Sep 2025 13:13:41 GMT
Pragma: no-cache
Vary: Accept-Encoding

/***
 * 加解密工具
 */
$(function(){
});

var encryptOptions = function (){
    return {
        options:{
            encryptKey:"",
            smPass:"",
            isIE8:false
        },
        setOptions : function (op){
            $.extend(encryptOptions.options, op);
        }
    }
}();

var aostaritEncryptUtils  = function (){
    return {
        init : function (options){
            if(options){
                encryptOptions.setOptions(options);
                //console.log(encryptOptions);
            }
        },
        string : {
            encrypt : function (str,force){
                var smPass = encryptOptions.options.smPass;
                if (smPass == "true" || smPass === true || force){
                    var encryptKey = encryptOptions.options.encryptKey;
                    if(!encryptKey || encryptKey == "" || encryptKey == null || encryptKey == undefined || encryptKey == "undefined"){
                        return  str ;
                    }
                    var encryptStr;
                    var random=getRandomString(8);
                    var isIE8 = encryptOptions.options.isIE8;
                    if (isIE8){
                        var keys = encryptKey.split("#");
                        //获取key秘钥
                        var key = RSAUtils.getKeyPair(keys[1], '', keys[0]);
                        //对密码进行md5信息摘要
                        var envilope=$.md5(str)+random+str;
                        //进行完整的信息连接，生成数字签名元数据
                        encryptStr = RSAUtils.encryptedString(key, envilope);
                    }else {
                        var sm3enc =  do_sm3_encrypt(str)+random+str ;
                        encryptStr = do_sm2_encrypt(sm3enc,encryptKey) ;
                    }
                    return encryptStr;
                }
                return str ;
            },
            sign: function(str) {
                if(encryptOptions.options.isIE8){
                    return $.md5(str);
                } else {
                    return do_sm3_encrypt(str);
                }
            }

        }
    };
}();