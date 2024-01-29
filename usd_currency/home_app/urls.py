from django.urls import path
from .views import GetCurrentUSD


urlpatterns = [
    path('get-current-usd/', GetCurrentUSD.as_view(), name='get_current_usd'),
]
