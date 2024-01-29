from rest_framework import serializers

from .models import UsdRubExchangeRate


class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsdRubExchangeRate
        fields = 'usd_rub', 'request_time'
