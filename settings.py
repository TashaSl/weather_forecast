import os

CALLBACK_API_CONFIRMATION_TOKEN = os.getenv('CALLBACK_API_CONFIRMATION_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
VK_API_ACCESS_TOKEN = os.getenv('VK_API_ACCESS_TOKEN')
OWM_ACCESS_TOKEN = os.getenv('OWM_ACCESS_TOKEN')
WEATHER_UPDATING_THRESHOLD = 60 * 60      # request to get weather is made 1 per 1 hour
DATETIME_STRING_REPRESENTATION = "%d.%m.%Y %H:%M:%S.%f"
DEFAULT_CITY = 'Minsk,BY'
DEFAULT_CITY_REPRESENTATION = 'Минск'
