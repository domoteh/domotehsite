from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import NewsletterSubscriber, StaticPage


def static_page(request: HttpRequest, slug: str) -> HttpResponse:
    page = get_object_or_404(StaticPage, slug=slug, is_active=True)
    return render(request, "pages/detail.html", {"page": page})


@require_POST
def newsletter_subscribe(request: HttpRequest) -> HttpResponse:
    email = request.POST.get("email", "").strip()
    if email:
        NewsletterSubscriber.objects.get_or_create(email=email)
    return render(request, "pages/partials/subscribe_success.html")
