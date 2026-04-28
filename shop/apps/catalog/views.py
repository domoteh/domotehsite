from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def homepage(request: HttpRequest) -> HttpResponse:
    new_products = Product.objects.filter(is_available=True).order_by("-created_at")[:20]
    bestsellers = Product.objects.filter(is_available=True, is_bestseller=True)[:20]
    popular = Product.objects.filter(is_available=True).order_by("-updated_at")[:20]

    top_categories = Category.objects.filter(level=0, is_active=True)
    category_sections = []
    for cat in top_categories:
        products = Product.objects.filter(
            category__in=cat.get_descendants(include_self=True),
            is_available=True,
        ).order_by("-created_at")[:5]
        if products:
            category_sections.append({"category": cat, "products": products})

    return render(request, "catalog/home.html", {
        "new_products": new_products,
        "bestsellers": bestsellers,
        "popular": popular,
        "category_sections": category_sections,
    })


def category_detail(request: HttpRequest, slug: str) -> HttpResponse:
    category = get_object_or_404(Category, slug=slug, is_active=True)
    descendants = category.get_descendants(include_self=True)
    products = Product.objects.filter(category__in=descendants, is_available=True)

    sort = request.GET.get("sort", "-created_at")
    allowed_sorts = {
        "price_asc": "retail_price",
        "price_desc": "-retail_price",
        "name": "name",
        "new": "-created_at",
    }
    products = products.order_by(allowed_sorts.get(sort, "-created_at"))

    brand = request.GET.get("brand")
    if brand:
        products = products.filter(brand=brand)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        products = products.filter(retail_price__gte=min_price)
    if max_price:
        products = products.filter(retail_price__lte=max_price)

    paginator = Paginator(products, 24)
    page = paginator.get_page(request.GET.get("page"))

    brands = (
        Product.objects.filter(category__in=descendants, is_available=True)
        .exclude(brand="")
        .values_list("brand", flat=True)
        .distinct()
        .order_by("brand")
    )

    template = "catalog/partials/product_grid.html" if request.htmx else "catalog/category.html"
    return render(request, template, {
        "category": category,
        "page_obj": page,
        "brands": brands,
        "current_sort": sort,
        "current_brand": brand or "",
    })


def product_detail(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related(
            "images", "params", "wholesale_prices", "reviews"
        ),
        slug=slug,
    )
    is_wholesale = getattr(request.user, "is_wholesale", False)
    wholesale = product.get_wholesale_price()

    related = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(pk=product.pk)[:15]

    return render(request, "catalog/product.html", {
        "product": product,
        "wholesale": wholesale,
        "is_wholesale": is_wholesale,
        "related_products": related,
    })


def search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    products = Product.objects.none()
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(sku__icontains=query) | Q(brand__icontains=query),
            is_available=True,
        )
    paginator = Paginator(products, 24)
    page = paginator.get_page(request.GET.get("page"))

    template = "catalog/partials/product_grid.html" if request.htmx else "catalog/search.html"
    return render(request, template, {"page_obj": page, "query": query})
