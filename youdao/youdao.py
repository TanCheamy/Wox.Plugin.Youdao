# -*- coding: utf-8 -*-

import copy
import http.client
import json
import os
import time
import urllib
import webbrowser

import pyperclip
from win32com.client import Dispatch

from wox import Wox

from .constants import *


class Main(Wox):

    def query(self, param):
        """依次处理 Wox 队列信息

        Arguments:
            param {string} -- 命令

        Returns:
            list -- 消息列表
        """

        result = []
        q = param.strip()
        if not q:
            tit = 'Start to translate between Chinese and English'
            subtit = 'Powered by youdao api, Python3.x only.'
            return [self.genformat(tit, subtit)]

        response = self.yd_api(q)
        if not response:
            tit = '网络请求失败'
            subtit = '请检查网络连接是否正常'
            return [self.genformat(tit, subtit)]

        errCode = response.get('errorCode', '')
        if not errCode:
            tit = '网易在线翻译服务暂不可用'
            subtit = '请待服务恢复后再试'
            return [self.genformat(tit, subtit)]

        if errCode != '0':
            tit = ERROR_INFO.get(errCode, '未知错误')
            subtit = 'errorCode=%s' % errCode
            return [self.genformat(tit, subtit)]

        translation = response.get('translation', [])
        basic = response.get('basic', {})
        web = response.get('web', [])

        if translation:
            tit = translation[0]
            subtit = '点击复制到剪贴板并收藏'
            method = 'copy2clipboard'
            parameters = [q, translation[0]]
            res = self.genaction(tit, subtit, method, parameters)
            result.append(res)

        if translation:
            tit = q
            subtit = '点击发音'
            method = 'speak'
            parameters = [q]
            result.append(self.genaction(tit, subtit, method, parameters))

        if basic:
            for i in basic['explains']:
                subtit = '{} - 基本词典'.format(response.get('query', ''))
                method = 'open_url'
                parameters = [q, QUERY_URL]
                result.append(self.genaction(i, subtit, method, parameters))
        if web:
            method = 'open_url'
            for i in web:
                tit = translation[0]
                subtit = '{} - 网络释义'.format(i['key'])
                parameters = [q, QUERY_URL]
                result.append(self.genaction(tit, subtit, method, parameters))
        return result

    @staticmethod
    def genformat(tit, subtit):
        res = copy.deepcopy(TEMPLATE)
        res['Title'] = tit
        res['SubTitle'] = subtit

        return res

    @staticmethod
    def genaction(tit, subtit, method, actparam):
        res = copy.deepcopy(TEMPLATE)
        res['Title'] = tit
        res['SubTitle'] = subtit

        action = copy.deepcopy(ACTION_TEMPLATE)
        action['JsonRPCAction']['method'] = method
        action['JsonRPCAction']['parameters'] = actparam
        res.update(action)

        return res

    def copy2clipboard(self, query, translation):
        """复制到剪切板

        Arguments:
            value -- 复制内容
        """
        self.record(query, translation)  # 记录
        pyperclip.copy(str(translation).strip())

    def speak(self, source):
        """发音

        :param query: source
        :return:
        """
        spVoice = Dispatch("SAPI.SpVoice")
        spVoice.Speak(source)

    @staticmethod
    def record(query, translation):
        """单词记录
        """
        fileName = os.path.join(PATH, '单词收藏.csv')
        message = "{}, {}, {}\n"
        with open(fileName, 'a+', encoding='utf-8') as f:
            if os.path.exists(fileName):
                date = time.strftime("%Y-%m-%d", time.localtime())
                message = message.format(query, translation, date)
            else:
                message = message.format("query", "translation", "date")
            f.write(message)

    def open_url(self, query, url=None):
        """查询关键词

        Arguments:
            query {string} -- 关键词

        Keyword Arguments:
            url {string} -- 查询链接 (default: {None})
        """

        if url:
            webbrowser.open(url + query)
        else:
            webbrowser.open(query)

    @staticmethod
    def yd_api(q):
        """youdao api

        Arguments:
            q {string} -- 查询词

        Returns:
            string -- 查询结果
        """

        payload = "q={}&from=Auto&to=Auto".format(urllib.parse.quote(q))
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Cache-Control': "no-cache"
        }
        try:
            conn = http.client.HTTPSConnection("aidemo.youdao.com")
            conn.request("POST", "/trans", payload, headers)
            res = conn.getresponse()
        except Exception:
            pass
        else:
            if res.code == 200:
                return json.loads(res.read().decode("utf-8"))
        finally:
            if conn:
                conn.close()

    def _get_proxies(self):
        """代理设置

        Returns:
            dict -- 返回包含代理信息的头文件
        """

        proxies = {}
        if self.proxy and self.proxy.get("enabled") and self.proxy.get("server"):
            proxies["http"] = "http://{}:{}".format(
                self.proxy.get("server"), self.proxy.get("port"))
            proxies["https"] = "http://{}:{}".format(
                self.proxy.get("server"), self.proxy.get("port"))
        return proxies
