# Документация Django-проекта

### Цель:
Создать Django-проект, который при переходе на страницу /get-current-usd/ будет отображать текущий курс доллара к рублю в формате JSON. Кроме того, проект должен показывать 10 последних запросов на обменный курс. Между последовательными запросами курса должна быть пауза не менее 10 секунд.

### Обзор реализации:

1. Модель: UsdRubExchangeRate
Представляет обменный курс USD на RUB.
```python
from django.db import models

class UsdRubExchangeRate(models.Model):
    usd_rub = models.FloatField()
    request_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usd_rub}'
```
2. Утилиты: utils.py
Содержит функции для получения текущего курса и проверки прошедшего времени.
```python
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


```
3. Сериализатор: serializers.py
```python
from rest_framework import serializers
from .models import UsdRubExchangeRate

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsdRubExchangeRate
        fields = 'usd_rub', 'request_time'
```
Используется для преобразования объектов модели в JSON.
4. Представление: views.py
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_425_TOO_EARLY, HTTP_503_SERVICE_UNAVAILABLE
from .models import UsdRubExchangeRate
from .serializers import ExchangeRateSerializer
from .utils import get_currency_rate, check_time_more_10_sec

class GetCurrentUSD(APIView):
    def create_usd_rub_exchange_rate(self, usd_rub):
        return UsdRubExchangeRate.objects.create(usd_rub=usd_rub)

    def get_last_requests(self):
        return UsdRubExchangeRate.objects.all().order_by('-request_time')[:10]

    def handle_valid_usd_rub(self, usd_rub):
        created_usd_rub = self.create_usd_rub_exchange_rate(usd_rub)
        last_requests = self.get_last_requests()

        serializer = ExchangeRateSerializer(last_requests, many=True)

        return Response(
            {'usd_rub': created_usd_rub.usd_rub, 'request_time': serializer.data}
        )

    def get(self, request):
        last_obj = UsdRubExchangeRate.objects.last()

        if last_obj is None or check_time_more_10_sec(last_obj):
            usd_rub = get_currency_rate()

            if usd_rub is not None:
                return self.handle_valid_usd_rub(usd_rub)
            return Response(
                {'usd_rub': 'API недоступен. Мы не виноваты!!!'},
                status=HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {'error': f'Не прошло 10 секунд'}, status=HTTP_425_TOO_EARLY
        )
```
Обрабатывает запросы, включая проверку времени и взаимодействие с моделью.
5. URL-пути: urls.py
```python
from django.urls import path
from .views import GetCurrentUSD

urlpatterns = [path('get-current-usd/', GetCurrentUSD.as_view(), name='get_current_usd')]

```
Определяет URL-маршруты для представлений.
### Обработка Ошибок:
Код обрабатывает все возможные ошибки и отправляет соответствующие статусы:

- **HTTP_425_TOO_EARLY (Ошибка 425):**
  Возвращается, если не прошло 10 секунд с последнего запроса.

- **HTTP_503_SERVICE_UNAVAILABLE (Ошибка 503):**
  Возвращается, если сервис API для получения курса недоступен.


> **Примечание:** Весь код был написан с соблюдением рекомендаций PEP8 (Style Guide for Python Code) и принципа DRY (Don't Repeat Yourself).
