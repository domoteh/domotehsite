from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("monobank/callback/", views.monobank_callback, name="monobank_callback"),
    path("monobank/status/<int:order_pk>/", views.payment_status, name="payment_status"),
]
