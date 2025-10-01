import json
import redis
import requests

from datetime import datetime
from app.config import settings

# Lua scrips
send_message = ("local data = {"
                "from_user = ARGV[1],"
                "to_user = ARGV[2],"
                "date = ARGV[3],"
                "message = ARGV[4]"
                "}"
                "redis.call('RPUSH', KEYS[1], cjson.encode(data))"
                "return 'ok'"
                )

get_dialog = ("local dialog = KEYS[1]"
              "local result = redis.call('LRANGE', dialog, 0, -1)"
              "return result")

search_dialogs = ("local dialog_one = KEYS[1]"
                  "local dialog_two = KEYS[2]"
                  "local db = ARGV[1]"
                  "local status, _ = redis.call('SELECT', db)"
                  "if status.ok == 'OK' then "
                  "local value_one = redis.call('KEYS', dialog_one)"
                  "local value_two = redis.call('KEYS', dialog_two)"
                  "for _, value in ipairs(value_two) do "
                  "table.insert(value_one, value)"
                  "end return value_one "
                  "else return 'Error selecting database' end")


def redis_connect():
    r_connect = redis.Redis(host=settings.REDIS_DIALOG_HOST,
                            port=settings.REDIS_DIALOG_PORT,
                            db=settings.REDIS_DIALOG_DB,
                            password=settings.REDIS_DIALOG_PASSWORD
                            )
    try:
        r_connect.ping()
    except BaseException as error:
        print(f"Error {error}", flush=True)

    return r_connect


def find_sort_id(from_user: int, to_user: int) -> tuple:
    return from_user if from_user < to_user else to_user, to_user if to_user > from_user else from_user


def redis_db_send_message_from_to(from_user: int, to_user: int, message: str) -> str:
    r = redis_connect()
    first, last = find_sort_id(from_user, to_user)

    operation = r.register_script(send_message)

    result = operation(keys=[f"dialog:{first}:{last}"], args=[from_user,
                                                              to_user,
                                                              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                              message]).decode("utf-8")

    if result:
        url = f"http://{settings.DIALOG_UNREAD_ADD}/{from_user}/{to_user}"
        try:
            response = requests.post(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")


def redis_search_user_dialog(id_user: int) -> list:
    r = redis_connect()

    operation = r.register_script(search_dialogs)
    res = operation(keys=[f"dialog:*:{id_user}", f"dialog:{id_user}:*"], args=[str(1)])

    return [i.decode("utf-8") for i in res]


def redis_db_get_user_messages(from_user: int, to_user: int) -> list:
    r = redis_connect()
    first, last = find_sort_id(from_user, to_user)

    operation = r.register_script(get_dialog)
    dialog = operation(keys=[f"dialog:{first}:{last}"])

    return [json.loads(i.decode("utf-8")) for i in dialog]
