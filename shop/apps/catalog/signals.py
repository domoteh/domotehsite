from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Category

_CACHE_KEY = "nav_menu_categories"


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_nav_cache(sender, **kwargs) -> None:
    cache.delete(_CACHE_KEY)
