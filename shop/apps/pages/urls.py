from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("subscribe/", views.newsletter_subscribe, name="subscribe"),
    path("<slug:slug>/", views.static_page, name="detail"),
]
