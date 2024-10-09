#!/usr/bin/env python
import os
import json
import vk_api
from vk_api.utils import get_random_id
from work_with_streaming import get_server_url, Streaming


def main(arr_rul):
    try:
        access_tok = os.environ.get("ACCESS_TOKEN")
        com_key = os.environ.get("COMMUNITY_KEY")
        user_id = os.environ.get("USER_ID")
        resp_key = get_server_url(access_tok)
        if resp_key.get("key"):
            vk_session = vk_api.VkApi(token=com_key)
            vk = vk_session.get_api()
            api = Streaming(resp_key["endpoint"], resp_key["key"])
            api.update_rules(arr_rul)
            try:

                @api.stream
                def my_func(event):
                    id_author_finding = event["author"]["id"]
                    type_finding = event["event_type"]
                    url_finding = event["event_url"]
                    text_finding = event["text"]
                    src = f"[{id_author_finding}]:[{type_finding}]:{url_finding} {text_finding}"
                    msg = src[:4095]
                    vk.messages.send(
                        user_id=int(user_id), message=msg, random_id=get_random_id()
                    )

                api.start()
            except Exception as e:
                api.stop()
                print(f"ошибка при стримминге - {e}")
    except Exception as e:
        print(f"ошибка при получении ключа - {e}")


if __name__ == "__main__":
    while True:
        try:
            print("Started scrypt ...")
            with open('words.json', 'r') as file:
                data = json.load(file)
            main(arr_rul=data)
        except Exception as e:
            print(f"ошибка при запуске скрипта - {e}")
