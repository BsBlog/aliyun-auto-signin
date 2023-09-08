"""
    @Author: thsrite
    @Date: 2023/3/31
    @Description: 
"""
import json
import logging

import requests
from configobj import ConfigObj


class Pusher:

    def __init__(self, corpid: str, corpsecret: str, agentid: str, touser: str, proxyurl: str):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.touser = touser
        self.proxyurl = proxyurl

    def send(
            self,
            title: str,
            content: str
    ) -> dict:
        """
        发送消息

        :param title: 通知标题
        :param content: 消息内容
        :return:
        """
        qy_url = self.proxyurl or "https://qyapi.weixin.qq.com"
        get_token_url = f"{qy_url}/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
        request = requests.get(get_token_url)

        request.raise_for_status()

        # access_token
        ret_json = request.json()
        if ret_json['errcode'] != 0:
            raise Exception(f'[{ret_json["errcode"]}] {ret_json.text}')
        access_token = ret_json.get('access_token')

        # 发送图文消息
        send_msg_url = f'{qy_url}/cgi-bin/message/send?access_token={access_token}'
        data = {
            "touser": self.touser or "@all",
            "agentid": self.agentid,
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": content,
                        "picurl": "https://raw.githubusercontent.com/thsrite/aliyundrive-checkin/main/aliyunpan.jpg",
                        "url": ''
                    }
                ]
            },
            "duplicate_check_interval": 600
        }
        request = requests.post(send_msg_url, data=json.dumps(data))

        request.raise_for_status()

        return request.json()


def push(
        config: ConfigObj | dict,
        content: str,
        content_html: str,
        title: str,
) -> bool:
    """
    签到消息推送

    :param config: 配置文件, ConfigObj 对象 | dict
    :param content: 推送内容
    :param content_html: 推送内容, HTML 格式
    :param title: 标题
    :return:
    """
    if not config['wechat_corpid'] or not config['wechat_corpsecret'] \
            or not config['wechat_agentid']:
        logging.error('Wechat应用 推送参数配置不完整')
        return False

    try:
        pusher = Pusher(config['wechat_corpid'], config['wechat_corpsecret'], config['wechat_agentid'],
                        config['wechat_touser'], config['wechat_proxyurl'])
        pusher.send(title, content)
        logging.info('Wechat应用 推送成功')
    except Exception as e:
        logging.error(f'Wechat应用 推送失败, 错误信息: {e}')
        return False

    return True
