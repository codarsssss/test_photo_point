from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_425_TOO_EARLY,
                                   HTTP_503_SERVICE_UNAVAILABLE)
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
            {
                'usd_rub': created_usd_rub.usd_rub,
                'request_time': serializer.data
            }
        )

    def get(self, request):
        last_obj = UsdRubExchangeRate.objects.last()

        if last_obj is None or check_time_more_10_sec(last_obj):
            usd_rub = get_currency_rate()

            if usd_rub is not None:
                return self.handle_valid_usd_rub(usd_rub)
            return Response(
                {'usd_rub': 'API недоступен. Мы не виноваты!!!'},
                status=HTTP_503_SERVICE_UNAVAILABLE)
        return Response(
            {'error': f'Не прошло 10 секунд'},
            status=HTTP_425_TOO_EARLY
        )
