from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import BlogPost


def blog_list(request: HttpRequest) -> HttpResponse:
    posts = BlogPost.objects.filter(is_published=True)
    post_type = request.GET.get("type")
    if post_type:
        posts = posts.filter(post_type=post_type)
    paginator = Paginator(posts, 12)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "blog/list.html", {"page_obj": page})


def blog_detail(request: HttpRequest, slug: str) -> HttpResponse:
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, "blog/detail.html", {"post": post})
