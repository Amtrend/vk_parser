import os
import json
import requests
from websocket import WebSocketApp


def get_server_url(access_token):
    ver = os.environ.get("API_VER")
    url = f"https://api.vk.com/method/streaming.getServerUrl?v={ver}&access_token={access_token}"
    response = requests.get(url).json()
    if "error" in response:
        raise VkError(response["error"]["error_code"], response["error"]["error_msg"])
    return response["response"]


class Streaming(object):
    def __init__(self, endpoint, key):
        self.endpoint = endpoint
        self.key = key
        self.list_func = []
        self.ws = None

    def get_rules(self):
        url = f"https://{self.endpoint}/rules?key={self.key}"
        response = requests.get(url).json()
        if response["code"] != 200:
            raise VkError(response["error"]["error_code"], response["error"]["message"])
        else:
            return response["rules"]

    def add_rules(self, tag, value):
        url = f"https://{self.endpoint}/rules?key={self.key}"
        values = {"rule": {"value": value, "tag": tag}}
        response = requests.post(url, json=values).json()
        if response["code"] != 200:
            raise VkError(response["error"]["error_code"], response["error"]["message"])

    def del_rules(self, tag):
        url = f"https://{self.endpoint}/rules?key={self.key}"
        values = {"tag": tag}
        response = requests.delete(url, json=values).json()
        if response["code"] != 200:
            raise VkError(response["error"]["error_code"], response["error"]["message"])

    def del_all_rules(self):
        rules = self.get_rules()
        if rules:
            for item in rules:
                self.del_rules(item["tag"])

    def update_rules(self, array):
        max_rules = os.environ.get("MAX_RULES")
        if len(array) > int(max_rules):
            raise VkError(2006, "Too many rules")
        else:
            self.del_all_rules()
            for item in array:
                self.add_rules(item["tag"], item["value"])

    def stream(self, func):
        self.list_func.append(func)

    def start(self):
        er = False

        def on_message(ws, message):
            message = json.loads(message)
            if message["code"] == 100:
                for func in self.list_func:
                    func(message["event"])
            else:
                ws.close()
                self.start()

        def on_error(ws, error):
            er = True

        def on_close(ws):
            pass

        url = f"://{self.endpoint}/stream?key={self.key}"
        self.ws = WebSocketApp(
            "wss" + url, on_message=on_message, on_error=on_error, on_close=on_close
        )
        self.ws.run_forever()
        if er:
            headers = {
                "Connection": "upgrade",
                "Upgrade": "websocket",
                "Sec-Websocket-Version": "13",
            }
            response = requests.get("https" + url, headers=headers).json()
            if response["code"] == 400:
                raise VkError(
                    response["error"]["error_code"], response["error"]["message"]
                )
            else:
                self.start()

    def stop(self):
        self.ws.close()


class VkError(Exception):
    def __init__(self, error_code, message):
        self.message = message
        self.error_code = error_code

    def __str__(self):
        return f"{self.error_code}: {self.message}"
