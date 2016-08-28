#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @author: JeffMa
# @website: http://devework.com/
# @url: https://github.com/Jeff2Ma/AlfredWorkflow-DuoTai-Helper

'''
公共模块
将公用的函数收纳于此,方便调用
'''

import sys
import requests
import pickle
import subprocess

from workflow import Workflow, PasswordNotFound


reload(sys)
sys.setdefaultencoding('utf-8')

wf = Workflow()

'''
全局变量
'''
dt_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://duotai.org/login'
    }

dt_file_name = wf.datafile('cookie.txt')

'''
转化为文字说明
'''
def line_to_name(line):
    if line == 'usnv3':
        name = '北美华北专线'
    elif line == 'usev3':
        name = '北美华东专线'
    elif line == 'ussv3':
        name = '北美华南专线'
    elif line == 'jpnv3':
        name = '日本华北专线'
    elif line == 'jpev3':
        name = '日本华东专线'
    elif line == 'jpsv3':
        name = '日本华南专线'
    else:
        name = '啥线路都不是'

    return name

'''
 设置cookie
'''
def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

'''
 获取cookie
'''
def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

'''
 判断当前 keychain 中是否有保存账号信息
'''
def exist_keychain():
    email_in_data = wf.stored_data('duotai_email')

    if email_in_data == None:
        return False
    else:
        try:
            wf.get_password(email_in_data)
        except PasswordNotFound:
            return False
        return True

'''
获取 cookie
'''
def get_cookie():
    # 建立文件夹
    file = open(dt_file_name, "w")
    file.close()

    dt_login_url = 'https://duotai.org/api/signin'
    dt_email = get_data_email()
    dt_password = get_password()
    dt_login_payload = {"email": dt_email, "password": dt_password}

    # data=json.dumps(payload) 的语法不能正常实现
    r = requests.post(dt_login_url, headers=dt_headers, json=dt_login_payload)

    # print r.status_code
    # print r.text
    # print r.cookies
    # dt_cookies = r.cookies['connect.sid']
    if len(r.text) < 100:
        wf.add_item(u'重设账号信息',  # title
                    u'你之前的账号信息有误,请↵ 重新输入',  # subtitle
                    valid=True,
                    icon=u'icons/icon-warning.png',
                    arg=u'set_account')
        wf.send_feedback()
    else:
        save_cookies(r.cookies, dt_file_name)


'''
检测cookie 是否已经过期或不可用,如果是重新获取
'''
def check_cookie_ok():
    try:
        dt_cookies = load_cookies(dt_file_name)
    except:
        get_cookie()

    # print dt_cookies
    r2 = requests.get('https://duotai.org/api/user/', headers=dt_headers, cookies=dt_cookies)
    # print len(r2.text)
    # 判断条件: 如果因为过期等原因登录错误则返回信息len 较少
    if len(r2.text) < 100:
        # print 'cookie is wrong! restoring..'
        get_cookie()


'''
构建填写账号密码的窗口
'''
def dialog(msg, placeholder="", hide_input=False,
           is_choice=False, default_yes=True):
    if is_choice:
        default_button = "Yes" if default_yes else "No"
        scpt = """
            display dialog "{}" buttons {{"No", "Yes"}} default button "{}"
        """.format(msg, default_button)
    else:
        cmd = "with hidden answer" if hide_input else ""
        scpt = """
            set input_text to text returned of ¬
                (display dialog "{}" default answer "{}" {})
            return input_text
        """.format(msg, placeholder, cmd)
    p = subprocess.Popen(
        ["osascript"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p.communicate(scpt)
    if p.returncode != 0:
        return None
    return stdout.strip()

'''
添加账号信息并保存密码在 keychain 中
'''
def add_account():
    email_in_data = wf.stored_data('duotai_email')
    if email_in_data != None:
        default_email = email_in_data
    else:
        default_email = "example@duotai.org"

    duotai_email = dialog(
        u"请输入你的多态登录邮箱:", default_email)
    if duotai_email is None:
        print(u"添加账号失败!")
        return 0
    duotai_password = dialog(
        u"请输入你的多态登录密码:\n(密码将安全保存在系统 Keychain 中)",
        hide_input=True)
    if duotai_password is None:
        print(u"没有保存密码!")
        return 0
    if duotai_password is "":
        print(u"密码为空!")
        return 0

    # 保存多态邮箱到本地workflow data, 作为 keychain 中的入口 key
    wf.store_data('duotai_email', duotai_email)

    # email_in_data = wf.stored_data('duotai_email')
    # print email_in_data, duotai_email, duotai_password

    keychain_statue = ''
    # 判断当前 keychain 中是否有保存
    try:
        wf.get_password(duotai_email)
    except PasswordNotFound:
        keychain_statue = 'empty'

    # 如果keychain 没有,即 new 状态
    if keychain_statue == 'empty':
        # 保存在 keychain 中
        wf.save_password(duotai_email, duotai_password)
        print u"账号保存成功,请重新输入关键词激活使用!"
    else:
        # 删除再保存
        wf.delete_password(duotai_email)
        wf.save_password(duotai_email, duotai_password)
        print u"账号重新保存成功!"

'''
从 workflow data 中获取多态 email
'''
def get_data_email():
    data_email = wf.stored_data('duotai_email')
    # print data_email
    return data_email

'''
从 keychain 中获取密码
'''
def get_password():
    # 从 workflow data 中获取到邮箱名称(即保存在 keychain 中的"账户"中)
    data_email = wf.stored_data('duotai_email')

    # 获取密码, keychain 中的入口 key从上一步或得
    password = wf.get_password(data_email)
    # print password
    return password