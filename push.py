#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: push.py
#         Desc: 2015-15/1/5:下午1:54
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import time
import tornado.websocket
from settings import *
from swan import open_service
from salt_api.salt_https_api import token_id, salt_api_token
import nmap
from functools import partial, wraps
from concurrent.futures import ThreadPoolExecutor
import json
import tornado.gen
import tornado.concurrent
from tornado.concurrent import run_on_executor
from salt_api.cmdb_mysql import jobs_class
# from salt.output import display_output
import yaml
from conf.config import salt_api_pass, salt_api_url, salt_api_user
from tornado import gen
from api.git_class import SaltApiGit
from api.check_api import CheckApi
import requests

EXECUTOR = ThreadPoolExecutor(max_workers=4)
redis_ip = "127.0.0.1"
rc = redis.Redis(host=redis_ip, port=6379, db=1)
ps = rc.pubsub()
ps.subscribe("web_chat")


def unblock(f):
    # @tornado.web.asynchronous
    @wraps(f)
    def wrapper(*args, **kwargs):
        self = args[0]

        def callback(future):
            self.write(future.result())
            self.finish()

        EXECUTOR.submit(
            partial(f, *args, **kwargs)
        ).add_done_callback(
            lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                partial(callback, future)))

    return wrapper


def web_socket_api(data, uid):
    """
    延迟1秒发送数据,用于确保websocket第一次建立成功
    :param data:
    :param uid:
    :return:
    """
    rc = redis.Redis(host=redis_ip, port=6379, db=1)
    ps = rc.pubsub()
    ps.subscribe("web_chat")
    time.sleep(1)
    rc.publish('web_chat', json.dumps({"message": data, "to_email": uid}))
    return True


# class push_data(tornado.web.RequestHandler):
class push_data(tornado.web.RequestHandler):
    """
    注册方法
    """

    def get(self):
        self.write(json.dumps({"retCode": 403, "result": "error"}, indent=4))

    executor = ThreadPoolExecutor(100)

    # @tornado.web.asynchronous
    @gen.coroutine
    # @asynchronous
    def post(self):
        """
        接收数据后确认返回收到消息
        异步传给后端逻缉进行处理
        """
        print "接收到数据"
        self.write(json.dumps({"retCode": 200, "result": "OK"}, indent=4))
        self.finish()
        data = json.loads(self.request.body)
        uid = data.get("uid")

        if data.get("choose") == 0:
            script = data.get("script")
            swan_name = data.get("code_name")
            host = data.get("host")
            tgt = data.get("tgt")
            arg = data.get("arg")
            yield self.web_socket_api("正常业务发布，发布正在运行中，逻缉比较多，请耐心等待", uid)

            # 自动化发布普通任务
            token_api_id = token_id()

            # 将主机名放入list 传给salt api接口
            node_list = [host[i] for i in host.keys()]

            node_count = len(node_list)

            add_key = salt_api_token(
                {'client': 'local_async', 'fun': 'cmd.script', 'tgt': node_list,
                 "arg": ["salt://%s" % (script), tgt], 'timeout': 100, 'expr_form': 'list'}, salt_api_url,
                {"X-Auth-Token": token_api_id}
            )
            status = add_key.run()
            rst = yield self.web_socket_api("正在执行中", uid)
            if rst:
                print "已通知salt开始执行"

            jid_data = status.get("return")
            print jid_data
            jid_id = {"jid": ""}
            for i in jid_data:
                s = i["jid"]
                jid_id["jid"] = s
                yield self.web_socket_api("saltstack jid %s" % (s), uid)
            # rst = yield  self.jobs_data_find(s, uid, len(node_list))

            print "程序正在后台运行中"

            yield self.salt_job(jid_id, node_count, uid)
            yield self.web_socket_api("********************************************", uid)
            print "发布结束"

        # 选择配置中心则走以下逻缉
        if data.get("choose") == 1:
            print "通知配置中心"
            status = {"retCode": 1}
            host = data.get("host")
            ip_data = data.get("ip_data")
            for i in ip_data:
                Open_push = open_service(data.get("config_name"), i)
                rest = Open_push.offline_run()
                msg = rest.get("retMsg")
                if int(rest.get("retCode")) == 200:
                    # if 200 == 200:
                    yield self.web_socket_api("下线成功", uid)
                    print "下线成功"
                else:
                    status["retCode"] = 0
                    yield self.web_socket_api("下线失败,发布任务停止", uid)
                    yield self.web_socket_api(msg, uid)
                    print "下线失败,发布任务停止"
                    break

                # 发布操作
                if status["retCode"]:
                    print "请求salt开始执行salt文件"
                    yield self.web_socket_api("发布代码中....", uid)
                    # 执行模块
                    token_api_id = token_id()
                    print data.get("sls")
                    list = salt_api_token(
                        {'client': 'local_async', 'fun': 'state.sls', 'tgt': host.get(i),
                         "arg": data.get("sls"), 'timeout': 100}, salt_api_url,
                        {"X-Auth-Token": token_api_id}
                    )
                    master_status = list.run()
                    print master_status
                    yield self.web_socket_api("saltstack执行完成", uid)
                    print "已通知salt开始执行"

                    yield self.web_socket_api("********************************************", uid)
                    yield self.web_socket_api("检测端口中....", uid)
                    open_port = data.get("check_port")
                    p = "-p %s" % (str(open_port))
                    port_sum = len(open_port)
                    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    print "-" * 100
                    print i
                    ip = u"%s发布完成" % (i)
                    rst = yield self.config_push(i, p, open_port, data.get("config_name"), uid)
                    if rst:
                        yield self.web_socket_api(ip, uid)
                        rst = yield self.time_sleep(10)
                        if rst:
                            yield self.web_socket_api(ip, uid)
                            print "发布完成"

                    else:
                        yield self.web_socket_api("发布失败", uid)

        if data.get("choose") == 2:
            print(uid)
            yield self.web_socket_api("正常业务发布，发布正在运行中，逻缉比较多，请耐心等待", uid)
            print("set ok")

    @run_on_executor
    def web_socket_api(self, data, uid):
        """
        延迟1秒发送数据,用于确保websocket第一次建立成功
        :param data:
        :param uid:
        :return:
        """

        time.sleep(1)
        rc.publish('web_chat', json.dumps({"message": data, "to_email": uid}))
        return True

    @run_on_executor
    def time_sleep(self, data):
        time.sleep(data)
        return True

    @run_on_executor
    def salt_job(self, job, node_count, uid):
        while True:
            s = jobs_class(job["jid"])
            if len(s) == node_count:
                self.web_socket_api("已发布完成", uid)
                print "发布完成"
                break
            else:
                if len(s) != 0:
                    for i in s:
                        self.web_socket_api("%s发布完成" % (len(i)), uid)
                else:
                    self.web_socket_api("发布中，请稍后", uid)
                print "发布中，请稍后"
                time.sleep(5)
        return True

    @run_on_executor
    def config_push(self, host, p, open_port, config_name, uid):
        nm = nmap.PortScanner()
        port_sum = len(open_port.split(","))
        self.web_socket_api("10秒后检测端口和业务是否正常", uid)
        time.sleep(10)
        print "开始检测端口"
        ok_list = []
        port_data = open_port.split(",")
        host = "%s" % (str(host))
        p = "%s" % (p)
        while True:
            s = nm.scan(host, arguments=p)
            for sp in port_data:
                port = int(sp)
                rst = s["scan"][host]["tcp"][port]["state"]
                if rst != "open":
                    port_error = "%s %s端口未启动，5秒后重试 %s" % (
                        host, port, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                    self.web_socket_api(port_error, uid)
                    print "端口检测失败"
                else:
                    if port not in ok_list:
                        ok_list.append(port)
                        msg = "端口%s检测正常 %s" % (port, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                        self.web_socket_api(msg, uid)
                    print "判断所有端口是否全部存活", port
            if len(ok_list) == port_sum:
                port_rst = "%s端口检测正常，正在通知配置中心上线 %s" % (
                    ok_list, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                self.web_socket_api(port_rst, uid)
                print ok_list
                print "端口全部正常"
                break
            else:
                print "端口检测未完成"
                time.sleep(5)

        Open_push = open_service(config_name, host)
        rest = Open_push.online_run()
        if int(rest.get("retCode")) == 200:
            msg = '%s上线成功' % (host)
            self.web_socket_api(msg, uid)
            print "上线成功"
            return True
        else:
            self.web_socket_api("上线失败,10秒后重试，如上线不成功，则发布失败", uid)
            self.web_socket_api(rest.get("retMsg"), uid)
            time.sleep(10)
            Open_push = open_service(config_name, host)
            rest = Open_push.online_run()
            if int(rest.get("retCode")) == 200:
                msg = '%s上线成功 %s' % (host, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                self.web_socket_api(msg, uid)
                print "上线成功"
                return True
            else:
                msg = '%s上线失败' % (host)
                self.web_socket_api(msg, uid)
                print "上线失败"
                return False


class git_swan(tornado.web.RequestHandler):
    """
    注册方法
    """

    def get(self):
        self.write(json.dumps({"status": 403, "result": "error"}, indent=4))

    executor = ThreadPoolExecutor(100)

    # # @tornado.web.asynchronous
    @gen.coroutine
    # @asynchronous
    def post(self):
        """
        接收数据后确认返回收到消息
        异步传给后端逻缉进行处理
        """
        print "git发布接收到数据"
        self.write(json.dumps({"status": 200, "result": "OK"}, indent=4))
        self.finish()
        data = json.loads(self.request.body)
        uid = data.get("uid")
        arg = data.get("arg")
        choose = int(data.get("choose"))
        yield self.web_socket_api("git模式发布,任务正在执行中....", uid)
        print arg
        print data.get("CheckUrl")
        if data.get("reset_code"):
            s = yield self.NodeReset(data, uid)
            print "回滚数据"
            if s:
                yield self.web_socket_api(u"发布完成", uid)
            return
        elif data.get("git_minion"):
            s = yield self.salt_pull(data, uid)

            if s:
                yield self.web_socket_api(u"发布完成", uid)
            return

        else:
            print "is ok"
            s = yield self.NodePull(data, uid)
            if s:
                yield self.web_socket_api(u"发布完成", uid)
            return

    @run_on_executor
    def web_socket_api(self, data, uid):
        """
        延迟1秒发送数据,用于确保websocket第一次建立成功
        :param data:
        :param uid:
        :return:
        """

        time.sleep(1)
        rc.publish('web_chat', json.dumps({"message": data, "to_email": uid}))

        return True

    @run_on_executor
    def time_sleep(self, data):
        time.sleep(data)
        return True

    @run_on_executor
    def salt_pull(self, data, uid):
        host = data.get("host")
        version = data.get("git_version")
        choose = int(data.get("choose"))

        # 自动化发布普通任务
        token_api_id = token_id()

        # 将主机名放入list 传给salt api接口
        node_list = [host[i] for i in host.keys()]
        git_code_path = "%s%s" % (data.get("git_minion_path"), data.get("code_name"))
        code_path = data.get("code_path")
        user = "user=%s" % data.get("git_code_user")

        shell = data.get("shell")
        shell_status = int(data.get("shell_status"))
        if shell and shell_status == 0:
            print "需要先执行脚本 "
            code_checkout = SaltApiGit(arg=shell, tgt=node_list,
                                       token_api_id=token_api_id)
            rst = code_checkout.CmdRun()
            result = rst["return"][0]

            for k, v in result.items():
                self.web_socket_api(k, uid)
                self.web_socket_api(v, uid)
            # self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
            self.web_socket_api(u"脚本执行完毕", uid)
        # 如未选择版本,默认为master分支
        if version:

            code_pull = SaltApiGit(arg=[git_code_path, "origin"], token_api_id=token_api_id,
                                   tgt=data.get("git_minion")
                                   )
            status = code_pull.pull()
            self.web_socket_api(yaml.dump(status, default_flow_style=False), uid)
            self.web_socket_api(u"拉取代码完成", uid)

            code_checkout = SaltApiGit(arg=[git_code_path, version], tgt=data.get("git_minion"),
                                       token_api_id=token_api_id)
            print code_checkout.checkout()
            self.web_socket_api(u"切分支完分完毕", uid)

            code_push = SaltApiGit(tgt=data.get("git_minion"), arg=[git_code_path, "ops", version, "-f"],
                                   token_api_id=token_api_id
                                   )
            push_status = code_push.push()

            self.web_socket_api(yaml.dump(push_status, default_flow_style=False), uid)

            version_status = SaltApiGit(tgt=data.get("git_minion"), arg=[git_code_path, version],
                                        token_api_id=token_api_id)
            git_master_version = version_status.version()["return"][0][data.get("git_minion")]
            message = u"发布版本号: %s" % git_master_version
            self.web_socket_api(message, uid)

        else:
            self.web_socket_api(u"Error: 发布中止->请选择分支或参数", uid)
            return False

        time.sleep(1)
        self.web_socket_api(u"push远程分支完成", uid)
        self.web_socket_api(u"等待10秒........", uid)
        time.sleep(10)
        self.web_socket_api(u"通知需要更新代码的主机开始拉取代码........", uid)
        if version:
            u"""
            添加git user config
            """
            setname = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "user.name", "ops", user], token_api_id=token_api_id
            )
            setname.config_set()

            setname = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "user.email", "ops@fun.tv", user], token_api_id=token_api_id
            )
            setname.config_set()
            self.web_socket_api(u"开始拉取代码........", uid)
            code_pull = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "origin", user], token_api_id=token_api_id
            )
            print code_pull.pull()

            node_code_checkout = SaltApiGit(
                tgt=node_list,
                arg=[code_path, version], token_api_id=token_api_id
            )
            print(node_code_checkout.checkout())

        else:
            self.web_socket_api(u"Error: 发布中止->请选择分支或参数", uid)
            return False
        self.web_socket_api(u"拉取代码已完成,正在读取版本号......", uid)
        version_status = SaltApiGit(tgt=node_list, arg=code_path, token_api_id=token_api_id)
        rst = version_status.version().get("return")[0]
        self.web_socket_api(u"版本号读取完成......", uid)
        self.web_socket_api(u"开始验证版本号......", uid)
        for i in host.keys():
            ip = host.get(i, False)
            print ip
            host_rst = rst.get(ip, False)
            if host_rst and host_rst == git_master_version:
                message = u'%s 版本号: %s 发布成功' % (i, host_rst)
                self.web_socket_api(message, uid)
            elif host_rst and host_rst != git_master_version:
                message = u'%s 版本号: %s 发布失败' % (i, host_rst)
                self.web_socket_api(message, uid)
            else:
                message = u"%s未返回数据" % i
                self.web_socket_api(message, uid)

        self.web_socket_api(u"通知主机更新代完毕", uid)
        if shell and shell_status == 1:
            code_checkout = SaltApiGit(arg=shell, tgt=node_list,
                                       token_api_id=token_api_id)
            rst = code_checkout.CmdRun()
            self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
            self.web_socket_api(u"脚本执行完毕", uid)
            return True

        return True

    @run_on_executor
    def NodePull(self, data, uid):
        print "开始发布"
        user = "user=%s" % data.get("git_code_user")
        host = data.get("host")
        version = data.get("git_version")

        # 自动化发布普通任务
        token_api_id = token_id()

        # 将主机名放入list 传给salt api接口
        node_list = [host[i] for i in host.keys()]
        code_path = data.get("code_path")
        # 如未选择版本,默认为master分支
        shell = data.get("shell")
        shell_status = int(data.get("shell_status"))
        if shell and shell_status == 0:
            print "需要先执行脚本 "
            code_checkout = SaltApiGit(arg=shell, tgt=node_list,
                                       token_api_id=token_api_id)
            rst = code_checkout.CmdRun()
            self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
            self.web_socket_api(u"脚本执行完毕", uid)

        if version:
            setname = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "user.name", "ops", user], token_api_id=token_api_id
            )
            setname.config_set()

            setname = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "user.email", "ops@fun.tv", user], token_api_id=token_api_id
            )
            setname.config_set()
            code_pull = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "origin"], token_api_id=token_api_id
            )
            code_pull.pull()

            node_code_checkout = SaltApiGit(
                tgt=node_list,
                arg=[code_path, version, user], token_api_id=token_api_id
            )
            node_code_checkout.checkout()

            version_status = SaltApiGit(tgt=node_list, arg=code_path, token_api_id=token_api_id)
            rst = version_status.version().get("return")[0]

            for i in host.keys():
                ip = host.get(i, False)
                host_rst = rst.get(ip, False)

                message = u'%s 版本号: %s' % (i, host_rst)
                self.web_socket_api(message, uid)

            self.web_socket_api(u"代码更新代完毕", uid)
            if shell and shell_status == 1:
                print "需要先执行脚本 "
                code_checkout = SaltApiGit(arg=shell, tgt=node_list,
                                           token_api_id=token_api_id)
                rst = code_checkout.CmdRun()
                self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
                self.web_socket_api(u"脚本执行完毕", uid)

            return True
        else:
            self.web_socket_api(u"Error: 发布中止->请选择分支或参数", uid)
            return False

    @run_on_executor
    def NodeReset(self, data, uid):
        print "开始发布"
        user = "user=%s" % data.get("git_code_user")
        host = data.get("host")
        version = data.get("git_version")
        reset_code = data.get("reset_code")

        # 自动化发布普通任务
        token_api_id = token_id()

        # 将主机名放入list 传给salt api接口

        node_list = [host[i] for i in host.keys()]
        code_path = data.get("code_path")

        # 如未选择版本,默认为master分支
        if reset_code:
            setname = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "user.name", "ops", user], token_api_id=token_api_id
            )
            setname.config_set()

            setname = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "user.email", "ops@fun.tv", user], token_api_id=token_api_id
            )
            setname.config_set()
            branch_name = "opts='--hard %s'" % reset_code

            node_code_checkout = SaltApiGit(
                tgt=node_list,
                arg=[code_path, version, user], token_api_id=token_api_id
            )
            node_code_checkout.checkout()
            code_pull = SaltApiGit(
                tgt=node_list,
                arg=[code_path, branch_name, user], token_api_id=token_api_id
            )
            print "开始回滚"
            rst = code_pull.reset()
            self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
            self.web_socket_api(u"代码回滚代完毕", uid)
            version_status = SaltApiGit(tgt=node_list, arg=code_path, token_api_id=token_api_id)
            rst = version_status.version().get("return")[0]

            for i in host.keys():
                ip = host.get(i, False)
                host_rst = rst.get(ip, False)

                message = u'%s 版本号: %s' % (i, host_rst)
                self.web_socket_api(message, uid)
            return True

        else:
            self.web_socket_api(u"请输入回滚版本号", uid)
            return False


class git_shell(tornado.web.RequestHandler):
    """
    注册方法
    """

    def get(self):
        self.write(json.dumps({"retCode": 403, "result": u"数据格式错误"}, indent=4))
        return

    executor = ThreadPoolExecutor(100)

    # # @tornado.web.asynchronous
    @gen.coroutine
    # @asynchronous
    def post(self):
        """
        接收数据后确认返回收到消息
        异步传给后端逻缉进行处理
        """
        print "git发布接收到数据"
        self.write(json.dumps({"status": 200, "result": "OK"}, indent=4))
        self.finish()
        data = json.loads(self.request.body)
        uid = data.get("uid")
        yield self.web_socket_api("shell模式发布,任务正在执行中....", uid)

        s = yield self.salt_pull(data, uid)
        if s:
            yield self.web_socket_api(u"发布完成", uid)
        return

    @run_on_executor
    def web_socket_api(self, data, uid):
        """
        延迟1秒发送数据,用于确保websocket第一次建立成功
        :param data:
        :param uid:
        :return:
        """

        time.sleep(1)
        rc.publish('web_chat', json.dumps({"message": data, "to_email": uid}))

        return True

    @run_on_executor
    def time_sleep(self, data):
        time.sleep(data)
        return True

    @run_on_executor
    def salt_pull(self, data, uid):
        shell = data.get("shell")
        host = data.get("host")
        node_list = [host[i] for i in host.keys()]
        # 自动化发布普通任务
        token_api_id = token_id()
        tgt = data.get("tgt")
        if tgt:
            shell = "%s %s" % (shell, tgt)
            print shell
            code_checkout = SaltApiGit(arg=shell, tgt=node_list,
                                       token_api_id=token_api_id)
        else:
            code_checkout = SaltApiGit(arg=shell, tgt=node_list,
                                       token_api_id=token_api_id)
        rst = code_checkout.CmdRun()
        result = rst["return"][0]

        for k, v in result.items():
            self.web_socket_api(k, uid)
            self.web_socket_api(v, uid)

        self.web_socket_api(u"shell执行完毕", uid)

        return True


class GitJava(tornado.web.RequestHandler):
    """
    注册方法
    """

    def get(self):
        self.write(json.dumps({"retCode": 403, "result": u"数据格式错误"}, indent=4))
        return

    executor = ThreadPoolExecutor(100)

    # # @tornado.web.asynchronous
    @gen.coroutine
    # @asynchronous
    def post(self):
        """
        接收数据后确认返回收到消息
        异步传给后端逻缉进行处理
        """
        print "git发布接收到数据"
        self.write(json.dumps({"status": 200, "result": "OK"}, indent=4))
        self.finish()
        data = json.loads(self.request.body)
        uid = data.get("uid")
        choose = int(data.get("choose"))
        yield self.web_socket_api("git模式发布,任务正在执行中....", uid)
        if data.get("reset_code"):
            s = yield self.NodeReset(data, uid)
            print "回滚数据"
            if s:
                yield self.web_socket_api(u"发布完成", uid)
                yield self.TomcatRestart(data, uid)
            return
        elif data.get("git_minion"):
            s = yield self.salt_pull(data, uid, agent=True)

            if s:
                yield self.web_socket_api(u"发布完成", uid)
                yield self.TomcatRestart(data, uid)
            else:
                yield self.web_socket_api(u"发布中止", uid)
                return

        else:
            print "无git agent发布"
            print uid
            s = yield self.NodePull(data, uid)
            # s = yield self.NodePull(data, uid, agent=False)
            if s:
                yield self.web_socket_api(u"发布完成", uid)
                yield self.TomcatRestart(data, uid)
            return

    @run_on_executor
    def web_socket_api(self, data, uid):
        """
        延迟1秒发送数据,用于确保websocket第一次建立成功
        :param data:
        :param uid:
        :return:
        """
        time.sleep(1)
        rc.publish('web_chat', json.dumps({"message": data, "to_email": uid}))

        return True

    @run_on_executor
    def time_sleep(self, data):
        time.sleep(data)
        return True

    @run_on_executor
    def salt_pull(self, data, uid, agent=True):
        host = data.get("host")
        version = data.get("git_version", False)
        print version
        if not version:
            self.web_socket_api(u"发布失败选择分支名称或参数", uid)
            return False
        arg = data.get("arg")
        CheckUrl = data.get("CheckUrl")

        # 自动化发布普通任务
        token_api_id = token_id()

        # 将主机名放入list 传给salt api接口
        node_list = [host[i] for i in host.keys()]
        git_code_path = "%s%s" % (data.get("git_minion_path"), data.get("code_name"))
        code_path = data.get("code_path")
        user = "user=%s" % data.get("git_code_user")
        shell = data.get("shell")
        shell_status = int(data.get("shell_status"))
        if shell and shell == 0:
            print "需要先执行脚本 "
            code_checkout = SaltApiGit(arg=shell, tgt=node_list,
                                       token_api_id=token_api_id)
            rst = code_checkout.CmdRun()
            result = rst["return"][0]

            for k, v in result.items():
                self.web_socket_api(k, uid)
                self.web_socket_api(v, uid)
            # self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
            self.web_socket_api(u"脚本执行完毕", uid)
        # 如未选择版本,默认为master分支
        # print u"选择", version, u"版本哦"
        if agent:
            for i in range(0, 2):

                code_pull = SaltApiGit(arg=[git_code_path, "origin"], token_api_id=token_api_id,
                                       tgt=data.get("git_minion")
                                       )
                code_pull.pull()
                if i == 1:
                    # self.web_socket_api(yaml.dump(status, default_flow_style=False), uid)
                    self.web_socket_api(u"拉取代码完成", uid)

                code_checkout = SaltApiGit(arg=[git_code_path, version], tgt=data.get("git_minion"),
                                           token_api_id=token_api_id)
                code_checkout.checkout()
                if i == 1:
                    self.web_socket_api(u"切分支完分完毕", uid)

                code_push = SaltApiGit(tgt=data.get("git_minion"), arg=[git_code_path, "ops", version, "-f"],
                                       token_api_id=token_api_id
                                       )
                push_status = code_push.push()

                self.web_socket_api(yaml.dump(push_status, default_flow_style=False), uid)

            version_status = SaltApiGit(tgt=data.get("git_minion"), arg=[git_code_path, version],
                                        token_api_id=token_api_id)
            git_master_version = version_status.version()["return"][0][data.get("git_minion")]
            message = "发布版本号: %s" % git_master_version
            self.web_socket_api(message, uid)

            time.sleep(1)
            self.web_socket_api(u"push远程分支完成", uid)
            self.web_socket_api(u"等待10秒........", uid)
            time.sleep(10)
            self.web_socket_api(u"通知需要更新代码的主机开始拉取代码........", uid)
        else:
            self.web_socket_api(u"Error: 发布中止->请选择分支或参数", uid)
            return False

        if arg == "Single":
            for i in host.keys():
                setname = SaltApiGit(
                    tgt=node_list,
                    arg=[code_path, "user.name", "ops", user], token_api_id=token_api_id
                )
                setname.config_set()

                setname = SaltApiGit(
                    tgt=node_list,
                    arg=[code_path, "user.email", "ops@fun.tv", user], token_api_id=token_api_id
                )
                self.web_socket_api(u"开始拉取代码........", uid)
                setname.config_set()
                code_pull = SaltApiGit(
                    tgt=node_list,
                    arg=[code_path, "origin", user], token_api_id=token_api_id
                )
                code_pull.pull()

                node_code_checkout = SaltApiGit(
                    tgt=host[i],
                    arg=[code_path, version, user], token_api_id=token_api_id
                )
                node_code_checkout.checkout()
                self.web_socket_api(u"%s 代码下发完成" % host[i], uid)
                self.web_socket_api(u"判断是否需要检测接口........", uid)
                if CheckUrl:
                    swan_status = True
                    count = 0
                    while count < 6:
                        result = CheckApi(ip=host[i], url=CheckUrl)
                        # result = CheckApi(ip="192.168.111.6", url=CheckUrl)
                        rst, retMsg = result.run()
                        if rst:
                            print u"接口检测正常,开始发布下一台服务器"
                            self.web_socket_api(u"%s 接口检测正常" % host[i], uid)
                            count += 10
                            swan_status = True
                        else:
                            self.web_socket_api(u"%s 接口检测异常,10秒钟后重试-> 接口返回信息:%s" % (host[i], retMsg), uid)
                            time.sleep(10)
                            count += 1
                            swan_status = False

                    if not swan_status:
                        self.web_socket_api(u"%s 接口1分钟检测全部异常,发布中止" % host[i], uid)
                        return False
                else:
                    self.web_socket_api(u"不用检测接口,发布完成........", uid)
                    return True

        else:

            setname = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "user.name", "ops", user], token_api_id=token_api_id
            )
            setname.config_set()

            setname = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "user.email", "ops@fun.tv", user], token_api_id=token_api_id
            )
            setname.config_set()
            self.web_socket_api(u"开始拉取代码........", uid)
            code_pull = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "origin", user], token_api_id=token_api_id
            )
            code_pull.pull()

            node_code_checkout = SaltApiGit(
                tgt=node_list,
                arg=[code_path, version], token_api_id=token_api_id
            )
            print node_code_checkout.checkout()
            self.web_socket_api(u"拉取代码已完成,正在读取版本号......", uid)
            version_status = SaltApiGit(tgt=node_list, arg=code_path, token_api_id=token_api_id)
            rst = version_status.version().get("return")[0]
            self.web_socket_api(u"版本号读取完成......", uid)
            self.web_socket_api(u"开始验证版本号......", uid)

            if agent:
                for i in host.keys():
                    ip = host.get(i, False)
                    host_rst = rst.get(ip, False)
                    if host_rst and host_rst == git_master_version:
                        message = u'%s 版本号: %s 发布成功' % (i, host_rst)
                        self.web_socket_api(message, uid)
                    elif host_rst and host_rst != git_master_version:
                        message = u'%s 版本号: %s 发布失败' % (i, host_rst)
                        self.web_socket_api(message, uid)
                    else:
                        message = u"%s未返回数据" % i
                        self.web_socket_api(message, uid)
            else:
                for i in host.keys():
                    ip = host.get(i, False)
                    host_rst = rst.get(ip, False)
                    message = u'%s 版本号: %s' % (i, host_rst)
                    self.web_socket_api(message, uid)

            self.web_socket_api(u"通知主机更新代完毕", uid)

        if shell and shell_status == 1:
            print "需要先执行脚本 "
            code_checkout = SaltApiGit(arg=shell, tgt=node_list,
                                       token_api_id=token_api_id)
            rst = code_checkout.CmdRun()
            self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
            self.web_socket_api(u"脚本执行完毕", uid)
        return True

    @run_on_executor
    def NodePull(self, data, uid):
        print "无git 中继模式发布"
        user = "user=%s" % data.get("git_code_user")
        host = data.get("host")
        version = data.get("git_version")
        if not version:
            self.web_socket_api(u"发布失败选择分支名称或参数", uid)
            return False
        choose = data.get("choose")

        # 自动化发布普通任务
        token_api_id = token_id()

        # 将主机名放入list 传给salt api接口
        node_list = [host[i] for i in host.keys()]
        code_path = data.get("code_path")
        shell = data.get("shell")
        shell_status = int(data.get("shell_status"))
        if shell and shell_status == 0:
            print "需要先执行脚本 "
            code_checkout = SaltApiGit(arg=shell, tgt=node_list,
                                       token_api_id=token_api_id)
            rst = code_checkout.CmdRun()
            self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
            self.web_socket_api(u"脚本执行完毕", uid)
        # 如未选择版本,默认为master分支
        print "有无版本号"
        print version
        if version:
            node_code_checkout = SaltApiGit(
                tgt=node_list,
                arg=[code_path, version, user], token_api_id=token_api_id
            )
            print node_code_checkout.checkout()
            print user
            code_pull = SaltApiGit(
                tgt=node_list,
                arg=[code_path, user], token_api_id=token_api_id
            )
            code_pull.pull()



        else:
            node_code_checkout = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "master", user], token_api_id=token_api_id
            )
            node_code_checkout.checkout()
            code_pull = SaltApiGit(
                tgt=node_list, arg=[code_path, user], token_api_id=token_api_id,
                user=data.get("git_code_user")
            )
            code_pull.pull()
        version_status = SaltApiGit(tgt=node_list, arg=code_path, token_api_id=token_api_id)
        rst = version_status.version().get("return")[0]

        for i in host.keys():
            ip = host.get(i, False)
            host_rst = rst.get(ip, False)

            message = u'%s 版本号: %s' % (i, host_rst)
            self.web_socket_api(message, uid)

        self.web_socket_api(u"代码更新代完毕", uid)
        if shell and shell_status == 1:
            print "需要先执行脚本 "
            code_checkout = SaltApiGit(arg=shell, tgt=node_list,
                                       token_api_id=token_api_id)
            rst = code_checkout.CmdRun()
            self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
            self.web_socket_api(u"脚本执行完毕", uid)

        return True

    @run_on_executor
    def NodeReset(self, data, uid):
        print "开始发布"
        user = "user=%s" % data.get("git_code_user")
        host = data.get("host")
        version = data.get("git_version")
        reset_code = data.get("reset_code")

        # 自动化发布普通任务
        token_api_id = token_id()

        # 将主机名放入list 传给salt api接口

        node_list = [host[i] for i in host.keys()]
        code_path = data.get("code_path")

        # 如未选择版本,默认为master分支
        if version:
            setname = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "user.name", "ops", user], token_api_id=token_api_id
            )
            setname.config_set()

            setname = SaltApiGit(
                tgt=node_list,
                arg=[code_path, "user.email", "ops@fun.tv", user], token_api_id=token_api_id
            )
            setname.config_set()
            branch_name = "opts='--hard %s'" % reset_code
            node_code_checkout = SaltApiGit(
                tgt=node_list,
                arg=[code_path, version, user], token_api_id=token_api_id
            )
            node_code_checkout.checkout()
            code_pull = SaltApiGit(
                tgt=node_list,
                arg=[code_path, branch_name, user], token_api_id=token_api_id
            )
            print "开始回滚"
            rst = code_pull.reset()
            self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
            self.web_socket_api(u"代码回滚代完毕", uid)

            version_status = SaltApiGit(tgt=node_list, arg=code_path, token_api_id=token_api_id)
            rst = version_status.version().get("return")[0]

            for i in host.keys():
                ip = host.get(i, False)
                host_rst = rst.get(ip, False)

                message = u'%s 版本号: %s' % (i, host_rst)
                self.web_socket_api(message, uid)

            self.web_socket_api(u"代码回滚代完毕", uid)

            return True
        else:
            self.web_socket_api(u"Error 请选择分支或参数名", uid)
            return False

    @run_on_executor
    def TomcatRestart(self, data, uid):
        host = data.get("host")
        choose = int(data.get("choose"))
        if choose == 3:
            # 自动化发布普通任务
            token_api_id = token_id()

            # 将主机名放入list 传给salt api接口

            node_list = [host[i] for i in host.keys()]
            tomcat_init = "%s stop" % data.get("tomcat_init")

            code_checkout = SaltApiGit(arg=tomcat_init, tgt=node_list,
                                       token_api_id=token_api_id)
            code_checkout.CmdRun()

            cache = data.get("cache").split()
            for i in cache:
                i_path = "rm -rf %s" % i
                code_checkout = SaltApiGit(arg=i_path, tgt=node_list,
                                           token_api_id=token_api_id)
                code_checkout.CmdRun()
                message = u"%s 目录清空完毕" % i
                self.web_socket_api(message, uid)

            tomcat_init = "%s restart" % data.get("tomcat_init")

            code_checkout = SaltApiGit(arg=tomcat_init, tgt=node_list,
                                       token_api_id=token_api_id)
            code_checkout.CmdRun()
            # self.web_socket_api(yaml.dump(rst, default_flow_style=False), uid)
            self.web_socket_api(u"tomcat重启完毕", uid)
        else:
            print "is not java"
        return True
