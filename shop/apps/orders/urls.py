from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("<int:pk>/", views.order_detail, name="detail"),
    path("<int:pk>/success/", views.order_success, name="success"),
    path("history/", views.order_history, name="history"),
]
