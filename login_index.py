# -*- coding: utf-8 -*-

__author__ = 'EthanCui'

import re
import time
import base64

from pyv8 import PyV8
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# 没遇到登录需要验证码的情况，所以逻辑上并不严谨，仅参考

if __name__ == "__main__":

    session = requests.Session()
    headers = {
        "Host":"passport.baidu.com",
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    }

    session.get("http://index.baidu.com/",headers=headers,verify=False)
    # 需要生成cookies BAIDUID

    js = """
        function callback(){
            var h = "bd__cbs__";
            return h + Math.floor(Math.random() * 2147483648).toString(36);
            }

        function gid() {
                return "xxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (e) {
                    var t = 16 * Math.random() | 0, n = "x" == e ? t : 3 & t | 8;
                    return n.toString(16)
                }).toUpperCase()
            }
    """

    js_driver = PyV8.JSContext()
    js_driver.__enter__()
    js_driver.eval(js)

    gid = ctxt.locals.gid()
    # print(gid)
    callback1 = js_driver.locals.callback()
    callback2 = js_driver.locals.callback()
    callback3 = js_driver.locals.callback()

    token_url = "https://passport.baidu.com/v2/api/?getapi&tpl=nx&apiver=v3&tt=%s&class=login&gid=%s&" \
                "logintype=basicLogin&traceid=&callback=%s" % (time.time()*1000,gid,callback1)

    token_result = session.get(token_url,verify=False).text

    token_pattern = re.compile('"token"\s*:\s*"(.*?)",')
    token_obj = token_pattern.search(token_result)
    if token_obj:
        token = token_obj.group(1)
        # print(token)
    else:
        raise Exception(u"token匹配失败")

    key_url = "https://passport.baidu.com/v2/getpublickey?token=%s&tpl=nx&apiver=v3&tt=%s&gid=%s&traceid=&callback=%s" % (token,time.time()*1000,gid,callback2)

    key_result = session.get(key_url,headers=headers,verify=False).text

    pubkey_pattern = re.compile("""\s*"pubkey":'(.*?)'""")
    pubkey_obj = pubkey_pattern.search(key_result)
    if pubkey_obj:
        pubkey = pubkey_obj.group(1)
        # print(pubkey)
    else:
        raise Exception(u"pubkey匹配失败")
    pubkey = pubkey.replace("\\n","\n")

    key_pattern = re.compile("""\s*"key"\s*:\s*'(.*?)'""")
    key_obj = key_pattern.search(key_result)
    if key_obj:
        key = key_obj.group(1)
        # print(key)
    else:
        raise Exception(u"key匹配失败")

    password_unencrypt = "cuiliang188"
    rsakey = RSA.importKey(pubkey)
    cipher = PKCS1_v1_5.new(rsakey)
    password = base64.encodestring(cipher.encrypt(password_unencrypt))
    # print(password)

    data = {
        "staticpage":"http://index.baidu.com/v2/static/passport/v3Jump.html",
        "charset":"utf-8",
        "token":token,
        "tpl":"nx",
        "subpro":"",
        "apiver":"v3",
        "tt":"%d" % time.time()*1000,
        "codestring":"",
        "safeflg":0,
        "u":"http://index.baidu.com/?tpl=login",
        "isPhone":"",
        "detect":"",
        "gid":gid,
        "quick_user":0,
        "logintype":"basicLogin",
        "logLoginType":"pc_loginBasic",
        "idc":"",
        "loginmerge":True,
        "username":"cuiliang188@163.com",
        "password":password,
        "rsakey":key,
        "crypttype":12,
        "ppui_logintime":17614,
        "countrycode":"",
        "fp_uid":"2ee04e37b057f303a4bbfcb19c7c313e",
        "fp_info":"2ee04e37b057f303a4bbfcb19c7c313e002~~~QzQQYOyJIJ2x8JgiLJV_YQQvvyJcIXict0gcmo_yyJcIcw6Q0O6-F_PQB0bXQB0bSQQ1ZQQ9ty0hQFpVa6tgV9xXe6mCVcIHi9I4yFpz-9Hc-9Iow6-ogcIqg5HO-6Ivi9Io-cmHg5~FicICz6-vl6-0O5Q6U9TLkPt6~DYQoGYQoxYQoIYQbEy0PBCpheNp2sPpZqPl6EPJZfNqLjFTEkN1z2PT2sPpZ-Zl~HLnLRPTZUBJ6~PQ6~FlLjFQbUvn~svJ6dPlLYZqEcvnZHBJWjNT~HLJhxPlgiLJgi7sklLn3-BJhf9xqf61Og7xqV6-vRHy0~CLpZTvnZUNtOe9J3sc-oO9JXVc-CE9mYgclXOcIqOLmoV6m2H6JqevIYzLm0zc-qe9pCO6pc-vIXwLT6k6lCw9JL~v-FeLJqV5T2~vxvicx~T6Tvw6-3xLmcl6lXVv-Ce6pvVLT4Tvxcecp4HcI4sLxH-LJY-vxXl6mXgcIkHLxcVv-3~9JqiLmbyLpZTvnZUNtOw6IXzcTLHLxqV6m3xvIvzc-3TcxkTcI0O6-FivJZs6TYzvxHe6xCiLTCl6JYw9ILkcx4HLxb~cJ2xcmkT6IYeNYQbTYQb-YQbJYQbLQQYMysST0KXiO_syJNJgdPThwP0__QYQbrQQohYQoRYQoiYQoeYQoaYQokyP7Iqf6mYz6mXO9mY-9mFi6-Yi6X__",
        "dv":"tk0.8519010474187941528874622099@vva0Qwt32~0kqOour97j6hEoiU5rBCMd7UMgodIM69GFjK0ktgBEAxt32~0kqOour97j6hEoiU5rBCMd7UMgodIM69GFjK0kt~tE7xt32~0kqOour97j6hEoiU5rBCMd7UMgodIM69GFjK0kCpB3IxtEGOtmp5C5~v5NrBMjiC5jhUBriUAMBKRN~1LF5OBktztVzgBTzz0r7hENADC5jUMjhE5rxZMjijRwoyEJrXIDzjtkCjUq__ja0RjBE2d0kCztDzp9ktj0r7hENADC5jUMjhE5rxZMjiJLg6XUk5j9Dz~BDzptkGQBDpcLJ7KHmjOLwAcLTjTLni3syjTIgzwtE2Otd5g0kupBdtZ0r7hENADC5jUMjhE5rxZMjizGMBdAwiyIvzwBkCOBktw0kugtku~0r7hENADC5jUMjhE5rxZMjidAF6XsM7xwqqsBqxbIt2Lhxagtyzy0kGwuaYAnOz03PjtENztEqZBdCp9kR~Bkujt3PQBdCwt32z9EN_gassv7ZRkYa0wKfInoQ0J61sF7j0JBaLDx30ypjLJ7KIJKfIFC_Gast3tOtmzptdCg0kRQtmzpBkCz0kNztmzptdRw0kudBkRO9kRg",
        "traceid":"FAB8B101",
        "callback":"parent."+ callback3
    }
    # dv参数是根据 tk + Math.random() + 时间戳*1000 + @ + 根据鼠标移动轨迹，时间戳等长度 对 字母数字-~组成的数组进行按索引摘取拼接而成，没有检验啊？
    # fp_uid 是cookies值 fp_info 等都没进行校验，直接拿的浏览器模拟的值

    session.post("https://passport.baidu.com/v2/api/?login",data=data,headers=headers,verify=False)
    # print(response.text)
    new_header = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Host':'index.baidu.com'
    }
    response = session.post("http://index.baidu.com/Interface/api/pcPass",headers=new_header,verify=False).json()
    islogin = response['data']['result']['isLogin']
    if islogin:
        print(u"登录成功")
    else:
        print(u"登录失败")

    # print(session.cookies)

    new_header.update(
        {
        'Referer':'http://index.baidu.com/Helper/?tpl=brand&word='
        }
    )
    params = {
        'i':'1',
        'datetype':"m",
        "year":'2018',
        'no':'05'
    }
    brand_url = "http://index.baidu.com/Interface/Newwordgraph/getTopBrand"
    try:
        car_brand_result = session.get(brand_url,params=params,headers=new_header,verify=False).json()
        # print(car_brand_result)
        assert car_brand_result['status'] == "0"
    except:
        print("获取汽车搜索指数排行榜失败")

    print(car_brand_result['data']['data'])


















