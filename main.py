#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 一个多态ZPN 的助手管理型Alfred Workflow, 可通过本Workflow 直接查看账户信息,切换线路,开关某些模式
#
# @name: AlfredWorkflow-DuoTai-Helper
# @author: JeffMa
# @website: http://devework.com/
# @url: https://github.com/Jeff2Ma/AlfredWorkflow-DuoTai-Helper
#

'''
1) 主要关键词: dt
2) 变量及对应函数:

dt: 执行获取cookie 函数,通过xml展示可选参数及对应的说明;展示当前的代理情况:链接线路,边缘模式开启否,全网加速模式开启否,短地址(enter可拷贝)
dt set: 设置多态账号信息
dt switch: 展示当前所有可切换的线路
dt switch [line-name]: 切换具体线路
dt toggle [line-mode]: 开关/关闭相关模式
dt invite: 展示邀请码情况
'''

import sys
import requests
import json
import datetime
import subprocess
import webbrowser

import common  # 公共模块
from workflow import Workflow, PasswordNotFound

reload(sys)
sys.setdefaultencoding('utf-8')

wf = Workflow(
    update_settings={
        # Your username and the workflow's repo's name
        'github_slug': 'Jeff2Ma/AlfredWorkflow-DuoTai-Helper',
        # Optional number of days between checks for updates
        'frequency': 7
    }
)

'''
对输入的参数进行加工
'''
def arg(pos):
    try:
        args = sys.argv[1].split()
    except:
        args = []
    try:
        return args[pos]
    except:
        return ""

'''
获取用户信息
'''
def get_main_info(cookies):

    r2 = requests.get('https://duotai.org/api/user/', headers=common.dt_headers, cookies=cookies)
    text_json = json.loads(r2.text)

    # 当前连接的线路
    current_line_mode = text_json['settings']['line_mode']
    current_line_modes = text_json['settings']['lines']
    current_line_mode_name = common.line_to_name(current_line_mode, current_line_modes)
    # print current_line_mode_name

    # 是否开启了全球加速
    is_global_mode = text_json['settings']['global_mode']
    is_global_mode_name = ('ON' if is_global_mode else 'OFF')
    # print '全球加速状态:' + is_global_mode_name

    # 是否开启了边缘模式
    is_edge_mode = text_json['settings']['edge_mode']
    is_edge_mode_name = ('ON' if is_edge_mode else 'OFF')
    # print '边缘模式状态:' + is_edge_mode_name

    # 当前的短地址
    current_shortid = text_json['package']['shortid']
    # print 'http://xduotai.com/' + current_shortid

    # 当前的代理域名
    current_hostname = text_json['package']['hostname']

    # 当前的端口
    current_port = text_json['package']['port']
    # print current_port

    # 当前使用套餐信息
    display_name = text_json['package']['display_name']
    # print display_name

    # 个人信息
    profile_name = text_json['profile']['nickname']
    profile_email = text_json['profile']['email']
    # print profile_name + ' , '+ profile_email

    # 到期时间
    expire_at = text_json['package']['expire_at']
    expire_at = str(expire_at)[0:-3]
    date_array = datetime.datetime.utcfromtimestamp(float(expire_at))
    readable_time = date_array.strftime("%Y-%m-%d")
    # print readable_time

    # 流量
    usage_traffic = text_json['package']['usage'][0]
    amount_traffic = text_json['package']['usage'][1]

    # 组合展示信息 part1
    item_title = u'当前线路: ' + current_line_mode_name
    item_icon = 'regions/icon-' + common.region_name(current_line_mode[0:2]) + '.png'
    wf.add_item(item_title,  #title
                u'↵ 进行线路切换', #sub title
                arg=u'set',
                autocomplete=u'switch',
                valid=False,
                icon=item_icon)

    # 组合展示信息 part5
    '''
    item_title_5 = u'边缘模式: ' + is_edge_mode_name
    item_sub_title_5 = u'↵ ' + (u'关闭' if is_edge_mode else u'开启')
    item_arg_5 = ('toggle edge_mode_close' if is_edge_mode else 'toggle edge_mode_open')
    item_icon_5 = 'icons/icon-nw3.png'
    wf.add_item(item_title_5,
                item_sub_title_5,
                arg=item_arg_5,
                valid=True,
                icon=item_icon_5)
    '''


    # 组合展示信息 part4
    item_title_4 = u'全网加速: ' + is_global_mode_name
    item_sub_title_4 = u'↵ ' + (u'关闭' if is_global_mode else u'开启')
    item_arg_4 = ('toggle global_mode_close' if is_global_mode else 'toggle global_mode_open')
    item_icon_4 = 'icons/icon-nw2.png'
    wf.add_item(item_title_4,
                item_sub_title_4,
                arg=item_arg_4,
                valid=True,
                icon=item_icon_4)

    # 组合展示信息 part6
    item_title_6 = u'剩余流量: ' + common.convert_size(amount_traffic - usage_traffic)
    item_sub_title_6 = u'总共: %s' % common.convert_size(amount_traffic)
    item_sub_tip_6 = u'已用/剩余: %s/%s' % (common.convert_size(usage_traffic), common.convert_size(amount_traffic))
    wf.add_item(item_title_6,
                item_sub_title_6,
                modifier_subtitles={
                    u'fn': item_sub_tip_6,
                    u'ctrl': item_sub_tip_6,
                    u'alt': item_sub_tip_6,
                    u'cmd': item_sub_tip_6,
                },
                valid=False,
                icon=u'icons/icon-chart.png')

    # 组合展示信息 part2
    item_title_2 =  current_hostname + ':' + str(current_port)
    item_sub_title_2 = 'http://xduotai.com/' + current_shortid + '.pac'
    item_sub_tip_2 = u'提示: ↵ 将路径保存在系统的代理设置中, 按下 CMD+C 将复制到剪贴板'
    wf.add_item(item_title_2,
                item_sub_title_2,
                modifier_subtitles={
                    u'fn': item_sub_tip_2,
                    u'ctrl': item_sub_tip_2,
                    u'alt': item_sub_tip_2,
                    u'cmd': item_sub_tip_2,
                },
                arg=u'set_pac_url '+item_sub_title_2, # PAC 文件路径将安装到系统设置中
                valid=True,
                icon=u'icons/icon-fly.png',
                copytext=item_sub_title_2)

    # 组合展示信息 part3
    item_title_3 = u'套餐: ' + display_name + u', 至 ' + readable_time
    item_sub_title_3 = u'用户: ' + profile_name + ' , ' + u'邮箱: ' + profile_email
    item_sub_tip_3 = u'提示: 按下 CMD+C 将复制[ ' + item_title_2 +u' ]到剪贴板'
    wf.add_item(item_title_3,
                item_sub_title_3,
                modifier_subtitles={
                    u'fn': item_sub_tip_3,
                    u'ctrl': item_sub_tip_3,
                    u'alt': item_sub_tip_3,
                    u'cmd': item_sub_tip_3,
                },
                arg=item_title_3,
                valid=False,
                icon=u'icons/icon-stat.png',
                copytext=item_title_2)

    wf.send_feedback()

'''
默认的显示xml,即输入dt 后的xml 结果,区分是否已经设置好账号
'''
def default_item(keyword):
    keyword = keyword.lower()
    # if keyword in "set" or keyword == "":
    if common.exist_keychain():
        common.check_cookie_ok()
        cookies = common.load_cookies(common.dt_file_name)
        get_main_info(cookies)
    else:
        wf.add_item(u'添加账号',  # title
                    u'↵ 添加多态账号',  # subtitle
                    valid=True,
                    icon=u'icons/icon-set.png',
                    arg=u'set_account')
        wf.send_feedback()

'''
展示可切换线路
'''
def show_line_info():
    wf.add_item(
        u'提示: 选中线路,↵ 即可切换',  # title
        '',
        valid=False,
        icon=u'icons/icon-info.png',
        arg=u'set_account')

    dt_cookies = common.load_cookies(common.dt_file_name)
    r3 = requests.get('https://duotai.org/api/user/', headers=common.dt_headers, cookies=dt_cookies)
    text_json = json.loads(r3.text)
    i = 0
    for json_item in text_json['settings']['lines']:
        # print json_item['line']
        # print json_item['line'][0:2]
        # print json_item['name']

        if text_json['settings']['line_mode'] == json_item['line']:
            item_title = json_item['name'] + '(当前线路)'
        else:
            item_title = json_item['name']

        region_single = json_item['line'][0:2]

        wf.add_item(item_title,
                    '',
                    valid=True,
                    icon='regions/icon-' + common.region_name(region_single) + '.png',
                    arg="switch " + json_item['line'])
        i = i + 1
    wf.send_feedback()

'''
切换线路函数
'''
def switch_line(line_mode):
    line_mode = line_mode.lower()
    request_payload = {"line_mode": line_mode}
    dt_cookies = common.load_cookies(common.dt_file_name)
    r4 = requests.put('https://duotai.org/api/user/settings', headers=common.dt_headers, cookies=dt_cookies,
                      json=request_payload)

    if r4.status_code == 200:
        print u"成功切换到目标线路[%s]!" % line_mode


'''
设置PAC 文件路径到系统代理配置
'''
def set_pac_url(pac_url):
    # /usr/sbin/networksetup -setautoproxyurl Wi-Fi $pac_url
    p = subprocess.Popen([
        "/usr/sbin/networksetup",
        "-setautoproxyurl",
        "Wi-Fi",
        pac_url],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    if p.returncode != 0:
        print u"无法设置!请给予系统权限!"
    else:
        print u"成功设置PAC 文件路径到系统代理配置!"

'''
关闭/开启相关模式
'''
def toggle_mode(mode_command):
    if mode_command == 'global_mode_close':
        request_payload = {"global_mode": "false"}
    elif mode_command == 'global_mode_open':
        request_payload = {"global_mode": "true"}
    elif mode_command == 'edge_mode_close':
        request_payload = {"edge_mode": "false"}
    elif mode_command == 'edge_mode_open':
        request_payload = {"edge_mode": "true"}
    else:
        return

    dt_cookies = common.load_cookies(common.dt_file_name)
    if request_payload:
        r4 = requests.put('https://duotai.org/api/user/settings', headers=common.dt_headers, cookies=dt_cookies,json=request_payload)
        # print r4.status_code
        if r4.status_code == 200:
            print '成功执行任务[' + mode_command + ']!'


'''
邀请情况
'''
def invite_info():
    dt_cookies = common.load_cookies(common.dt_file_name)
    r5 = requests.get('https://duotai.org/api/user/invite-codes', headers=common.dt_headers, cookies=dt_cookies)
    text_json = json.loads(r5.text)

    # print text_json['invite_codes']

    if len(text_json['invite_codes']) > 0:
        invite_code = text_json['invite_codes'][0]['code']
        invite_info_title = u"有效邀请码: " + invite_code.upper()
        wf.add_item(invite_info_title,
                    u"按下 CMD+C 即可复制到剪贴板",
                    valid=False,
                    icon=u'icons/icon-new.png',
                    copytext=invite_code.upper())
    else:
        wf.add_item(u"暂无邀请码",
                    u" ↵ 生成新的邀请码",
                    arg=u'create_invite_code',
                    valid=True,
                    icon=u'icons/icon-add.png')

    wf.send_feedback()

'''
生成邀请码函数
'''
def create_invite_code():
    dt_cookies = common.load_cookies(common.dt_file_name)
    r6 = requests.post('https://duotai.org/api/user/invite-codes', headers=common.dt_headers, cookies=dt_cookies)
    text_json = json.loads(r6.text)
    # print text_json
    # 判断是否正常生成
    if len(text_json) > 10:
        new_code = text_json['code']
        print u"新的邀请码:" + new_code.upper()
    else:
        print u"无法生成新的邀请码!"


'''
更新提醒
'''
def update_notic():
    wf.check_update()
    # wf.cached_data('__workflow_update_status', max_age=0)
    if wf.update_available:
        wf.add_item(u'提醒: DuoTai-Helper 有更新!',
                    u'检测到本workflow 有更新版本, 请 ↵ 前往下载',
                    arg=u'update',
                    valid=True,
                    icon=u'icons/icon-update.png')


'''
引导到下载页
'''
def update_action():
    webbrowser.open_new('https://github.com/Jeff2Ma/AlfredWorkflow-DuoTai-Helper/releases')

'''
删除多态账号
'''
def remove_account():
    wf.clear_data()
    print u"删除成功!"

'''
删除账号的item
'''
def rm_item():
    wf.add_item(u"删除保存的多态账号",
                u" ↵ 将删除账号",
                arg=u'remove_account',
                valid=True,
                icon=u'icons/icon-rm.png')

    wf.send_feedback()

'''
主函数
'''
def main():
    update_notic()
    if arg(1) == "switch":
        if arg(2) == "":
            show_line_info()
        else:
            switch_line(arg(2))
    elif arg(1) == "invite":
            invite_info()
    elif arg(1) == "rm":
        rm_item()
    elif arg(0) == "default_item":
        default_item(arg(1))
    elif arg(0) == "second_task":
        if arg(1) == "toggle":
            toggle_mode(arg(2))
        elif arg(1) == "set_account":
            common.add_account()
        elif arg(1) == "set_pac_url":
            set_pac_url(arg(2))
        elif arg(1) == "create_invite_code":
            create_invite_code()
        elif arg(1) == "remove_account":
            remove_account()
        elif arg(1) == "update":
            update_action()


if __name__ == '__main__':
    main()
