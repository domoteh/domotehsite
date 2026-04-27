from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.catalog.urls")),
    path("cart/", include("apps.cart.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("orders/", include("apps.orders.urls")),
    path("payments/", include("apps.payments.urls")),
    path("wishlist/", include("apps.wishlist.urls")),
    path("compare/", include("apps.compare.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("blog/", include("apps.blog.urls")),
    path("pages/", include("apps.pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
