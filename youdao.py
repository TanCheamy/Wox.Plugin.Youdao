import http.client
import json
import urllib
import webbrowser

from wox import Wox

QUERY_URL = 'http://dict.youdao.com/search?q='
EMPTY_RESULT = {
    'Title': 'Start to translate between Chinese and English',
    'SubTitle': 'Powered by youdao api, Python3.x only.',
    'IcoPath': 'Img\\youdao.ico'
}
SERVER_DOWN = {
    'Title': '网易在线翻译服务暂不可用',
    'SubTitle': '请待服务恢复后再试',
    'IcoPath': 'Img\\youdao.ico'
}
ERROR_INFO = {
    "101": "缺少必填的参数，出现这个情况还可能是et的值和实际加密方式不对应",
    "102": "不支持的语言类型",
    "103": "翻译文本过长",
    "104": "不支持的API类型",
    "105": "不支持的签名类型",
    "106": "不支持的响应类型",
    "107": "不支持的传输加密类型",
    "108": "appKey无效，注册账号，登录后台创建应用和实例并完成绑定，可获得应用ID和密钥等信息，其中应用ID就是appKey（注意不是应用密钥）",
    "109": "batchLog格式不正确",
    "110": "无相关服务的有效实例",
    "111": "开发者账号无效",
    "113": "q不能为空",
    "201": "解密失败，可能为DES,BASE64,URLDecode的错误",
    "202": "签名检验失败",
    "203": "访问IP地址不在可访问IP列表",
    "205": "请求的接口与选择的接入方式不一致",
    "301": "辞典查询失败",
    "302": "翻译查询失败",
    "303": "服务端的其它异常",
    "401": "账户已经欠费",
    "411": "访问频率受限,请稍后访问",
    "2005": "ext参数不对",
    "2006": "不支持的voice",
}


class Main(Wox):

    def query(self, param):
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

    def open_url(self, query, url=None):
        if url:
            webbrowser.open(url + query)
        else:
            webbrowser.open(query)

    @staticmethod
    def yd_api(q):
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
            if res.code == 200:
                return json.loads(res.read().decode("utf-8"))
        except Exception:
            pass
        finally:
            if conn:
                conn.close()

    def __get_proxies(self):
        proxies = {}
        if self.proxy and self.proxy.get("enabled") and self.proxy.get("server"):
            proxies["http"] = "http://{}:{}".format(
                self.proxy.get("server"), self.proxy.get("port"))
            proxies["https"] = "http://{}:{}".format(
                self.proxy.get("server"), self.proxy.get("port"))
        return proxies


if __name__ == '__main__':
    Main()
