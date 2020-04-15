from decimal import Decimal, ROUND_HALF_UP
import os
import json


WINDS = [
    (0, 'северный'),
    (45, 'северо-восточный'),
    (90, 'восточный'),
    (135, 'юго-восточный'),
    (180, 'южный'),
    (225, 'юго-западный'),
    (270, 'западный'),
    (315, 'северо-западный')
]


HECTOPASCALS_TO_MERCURY_MILLIMETERS = Decimal(1.333224)


FILE_PATH_OF_WEATHER_DESCRIPTION = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)
    ),
    'translation_weather_status.json'
)


def get_wind_description(wind_degree: int) -> str:
    '''
    Get wind description by wind degree (see `wind rose`)
    :param wind_degree: degree of wind
    :return: wind description
    '''
    assert 0 <= wind_degree < 360, 'Not valid value of given wind degree: expected between 0 and 360.'
    for u in range(1, len(WINDS) - 1):
        if (WINDS[u-1][0] + WINDS[u][0]) / 2 <= wind_degree < (WINDS[u][0] + WINDS[u+1][0]) / 2:
            return WINDS[u][1]
    return WINDS[0][1]


def get_translating_press_value(press_value: int) -> int:
    '''
    Convert atmospheric pressure from hectopascals in mercury millimeters.
    :param press_value: value of atmospheric pressure in hectopascals
    :return: value of atmospheric pressure in mercury millimeters
    '''
    return int((Decimal(press_value) / HECTOPASCALS_TO_MERCURY_MILLIMETERS).quantize(1, rounding=ROUND_HALF_UP))


def get_weather_description_by_code(weather_code: int) -> str:
    '''
    Get weather detail description by given weather code (see available list of weather code in `translation_weather_status.json`)
    :param weather_code: weather code
    :return: weather description
    '''
    with open(FILE_PATH_OF_WEATHER_DESCRIPTION, 'r') as f:
        weather_status = json.load(f)
    suitable_descriptions = list(filter(lambda el: el['id'] == weather_code, weather_status))
    assert len(suitable_descriptions) > 0, 'Not found weather description with given weather_code.'
    assert suitable_descriptions[0].get("ru"), 'Not valid format of weather description for given weather_code.'
    return suitable_descriptions[0]["ru"]
