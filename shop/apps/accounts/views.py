from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.cart.services import merge_cart_on_login

from .forms import UserRegistrationForm


def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            merge_cart_on_login(request)
            return redirect("catalog:home")
    else:
        form = UserRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    return render(request, "accounts/profile.html")
