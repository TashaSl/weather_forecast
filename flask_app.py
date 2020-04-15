from flask import Flask, globals
import vk
import json
import pyowm
import redis
import datetime
import logging
from utils import get_translating_press_value, get_weather_description_by_code, get_wind_description
from settings import *


app = Flask(__name__)
owm = pyowm.OWM(OWM_ACCESS_TOKEN)
redis_weather_cache = redis.from_url(os.environ.get("REDIS_URL"))
logger = logging.getLogger(__name__)


GET_WEATHER_BUTTON, HOURLY_FORECAST_BUTTON, CHOOSE_DAY_BUTTON = range(3)

BUTTONS = {
    GET_WEATHER_BUTTON: {
        "action": {
            "type": "text",
            "payload": {"button": GET_WEATHER_BUTTON},
            "label": 'Получить прогноз погоды'
        },
        "color": "primary"
    },
    HOURLY_FORECAST_BUTTON: {
        "action": {
            "type": "text",
            "payload": {"button": HOURLY_FORECAST_BUTTON},
            "label": "Почасовой прогноз погоды"
        },
        "color": "primary"
    },
    CHOOSE_DAY_BUTTON: {
        "action": {
            "type": "text",
            "payload": {"button": CHOOSE_DAY_BUTTON},
            "label": "Выбрать другой день"
        },
        "color": "primary"
    }
}


def send_response(user_id, msg_text):
    session = vk.Session()
    api = vk.API(session, v=5.50)
    api.messages.send(
        access_token=VK_API_ACCESS_TOKEN,
        user_id=str(user_id),
        message=msg_text,
        keyboard=json.dumps({
            "one_time": False,
            "buttons": [
                [{
                    'action': {
                        'type': 'text',
                        "payload": "{\"button\": \"1\"}",
                        "label": 'Получить прогноз погоды'
                    },
                    "color": "primary"
                }]
            ]
        })
    )


def check_request_freshness(updated_value: datetime.datetime) -> bool:
    return (datetime.datetime.now() - updated_value).total_seconds() < WEATHER_UPDATING_THRESHOLD


def get_weather_from_cache() -> str:
    # check if redis is available
    if not redis_weather_cache.ping():
        return ''
    last_weather_request = redis_weather_cache.get(DEFAULT_CITY)
    if not last_weather_request:
        return ''
    else:
        last_weather_request = json.loads(last_weather_request)
    if last_weather_request.get('today') or \
            last_weather_request['today'].get('updated') or \
            last_weather_request['today'].get('value'):
        return ''
    updated_value = datetime.datetime.strptime(
        last_weather_request['today']['updated'],
        DATETIME_STRING_REPRESENTATION
    )
    weather_value = last_weather_request['today']['value']
    if check_request_freshness(updated_value):
        return weather_value
    return ''


def save_weather_to_cache(weather_value):
    # check if redis is available
    if not redis_weather_cache.ping():
        return ''
    last_weather_request = redis_weather_cache.get(DEFAULT_CITY)
    if not last_weather_request:
        last_weather_request = {}
    else:
        last_weather_request = json.loads(last_weather_request)
    last_weather_request.update({
        'today': {
            'value': weather_value,
            'updated': datetime.datetime.now().strftime(DATETIME_STRING_REPRESENTATION)
        }
    })
    redis_weather_cache.set(DEFAULT_CITY, json.dumps(last_weather_request))


def get_weather() -> str:
    cache_weather = get_weather_from_cache()
    logging.info('get cache value {0}'.format(cache_weather))
    if cache_weather:
        return cache_weather

    # check if owm is available
    if not owm.is_API_online():
        return 'Извините, сервис временно недоступен'

    observation = owm.weather_at_place(DEFAULT_CITY)
    w = observation.get_weather()
    weather_value = """
    Сейчас в городе {city} {cur_temperature}°C, {weather_description}
    ветер {wind_speed} м/с {wind_description},
    влажность {humidity_value}%,
    давление {press_value} мм рт. ст.""".format(
        city=DEFAULT_CITY,
        cur_temperature=int(w.get_temperature('celsius')['temp']),
        weather_description=get_weather_description_by_code(w.get_weather_code()),
        wind_speed=w.get_wind()['speed'],
        wind_description=get_wind_description(w.get_wind()['deg']),
        humidity_value=w.get_humidity(),
        press_value=get_translating_press_value(w.get_pressure()['press'])
    )
    save_weather_to_cache(weather_value)
    return weather_value


@app.route('/', methods=['POST'])
def hello_world():
    data = globals.request.get_json()
    logging.info('request data: {0}'.format(data))
    assert 'type' in data
    assert str(data.get('group_id', 0)) == GROUP_ID
    if data.get('type') == 'confirmation':
        return CALLBACK_API_CONFIRMATION_TOKEN
    elif data['type'] == 'message_new':
        if data.get('object', {}).get('out') == 1:
            return 'ok'
        if data.get('object', {}).get('body', '').strip() == "Начать":
            send_response(
                user_id=data['object']['user_id'],
                msg_text='Привет! Это умный сервис прогноза погоды. Сделан в рамках задания "Школа будущих СТО" Яндекс.Облака.'
            )
            return 'ok'
        if data.get('object', {}).get('body', '').strip() == "Получить прогноз погоды":
            try:
                msg_text = get_weather()
            except Exception as e:
                logger.error(e)
                msg_text = 'Что-то пошло не так, попробуйте еще раз!'
            send_response(
                user_id=data['object']['user_id'],
                msg_text=msg_text
            )
        return 'ok'


if __name__ == '__main__':
    app.run()
