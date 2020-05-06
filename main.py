import requests
import os
import time
import telegram
from dotenv import load_dotenv
import logging

DVMN_API = "https://dvmn.org/api/"
METHOD_LONG = "long_polling/"


def get_status(method, timeout, _timestamp, _token):
    url = "".join([DVMN_API, method])
    header = {"Authorization": " ".join(["Token", _token])}
    payload = {"timestamp": _timestamp}
    try:
        response = requests.get(url, timeout=timeout, headers=header, params=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as _error:
        raise requests.exceptions.HTTPError(f"Program had to stop. Not possible to get status: f{_error}")
    return response.json()


if __name__ == "__main__":
    logging.basicConfig(format="[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(message)s",
                        level=logging.DEBUG,
                        handlers=[logging.FileHandler('log.log', 'w', 'utf-8')])
    load_dotenv()
    token = os.getenv("TOKEN")
    chat_id = os.getenv("CHAT_ID")
    bot = telegram.Bot(token=os.getenv('T_API_TOKEN'))
    timestamp = None
    while True:
        try:
            task_status = get_status(METHOD_LONG, 100, timestamp, token)
            if task_status['status'] == 'found':
                timestamp = task_status['last_attempt_timestamp']
                work_title = task_status['new_attempts'][0]['lesson_title']
                solution_is_wrong = task_status['new_attempts'][0]['is_negative']
                lesson_url = task_status['new_attempts'][0]['lesson_url']
                module = lesson_url.split('/')[2]
                if solution_is_wrong:
                    step_to_do = 'Please correct errors and send it for checking.\n'
                    link_to_task = "".join(['https://dvmn.org', lesson_url])
                else:
                    step_to_do = 'The task is solved. You can start a new one.'
                    link_to_task = ""
                bot.send_message(chat_id=chat_id,
                                 text=f'Your work: "{work_title}" from module {module} is verified.'
                                      f'\n{step_to_do} {link_to_task}')
            elif task_status['status'] == 'timeout':
                timestamp = task_status['timestamp_to_request']
        except requests.exceptions.HTTPError as error:
            logging.error(error)
            break
        except requests.exceptions.ReadTimeout as error:
            logging.error(error)
            continue
        except requests.exceptions.ConnectionError as error:
            logging.error(error)
            time.sleep(120)
            continue
