from django.db import models


class UsdRubExchangeRate(models.Model):
    usd_rub = models.FloatField()
    request_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usd_rub}'
