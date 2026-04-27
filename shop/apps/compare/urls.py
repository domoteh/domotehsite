from django.urls import path

from . import views

app_name = "compare"

urlpatterns = [
    path("", views.compare_list, name="list"),
    path("toggle/<int:product_id>/", views.compare_toggle, name="toggle"),
]
