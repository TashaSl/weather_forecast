from flask import Flask, globals
import vk
import json
import pyowm
from utils import get_translating_press_value, get_weather_description_by_code, get_wind_description
from settings import *


app = Flask(__name__)
owm = pyowm.OWM(OWM_ACCESS_TOKEN)
# owm.is_API_online()


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


def get_weather():
    observation = owm.weather_at_place('Minsk,BY')
    w = observation.get_weather()
    return 'Сейчас в Минске {cur_temperature}°C, '\
           '{weather_description}, '\
           'ветер {wind_speed} м/с {wind_description}, '\
           'влажность {humidity_value}%, '\
           'давление {press_value} мм рт. ст.'.format(
                cur_temperature=int(w.get_temperature('celsius')['temp']),
                weather_description=get_weather_description_by_code(w.get_weather_code()),
                wind_speed=w.get_wind()['speed'],
                wind_description=get_wind_description(w.get_wind()['deg']),
                humidity_value=w.get_humidity(),
                press_value=get_translating_press_value(w.get_pressure()['press'])
           )


@app.route('/', methods=['POST'])
def hello_world():
    data = globals.request.get_json()
    print(data)
    assert 'type' in data
    assert str(data.get('group_id', 0)) == GROUP_ID
    if data.get('type') == 'confirmation':
        return CALLBACK_API_CONFIRMATION_TOKEN
    elif data['type'] == 'message_new':
        if data.get('object', {}).get('out') == 1:
            print('this is my msg')
            return 'ok'
        if data.get('object', {}).get('body', '').strip() == "Начать":
            send_response(
                user_id=data['object']['user_id'],
                msg_text='Привет! Это умный сервис прогноза погоды. Сделан в рамках задания "Школа будущих СТО" Яндекс.Облака.'
            )
            return 'ok'
        if data.get('object', {}).get('body', '').strip() == "Получить прогноз погоды":
            send_response(
                user_id=data['object']['user_id'],
                msg_text=get_weather()
            )
        return 'ok'


if __name__ == '__main__':
    app.run()
