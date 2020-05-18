import requests
import os
import telegram
import time
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

DVMN_API = "https://dvmn.org/api/"
LONG_POLLING_METHOD = "long_polling/"


class TelegramLogsHandler(logging.Handler):

    def __init__(self, _token, _chat_id, ):
        super().__init__()
        self.chat_id = _chat_id
        self.bot = telegram.Bot(_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=chat_id, text=log_entry)


def get_status(method, timeout, _timestamp, _token):
    url = f"{DVMN_API}{method}"
    header = {"Authorization": f"Token {_token}"}
    payload = {"timestamp": _timestamp}
    response = requests.get(url, timeout=timeout, headers=header, params=payload)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    logging.basicConfig(format="[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(message)s",
                        level=logging.DEBUG,
                        handlers=[RotatingFileHandler('log.log', maxBytes=20000, encoding='utf-8', backupCount=2)])
    load_dotenv()
    token = os.getenv("DVMN_API_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    telegram_token = os.getenv('TELEGRAM_API_TOKEN')
    logger = logging.getLogger("Bot Logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(telegram_token, chat_id))
    logger.info("Notification bot started")
    bot = telegram.Bot(token=telegram_token)
    timestamp = None
    while True:
        try:
            task_status = get_status(LONG_POLLING_METHOD, 100, timestamp, token)
            if task_status['status'] == 'found':
                timestamp = task_status['last_attempt_timestamp']
                lesson_result = task_status['new_attempts'][0]
                work_title = lesson_result['lesson_title']
                solution_is_wrong = lesson_result['is_negative']
                lesson_url = lesson_result['lesson_url']
                module = lesson_url.split('/')[2]
                if solution_is_wrong:
                    step_to_do = 'Please correct errors and send it for checking.\n'
                    link_to_task = f"https://dvmn.org{lesson_url}"
                else:
                    step_to_do = 'The task is solved. You can start a new one.'
                    link_to_task = ""
                bot.send_message(chat_id=chat_id,
                                 text=f'Your work: "{work_title}" from module {module} is verified.'
                                      f'\n{step_to_do} {link_to_task}')
            elif task_status['status'] == 'timeout':
                timestamp = task_status['timestamp_to_request']
        except requests.exceptions.HTTPError as error:
            logger.info("Bot stopped with error:")
            logger.error(error)
            break
        except requests.exceptions.ReadTimeout as error:
            continue
        except requests.exceptions.ConnectionError as error:
            time.sleep(1)
            continue
