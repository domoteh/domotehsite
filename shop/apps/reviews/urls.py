from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("product/<int:product_id>/add/", views.add_review, name="add_review"),
    path("product/<int:product_id>/question/", views.add_question, name="add_question"),
]
