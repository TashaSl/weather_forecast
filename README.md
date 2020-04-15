# О Задании
[Умный сервис прогноза погоды](https://www.notion.so/03f6716315e04acea3023766e5f2cc0e) (*Базовый уровнь сложности*)

# Проектирование

## Техническая часть
Сервис написан на Python (версия 3.6)

Состоит из двух частей:
1. Flask приложение, принимающее запросы callback API Вконтакте
2. Redis, для хранения кэша запросов к [API прогноза погоды](https://openweathermap.org/api)

Для развертывания используется [Heroku](https://www.heroku.com/) 

## Пользовательский интерфейс 
Кнопочный бот в [ВК](https://vk.com)

Формат ответа
```text
<День> в <город> <температура по цельсию>, <детальное описание погоды>
ветер <скорость ветра в м/с> <направление ветра>,
влажность <процент влажности>,
давление <давление в мм рт. ст.>
```

## Описание работы
1. Получены данные о событии нажатия кнопки
2. Проверяю какая кнопка нажата
3. Если нажата кнопка "Старт" - отправляю пользователю приветственной сообщение
4. Если нажата кнопка "Получить прогноз погоды" - проверяю кэш
5. Если кэш погоды не истек, отправляю пользователю прогноз погоды из кэша
6. Если кэш погоды истек, делаю запрос к [API прогноза погоды](https://openweathermap.org/api), формирую ответ, сохраняю в кэш результаты, и отправляю пользователю
7. Если не удалось сопоставить данные пользователя с данными о кнопках - отправляю пользователю информационное сообщение

## Запуск 
### Запуск Redis-сервера
```bash
$ docker run -p 6379:6379 redis
```
REDIS_URL='redis://0.0.0.0:6379/0'


### Запуск Flask приложения
1. Склонируете репозиторий
```bash
$ git clone https://github.com/TashaSl/weather_forecast.git
$ cd weather_forecast
```
2. Создайте переменные окружения

REDIS_URL='redis://\<your redis server host>:\<your redis server port>/\<dbname to save cache>'

CALLBACK_API_CONFIRMATION_TOKEN='<your confirmation token, see `Настройка ВК` >'

GROUP_ID='<id of your group, see `Настройка ВК`>'

VK_API_ACCESS_TOKEN='<your access key, see `Настройка ВК`>'

OWM_ACCESS_TOKEN='<your access token to [owm](https://openweathermap.org/api), see `Настройка OWM`>'

3. Установите библиотеки и запустите приложение
```bash
$ pip3 install -r requiremets.txt
$ gunicorn flask_app:app
```

### Настройка ВК
1. Создайте сообщество
2. В управлении выберете "Работа с API"
3. Получите ключ доступа (VK_API_ACCESS_TOKEN), 
токен подтверждения связи с Callback API (CALLBACK_API_CONFIRMATION_TOKEN),
ID сообщества (GROUP_ID)
4. Подтвердите адрес callback сервера

### Настройка OWM
1. Ключ доступа достпен по [ссылке](https://home.openweathermap.org/api_keys) 
