import requests
from datetime import datetime, timedelta
import pytz


def get_currency_rate():
    try:
        response = requests.get(
            'https://api.exchangerate-api.com/v4/latest/USD')
        response.raise_for_status()
        usd_rub = response.json()['rates']['RUB']

        return usd_rub
    except requests.exceptions.RequestException as ex:
        print(f'API не доступен с ошибкой {ex}')

        return None


def check_time_more_10_sec(last_obj):
    current_time = datetime.now(pytz.utc)
    time_difference = current_time - last_obj.request_time
    ten_seconds = timedelta(seconds=10)

    return time_difference > ten_seconds

