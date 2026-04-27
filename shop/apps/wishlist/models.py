from django.conf import settings
from django.db import models

from apps.catalog.models import Product


class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Закладка"
        verbose_name_plural = "Закладки"
        unique_together = [("user", "product")]

    def __str__(self) -> str:
        return f"{self.user} — {self.product.name}"
