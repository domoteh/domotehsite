from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("liqpay/callback/", views.liqpay_callback, name="liqpay_callback"),
    path("monobank/callback/", views.monobank_callback, name="monobank_callback"),
]
