from django.core.cache import cache
from django.db.models import Prefetch

from .models import Category

_CACHE_KEY = "nav_menu_categories"
_CACHE_TTL = 60 * 5  # 5 minutes


def categories_menu(request) -> dict:
    qs = cache.get(_CACHE_KEY)
    if qs is None:
        qs = list(
            Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related(
                Prefetch(
                    "children",
                    queryset=Category.objects.filter(is_active=True),
                ),
                Prefetch(
                    "children__children",
                    queryset=Category.objects.filter(is_active=True),
                ),
            )
        )
        cache.set(_CACHE_KEY, qs, _CACHE_TTL)
    return {"menu_categories": qs}
