import http.client
import json
import os
import urllib
import webbrowser

from constant import *
from wox import Wox


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
            return [EMPTY_RESULT]
        response = self.yd_api(q)
        if not response:
            return [{
                'Title': '网络请求失败',
                'SubTitle': '请检查网络连接是否正常',
                'IcoPath': 'Img\\youdao.ico'
            }]
        errCode = response.get('errorCode', '')
        if not errCode:
            return [SERVER_DOWN]

        if errCode != '0':
            return [{
                'Title': ERROR_INFO.get(errCode, '未知错误'),
                'SubTitle': 'errorCode=%s' % errCode,
                'IcoPath': 'Img\\youdao.ico'
            }]

        tSpeakUrl = response.get('tSpeakUrl', '')
        translation = response.get('translation', [])
        basic = response.get('basic', {})
        web = response.get('web', [])
        if translation:
            self.record(q, translation[0])

        if translation:
            result.append({
                'Title': translation[0],
                'SubTitle': '有道翻译',
                'IcoPath': 'Img\\youdao.ico',
                'JsonRPCAction': {
                    'method': 'open_url',
                    'parameters': [q, QUERY_URL]
                }
            })

        if tSpeakUrl:
            result.append({
                'Title': '获取发音',
                'SubTitle': '点击可跳转 - 有道翻译',
                'IcoPath': 'Img\\youdao.ico',
                'JsonRPCAction': {
                    'method': 'open_url',
                    'parameters': [tSpeakUrl]
                }
            })
        if basic:
            for i in basic['explains']:
                result.append({
                    'Title': i,
                    'SubTitle': '{} - 基本词典'.format(response.get('query', '')),
                    'IcoPath': 'Img\\youdao.ico',
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': [q, QUERY_URL]
                    }
                })
        if web:
            for i in web:
                result.append({
                    'Title': ','.join(i['value']),
                    'SubTitle': '{} - 网络释义'.format(i['key']),
                    'IcoPath': 'Img\\youdao.ico',
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': [q, QUERY_URL]
                    }
                })
        return result

    @staticmethod
    def record(query, translation):
        """单词记录
        """
        fileName = 'record.csv'
        if not os.path.exists(fileName):
            with open(fileName, 'w', encoding='utf-8') as f:
                mes = "{}, {}\n".format("query", "translation")
                f.write(mes)

        with open(fileName, 'a+', encoding='utf-8') as f:
            mes = "{}, {}\n".format(query, translation)
            f.write(mes)

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


if __name__ == '__main__':
    Main()
