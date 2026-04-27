from django.urls import path

from . import views

app_name = "wishlist"

urlpatterns = [
    path("", views.wishlist_list, name="list"),
    path("toggle/<int:product_id>/", views.wishlist_toggle, name="toggle"),
]
